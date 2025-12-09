# Setup GitHub Pages for Proposal Requirements Guide

## Step 1: Render the R Markdown File

You need to render the `.rmd` file to create the HTML. Run this in R or RStudio:

```r
# Render the proposal guide
rmarkdown::render(
  input = "notebook/proposal_requirements_guide.rmd",
  output_file = "../proposal_requirements_guide.html",
  output_dir = NULL
)
```

This will create `proposal_requirements_guide.html` in the root directory.

## Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**:
   - Branch: `main` (or `master`)
   - Folder: `/ (root)`
4. Click **Save**

## Step 3: Access Your Guide

After a few minutes, your guide will be available at:

```
https://YOUR-USERNAME.github.io/pseudocode_algorithm/
```

The `index.html` will automatically redirect to the proposal guide.

## Alternative: Use RStudio

1. Open `notebook/proposal_requirements_guide.rmd` in RStudio
2. Click the **Knit** button
3. Move the generated HTML to root:
   ```bash
   # In PowerShell
   Move-Item notebook/proposal_requirements_guide.html . -Force
   ```

## Verify Setup

✅ Files needed for GitHub Pages:
- `index.html` (created - redirects to guide)
- `proposal_requirements_guide.html` (needs to be rendered from .rmd)
- `README.md` (created - repository documentation)

## Automated Rendering (PowerShell)

```powershell
# Render RMD to HTML in root directory
Rscript -e "rmarkdown::render('notebook/proposal_requirements_guide.rmd', output_file = '../proposal_requirements_guide.html')"

# Commit and push
git add index.html README.md proposal_requirements_guide.html
git commit -m "Set up GitHub Pages for proposal guide"
git push origin main
```

## Troubleshooting

**Problem:** RMD won't render
- **Solution:** Install required packages:
  ```r
  install.packages(c("rmarkdown", "knitr"))
  ```

**Problem:** GitHub Pages not showing
- **Solution:** 
  - Wait 5-10 minutes after enabling
  - Check Settings → Pages for any errors
  - Ensure files are in root directory
  - Check that repository is public

**Problem:** Links in README don't work
- **Solution:** Update `YOUR-USERNAME` in README.md and index.html with your actual GitHub username

## Next Steps

After setting up:

1. ✅ Render the RMD file
2. ✅ Enable GitHub Pages in settings
3. ✅ Update username in README.md and index.html
4. ✅ Commit and push all files
5. ✅ Share your guide URL!
