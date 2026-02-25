@echo off
echo.
echo === LifeOS GitHub Sync (Safe) ===
echo Repository: https://github.com/lienhuangbionime-lang/LifeOSvs
echo.

echo 1. Initializing Git (if needed)...
if not exist .git (
    git init
)

echo.
echo 2. Staging all changes...
git add .

echo.
echo 3. Committing changes...
git commit -m "feat: System v3.2/v7.1 alignment, Gemini 404 fix, and Intelligence upgrade"

echo.
echo 4. Setting branch to 'main'...
git branch -M main

echo.
echo 5. Setting remote URL...
git remote remove origin
git remote add origin https://github.com/lienhuangbionime-lang/LifeOSvs

echo.
echo 6. Pushing to GitHub...
git push -u origin main --force

echo.
echo === Sync Complete ===
pause
