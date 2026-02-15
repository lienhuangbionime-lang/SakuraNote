-- Migration: 005_cortex_growth_logs
-- Description: Create table for AI Decision Matrix and Growth Logs (Glass Box Protocol)
-- Date: 2026-02-14

CREATE TABLE IF NOT EXISTS public.cortex_growth_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_context TEXT NOT NULL,
    options_provided JSONB NOT NULL,
    user_choice TEXT NOT NULL,
    ai_prediction TEXT,
    prediction_match BOOLEAN,
    lessons_learned TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Optional: Add constraints or indexes
    CONSTRAINT check_options_json CHECK (jsonb_typeof(options_provided) = 'object')
);

-- Add comments for documentation
COMMENT ON TABLE public.cortex_growth_logs IS 'AI 決策與演化日誌表（玻璃盒協議核心）';
COMMENT ON COLUMN public.cortex_growth_logs.decision_context IS '決策背景與面臨的問題';
COMMENT ON COLUMN public.cortex_growth_logs.options_provided IS '系統給出的選項矩陣 (A vs B)';
COMMENT ON COLUMN public.cortex_growth_logs.user_choice IS '指揮官最終的選擇';
COMMENT ON COLUMN public.cortex_growth_logs.ai_prediction IS '系統原先預測的選擇';
COMMENT ON COLUMN public.cortex_growth_logs.prediction_match IS '預測是否命中 (用於計算誤判率)';
COMMENT ON COLUMN public.cortex_growth_logs.lessons_learned IS '從此次決策中提取的新偏好權重';

-- Add RLS policies (Open for now, can be restricted later)
ALTER TABLE public.cortex_growth_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all access to cortex_growth_logs"
ON public.cortex_growth_logs
FOR ALL
USING (true)
WITH CHECK (true);
