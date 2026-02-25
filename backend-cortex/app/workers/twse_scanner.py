"""
TWSE Scanner Worker (全台股戰略掃描)
Adapted from TrendSniper V24 for LifeOS v3.5 integration

Purpose: Automatically scan Taiwan Stock Exchange for trend reversal signals
Schedule: Daily at 14:30 (after market close)
Output: Stores summarized insights in memories table with category="market_intel"
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import time
import logging
from typing import List, Dict, Optional
from app.core.database import supabase
from app.core.gemini import get_model
import google.generativeai as genai

logger = logging.getLogger("cortex.twse_scanner")


class ScannerConfig:
    """System Constitution (憲章參數)"""
    # Technical Parameters
    MA_LONG = 90  # Trend line
    MA_SHORT = 20  # Support line
    
    # Thresholds (Data-optimized)
    TH_TREND_GAP = 1.01  # MA spread must > 1% (ensure bullish)
    TH_KISS_DIST = 0.02  # Price distance to MA20 must < 2% (ensure pullback)
    TH_VWAP_DEV_MAX = 0.15  # Deviation from quarterly cost cannot exceed 15% (prevent chasing highs)
    TH_VOL_COMPRESS = 0.5  # Volatility compression coefficient
    
    # Filters
    MIN_PRICE = 10  # Filter penny stocks
    MIN_VOL_AMT = 50_000_000  # 50M TWD daily volume (prevent liquidity drought)


class TWSEScanner:
    def __init__(self):
        self.report: List[Dict] = []
        
    def get_tw_stock_list(self) -> pd.DataFrame:
        """Fetch Taiwan stock list (TWSE + OTC)"""
        logger.info("[OK] Fetching stock list from TWSE...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Mode=2: TWSE, Mode=4: OTC
        market_types = [(2, '.TW', 'TWSE'), (4, '.TWO', 'OTC')]
        all_dfs = []
        
        for mode, suffix, market_name in market_types:
            url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}"
            try:
                r = requests.get(url, verify=False, headers=headers, timeout=10)
                df = pd.read_html(r.text)[0]
                df.columns = df.iloc[0]
                df = df.iloc[2:]
                
                # Filter 4-digit codes (exclude warrants)
                df['code'] = df['有價證券代號及名稱'].apply(lambda x: x.split()[0])
                df = df[df['code'].apply(lambda x: len(x) == 4)]
                
                df['name'] = df['有價證券代號及名稱'].apply(lambda x: x.split()[-1])
                df['suffix'] = suffix
                
                all_dfs.append(df[['code', 'name', 'suffix', '產業別']].copy())
                logger.info(f"[OK] {market_name} list fetched")
            except Exception as e:
                logger.error(f"[ERROR] Failed to fetch {market_name} list: {e}")
        
        if all_dfs:
            df_all = pd.concat(all_dfs, ignore_index=True)
            logger.info(f"[OK] Total {len(df_all)} stocks fetched")
            return df_all
        return pd.DataFrame()
    
    def fetch_stock_data(self, ticker_full: str) -> tuple:
        """Fetch OHLCV + fundamental snapshot"""
        try:
            stock = yf.Ticker(ticker_full)
            df = stock.history(period="1y")
            if df.empty:
                return None, None
            return df, stock.info
        except Exception:
            return None, None
    
    def analyze_stock(self, ticker: str, name: str, suffix: str) -> Optional[Dict]:
        """Core analysis logic (4 Survival Factors)"""
        ticker_full = f"{ticker}{suffix}"
        df, info = self.fetch_stock_data(ticker_full)
        
        if df is None or len(df) < 100:
            return None
        
        # 1. Data cleaning
        close = df['Close']
        vol = df['Volume']
        
        if close.empty or vol.empty:
            return None
        
        last_close = close.iloc[-1]
        last_vol = vol.iloc[-1]
        
        # Liquidity & price filters
        if (last_close < ScannerConfig.MIN_PRICE) or (last_close * last_vol < ScannerConfig.MIN_VOL_AMT):
            return None
        
        # 2. Feature engineering
        ma20 = close.ewm(span=ScannerConfig.MA_SHORT, adjust=False).mean()
        ma90 = close.ewm(span=ScannerConfig.MA_LONG, adjust=False).mean()
        
        # [F3] Trend core: MA spread
        if ma90.iloc[-1] == 0:
            return None
        f3_gap = ma20.iloc[-1] / ma90.iloc[-1]
        
        # [F6] Pullback core: Kiss distance
        if ma20.iloc[-1] == 0:
            return None
        dist_ma20 = (last_close - ma20.iloc[-1]) / ma20.iloc[-1]
        f6_kiss = abs(dist_ma20)
        
        # [F10] Position core: Q-VWAP deviation
        vol_ma = df['Volume'].rolling(60).sum().replace(0, 1)
        vwap_est = (df['Volume'] * df['Close']).rolling(60).sum() / vol_ma
        
        if pd.isna(vwap_est.iloc[-1]) or vwap_est.iloc[-1] == 0:
            return None
        f10_dev = (last_close - vwap_est.iloc[-1]) / vwap_est.iloc[-1]
        
        # [F11] Momentum core: Volatility compression
        high_5 = df['High'].rolling(5).max()
        low_5 = df['Low'].rolling(5).min()
        
        if low_5.iloc[-1] == 0:
            return None
        f11_vol = (high_5.iloc[-1] - low_5.iloc[-1]) / low_5.iloc[-1]
        
        # 3. Constitution check
        # A. Revenue growth filter
        rev_growth = 0
        if info:
            rev_growth = info.get('revenueGrowth', 0) or 0
            if rev_growth < 0:
                return None
        
        # B. Trend inertia filter
        if f3_gap < ScannerConfig.TH_TREND_GAP:
            return None
        
        # C. Entry trigger filter
        is_trend_up = (ma20.iloc[-1] > ma90.iloc[-1]) and (ma90.iloc[-1] > ma90.iloc[-5])
        is_pullback = f6_kiss < ScannerConfig.TH_KISS_DIST
        is_not_hot = f10_dev < ScannerConfig.TH_VWAP_DEV_MAX
        
        # 4. Signal output
        if is_trend_up and is_pullback and is_not_hot:
            risk_price = ma90.iloc[-1]
            return {
                "code": ticker,
                "name": name,
                "signal": "Pullback Lock",
                "price": round(last_close, 2),
                "ma20_dist_pct": round(dist_ma20 * 100, 2),
                "f3_strength": round(f3_gap, 2),
                "f11_compression": round(f11_vol * 100, 2),
                "rev_growth": f"{rev_growth:.1%}" if rev_growth else "N/A",
                "stop_loss": round(risk_price, 2)
            }
        return None
    
    async def semantic_compress(self, signals: List[Dict]) -> str:
        """Use Gemini to compress signals into narrative summary"""
        if not signals:
            return "今日無符合憲章之標的 (空手也是一種策略)"
        
        # Build raw data string
        raw_data = "\n".join([
            f"- {s['code']} {s['name']}: 現價 {s['price']}, MA20距離 {s['ma20_dist_pct']}%, 營收成長 {s['rev_growth']}"
            for s in signals
        ])
        
        prompt = f"""
你是市場分析師。以下是今日台股掃描結果 ({len(signals)} 檔標的)：

{raw_data}

請用 1-2 段話總結：
1. 整體市場趨勢 (多頭/盤整/空頭)
2. 值得關注的標的與理由
3. 風險提示

保持專業、簡潔、可執行。
"""
        
        try:
            model_config = get_model("smart")
            if not model_config.get("configured"):
                logger.warning("[WARN] Gemini not configured, using raw summary")
                return f"掃描完成，共發現 {len(signals)} 檔標的。詳見原始數據。"
            
            model = genai.GenerativeModel(model_config.get("model"))
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"[ERROR] Semantic compression failed: {e}")
            return f"掃描完成，共發現 {len(signals)} 檔標的。AI 摘要失敗。"
    
    async def run_scan(self) -> Dict:
        """Main scan execution"""
        logger.info("[OK] TWSE Scanner started")
        
        # 1. Fetch stock list
        df_list = self.get_tw_stock_list()
        if df_list.empty:
            logger.error("[ERROR] Failed to fetch stock list")
            return {"status": "failed", "message": "Stock list unavailable"}
        
        # 2. Scan stocks
        target_list = df_list.values.tolist()
        logger.info(f"[OK] Scanning {len(target_list)} stocks...")
        
        for row in target_list:
            ticker, name, suffix, _ = row
            try:
                result = self.analyze_stock(ticker, name, suffix)
                if result:
                    self.report.append(result)
                    logger.info(f"[OK] Signal: {ticker} {name} @ {result['price']}")
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                logger.debug(f"[WARN] Error analyzing {ticker}: {e}")
                continue
        
        # 3. Semantic compression
        summary = await self.semantic_compress(self.report)
        
        # 4. Store in memories
        if supabase:
            try:
                content = f"""# 全台股戰略掃描 [{datetime.now().strftime('%Y-%m-%d')}]

## AI 摘要
{summary}

## 原始訊號 ({len(self.report)} 檔)
"""
                for sig in self.report:
                    content += f"\n- **{sig['code']} {sig['name']}**: 現價 {sig['price']}, 停損 {sig['stop_loss']}, 營收成長 {sig['rev_growth']}"
                
                supabase.table("memories").insert({
                    "content": content,
                    "date": datetime.now().date().isoformat(),
                    "category": "market_intel",
                    "is_ai": True,
                    "ai_model": "TrendSniper_V24",
                    "tags": ["TWSE", "Stock", "Scanner"]
                }).execute()
                
                logger.info("[OK] Scan results saved to memories")
            except Exception as e:
                logger.error(f"[ERROR] Failed to save to database: {e}")
        
        return {
            "status": "completed",
            "signals_found": len(self.report),
            "summary": summary
        }


# Async wrapper for scheduler
async def run_twse_scan():
    """Entry point for APScheduler"""
    scanner = TWSEScanner()
    return await scanner.run_scan()
