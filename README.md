# Pseudocode Algorithm Repository

A comprehensive educational resource for understanding machine learning algorithms through detailed pseudocode explanations and R Markdown presentations.

## 📚 Overview

This repository provides:

- **Detailed Pseudocode Examples** - Step-by-step algorithm implementations
- **R Markdown Presentations** - Interactive slides with code examples
- **Literature Collection Tools** - Scripts to download research papers from PubMed Central
- **Dissertation Proposal Guide** - Comprehensive guide for doctoral students

## 📁 Repository Structure

```
pseudocode_algorithm/
├── examples/              # Pseudocode algorithm examples
│   ├── random_forest.txt  # Random Forest algorithm pseudocode
│   ├── random_forest.rmd  # Random Forest presentation
│   ├── xgboost.txt        # XGBoost algorithm pseudocode
│   └── xgboost.rmd        # XGBoost presentation
│
├── notebook/              # R Markdown guides and notebooks
│   └── proposal_requirements_guide.rmd  # Dissertation proposal guide
│
├── scripts/               # Utility scripts for literature collection
│   ├── utils/
│   │   └── literature_downloader.py     # PMC article downloader
│   ├── download_all_literature.py        # Batch downloader
│   └── pmc_literature_keywords_algorithms.csv
│
├── papers/                # Reference papers (PDFs)
│   ├── randomforest2001.pdf
│   └── xgboost_chenAemb.pdf
│
├── archive/               # Archived materials and API keys (not in git)
├── requirements/          # Requirements documents (not in git)
│   └── proposal/          # Dissertation proposal templates
└── rmd_template/          # R Markdown templates
```

## 🎯 Featured Content

### 1. Algorithm Pseudocode Examples

#### Random Forest

- **File:** `examples/random_forest.txt`
- **Presentation:** `examples/random_forest.rmd`
- **Topics Covered:**
  - Bootstrap sampling and bagging
  - Random feature selection
  - Decision tree construction
  - Ensemble prediction
  - Out-of-bag error estimation
- **References:** Breiman (2001), Heineman et al. (2009)

#### XGBoost

- **File:** `examples/xgboost.txt`
- **Presentation:** `examples/xgboost.rmd`
- **Topics Covered:**
  - Gradient boosting framework
  - Second-order Taylor expansion
  - Regularization techniques
  - Split finding algorithms
  - Missing value handling
- **References:** Chen & Guestrin (2016)

### 2. Dissertation Proposal Requirements Guide

**📖 [View the Guide](https://melhzy.github.io/pseudocode_algorithm/)**

A comprehensive 1000+ line guide covering:

- **Two Proposal Formats:** Published Papers vs Traditional
- **Evaluation Rubrics:** 11-dimension scoring framework
  - 7 dimensions for written proposals
  - 4 dimensions for oral presentations
- **Defense Preparation:** Timeline, structure, and strategies
- **Writing Standards:** APA formatting and scholarly presentation
- **Project Management:** Timeline, milestones, and tracking tools
- **Common Pitfalls:** Top 10 mistakes and how to avoid them
- **Templates and Checklists:** Ready-to-use resources

**Key Features:**

- ✅ Detailed rubrics with 4 scholarship levels (Exemplary, Developed, Developing, Emerging)
- ✅ Self-assessment checklist
- ✅ PPT/presentation guidelines
- ✅ Pass/fail criteria
- ✅ Interactive TOC with floating navigation
- ✅ Hidden code chunks (show/hide functionality)

## 🚀 Getting Started

### Prerequisites

**For R Markdown Presentations:**

```r
install.packages(c("rmarkdown", "knitr", "randomForest", "xgboost", "caret", "ggplot2"))
```

**For Literature Download Scripts:**

```bash
pip install requests pandas
```

### Setting Up GitHub Pages

**Quick Start:**

1. **Clone the repository:**

```bash
git clone https://github.com/melhzy/pseudocode_algorithm.git
cd pseudocode_algorithm
```

2. **Render the proposal guide:**

   **Option A - RStudio (Recommended):**

   - Open `notebook/proposal_requirements_guide.rmd` in RStudio
   - Click the **Knit** button
   - Move the HTML to root:
     ```powershell
     Move-Item notebook/proposal_requirements_guide.html . -Force
     ```

   **Option B - R Command Line:**

   ```r
   rmarkdown::render(
     "notebook/proposal_requirements_guide.rmd",
     output_file = file.path(getwd(), "proposal_requirements_guide.html")
   )
   ```
3. **Enable GitHub Pages:**

   - Go to **Settings** → **Pages**
   - Source: `main` branch, `/ (root)` folder
   - Click **Save**
4. **View your guide at:**

   ```
   https://melhzy.github.io/pseudocode_algorithm/
   ```

See [`GITHUB_PAGES_SETUP.md`](GITHUB_PAGES_SETUP.md) for detailed instructions.

### Viewing Presentations Locally

**Open RMD files in RStudio:**

```r
# For Random Forest presentation
rmarkdown::render("examples/random_forest.rmd")

# For XGBoost presentation
rmarkdown::render("examples/xgboost.rmd")
```

### Using Literature Download Scripts

1. **Set up your NCBI API key:**

   - Get your API key from: https://www.ncbi.nlm.nih.gov/account/settings/
   - Place it in `archive/ncbi_api_key.txt` (this file is gitignored)
2. **Download papers:**

```bash
# Single keyword search
python scripts/utils/literature_downloader.py "random forest" --max-results 10

# Batch download from keywords file
python scripts/download_all_literature.py
```

3. **Customize keywords:**
   - Edit `scripts/pmc_literature_keywords_algorithms.csv`
   - Add your search terms, categories, and priorities

## 📊 R Markdown Presentations

Each algorithm presentation includes:

- **Algorithm Overview** - Conceptual explanation
- **Pseudocode** - Step-by-step implementation
- **Key Concepts** - Important terminology and techniques
- **R Code Examples** - Working implementations
- **Complexity Analysis** - Time and space complexity
- **Applications** - Real-world use cases
- **References** - Original papers and resources

**Presentation Format:** Slidy HTML (keyboard navigation: →/← or Page Up/Down)

## 📝 Dissertation Proposal Guide

### Rendering the Guide

To generate the HTML guide:

```r
# In RStudio
rmarkdown::render(
  "notebook/proposal_requirements_guide.rmd",
  output_file = "proposal_requirements_guide.html"
)
```

### Guide Structure

1. **Introduction** - Purpose and overview
2. **Two Proposal Formats** - Choosing between Published Papers and Traditional
3. **Common Requirements** - Essential components for both formats
4. **Format-Specific Details** - Chapter-by-chapter requirements
5. **Detailed Requirements** - Literature review, methodology, etc.
6. **Evaluation Rubrics** - Complete scoring framework (NEW!)
7. **Proposal Defense** - Structure, timeline, and outcomes
8. **Defense Preparation** - Before, during, and after strategies
9. **Writing Standards** - Formatting and citation guidelines
10. **Timeline Management** - Project phases and milestones
11. **Common Pitfalls** - Mistakes to avoid
12. **Committee Expectations** - What they're looking for
13. **Resources** - Tools and support services
14. **Action Items** - Step-by-step next steps
15. **Final Thoughts** - Keys to success
16. **Appendix** - Templates and examples
17. **Contact Information** - Key resources
18. **Success Stories** - Example improvements
19. **Summary** - Key takeaways

## 🔧 Configuration

### GitHub Pages Setup

This repository is configured for GitHub Pages. The proposal guide is available at:

**https://melhzy.github.io/pseudocode_algorithm/**

To enable GitHub Pages for your fork:

1. Go to repository **Settings** → **Pages**
2. Under **Source**, select:
   - Branch: `main` (or `master`)
   - Folder: `/ (root)`
3. Click **Save**
4. The guide will be available at the URL shown

### File Exclusions

The following are excluded from version control (`.gitignore`):

- `archive/` - API keys and archived materials
- `requirements/` - Proposal templates and documents
- Python cache files (`__pycache__/`, `*.pyc`)
- R temporary files (`.Rhistory`, `.RData`)
- IDE files (`.vscode/`, `.idea/`)

## 📚 References

### Key Papers

1. **Breiman, L. (2001).** Random forests. *Machine Learning, 45*(1), 5-32.
2. **Chen, T., & Guestrin, C. (2016).** XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785-794).
3. **Heineman, G. T., Pollice, G., & Selkow, S. (2009).** *Algorithms in a Nutshell*. O'Reilly Media.

### Additional Resources

- **Random Forest Documentation:** https://scikit-learn.org/stable/modules/ensemble.html#forest
- **XGBoost Documentation:** https://xgboost.readthedocs.io/
- **NCBI E-utilities:** https://www.ncbi.nlm.nih.gov/books/NBK25501/

## 🤝 Contributing

Contributions are welcome! Please feel free to:

- Add more algorithm examples
- Improve existing pseudocode
- Enhance R Markdown presentations
- Fix bugs in download scripts
- Improve documentation

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-algorithm`)
3. Commit your changes (`git commit -am 'Add new algorithm'`)
4. Push to the branch (`git push origin feature/new-algorithm`)
5. Create a Pull Request

## 📄 License

This project is licensed under the terms specified in the `LICENSE` file.

## 👤 Author

**Pseudocode Algorithm Project**

## 🙏 Acknowledgments

- Original algorithm authors: Breiman, Chen, Guestrin, and others
- R Community for excellent documentation and packages
- NCBI for providing PubMed Central API access
- Academic institutions for proposal guidance frameworks

## 📞 Contact

For questions about:

- **Algorithm content:** Review examples and presentations
- **Literature downloads:** Check scripts README
- **Proposal guide:** See guide sections 17 (Contact Information)

---

**⭐ Star this repository if you find it helpful!**

Last Updated: December 2025
