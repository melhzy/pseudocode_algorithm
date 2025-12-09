@echo off
REM Simple batch script to render RMD and setup GitHub Pages

echo ========================================
echo GitHub Pages Setup
echo ========================================
echo.

echo Step 1: Rendering proposal_requirements_guide.rmd...
echo.

REM Try to render using Rscript
Rscript -e "rmarkdown::render('notebook/proposal_requirements_guide.rmd', output_file = file.path(getwd(), 'proposal_requirements_guide.html'))"

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to render RMD file.
    echo.
    echo Please render manually in RStudio:
    echo 1. Open notebook/proposal_requirements_guide.rmd
    echo 2. Click 'Knit' button
    echo 3. Move the HTML to root folder
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Successfully rendered proposal_requirements_guide.html
echo.

echo Step 2: Verifying files...
echo.

IF EXIST "index.html" (echo ✓ index.html) ELSE (echo ✗ index.html MISSING)
IF EXIST "README.md" (echo ✓ README.md) ELSE (echo ✗ README.md MISSING)
IF EXIST "proposal_requirements_guide.html" (echo ✓ proposal_requirements_guide.html) ELSE (echo ✗ proposal_requirements_guide.html MISSING)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Update YOUR-USERNAME in README.md and index.html
echo 2. Commit and push:
echo    git add .
echo    git commit -m "Set up GitHub Pages"
echo    git push origin main
echo.
echo 3. Enable GitHub Pages in Settings -^> Pages
echo.
pause
