# Render R Markdown and Setup GitHub Pages
# Run this script from the repository root

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Pages Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if R is installed
Write-Host "Checking for R installation..." -ForegroundColor Yellow
try {
    $rVersion = Rscript --version 2>&1
    Write-Host "✓ R is installed: $rVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ R is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install R from: https://cran.r-project.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 1: Installing required R packages..." -ForegroundColor Yellow

# Install required packages
$installScript = "packages <- c('rmarkdown', 'knitr'); new_packages <- packages[!(packages %in% installed.packages()[,'Package'])]; if(length(new_packages)) { install.packages(new_packages, repos='https://cran.r-project.org'); cat('Installed:', new_packages, '\n') } else { cat('All required packages already installed\n') }"

Rscript -e $installScript

Write-Host ""
Write-Host "Step 2: Rendering proposal_requirements_guide.rmd..." -ForegroundColor Yellow

# Render the RMD file
$renderScript = "rmarkdown::render('notebook/proposal_requirements_guide.rmd', output_file = '../proposal_requirements_guide.html', output_dir = NULL)"

try {
    Rscript -e $renderScript
    Write-Host "✓ Successfully rendered proposal_requirements_guide.html" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to render RMD file" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Verifying generated files..." -ForegroundColor Yellow

# Check if files exist
$files = @(
    "index.html",
    "README.md",
    "proposal_requirements_guide.html",
    "GITHUB_PAGES_SETUP.md"
)

$allExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host ""
    Write-Host "Some files are missing. Please check the setup." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update YOUR-USERNAME in README.md and index.html" -ForegroundColor White
Write-Host "2. Commit the changes:" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m 'Set up GitHub Pages'" -ForegroundColor Gray
Write-Host "   git push origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Enable GitHub Pages in repository settings:" -ForegroundColor White
Write-Host "   Settings → Pages → Source: main branch / (root)" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Your guide will be available at:" -ForegroundColor White
Write-Host "   https://YOUR-USERNAME.github.io/pseudocode_algorithm/" -ForegroundColor Cyan
Write-Host ""
