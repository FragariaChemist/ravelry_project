# 🧶 Ravelry Knitting Pattern Recommender

A content-based knitting pattern recommender built from Ravelry pattern data using Python, spaCy, scikit-learn, and Streamlit.

Enter a knitting pattern you like and the application recommends five similar patterns based on pattern metadata and designer notes.

## About This Project

This project was originally created as a data science project using a series of Jupyter notebooks. Years later, I returned to the project to refactor the original notebook-based code into a more maintainable Python application.

The refactor was AI-assisted. I used ChatGPT as a coding and learning partner to help review the original implementation, identify problems, explain unfamiliar concepts, suggest refactoring approaches, and work through changes incrementally. I reviewed, tested, and made the final decisions about the code and project structure.

The original work has intentionally been preserved to show the development and thought process behind the project.

- [`src/`](src/) contains the current refactored application.
- [`original_notebooks/`](original_notebooks/) contains the original Jupyter notebooks.
- [`legacy/README_original.md`](legacy/README_original.md) is the original project README, including the original analysis, data dictionaries, conclusions, and ideas for improvement.
- [`legacy/original_streamlit_app.py`](legacy/original_streamlit_app.py) contains the original Streamlit/S3 implementation.

The refactor preserves the original recommender concept while improving the project structure, data pipeline, maintainability, and deployability.

## Project Structure

```text
ravelry_project/
│
├── src/
│   ├── app.py
│   ├── recommender.py
│   ├── collect_data.py
│   ├── clean_data.py
│   ├── build_recommender.py
│   └── check_recommender.py
│
├── original_notebooks/
│   └── Original Jupyter notebook implementation
│
├── legacy/
│   ├── README_original.md
│   └── original_streamlit_app.py
│
├── data/
│   └── Pattern data used by the recommender
│
├── artifacts/
│   └── Generated recommender feature matrix
│
├── requirements.txt
├── LICENSE
└── README.md
```

The main current code is in `src/`. The `original_notebooks/` and `legacy/` directories are preserved as historical versions of the project rather than code required to run the current application.

## How the Recommender Works

The current recommender uses a combination of categorical, numerical, and text features from each knitting pattern.

### Categorical Features

- author
- yarn weight
- pattern type

These are converted into one-hot encoded features.

### Numerical Features

- difficulty rating
- gauge per inch
- maximum yardage
- price
- project count
- queued project count
- average rating

`projects_count` and `queued_projects_count` are highly skewed, so they are transformed with `log1p` before scaling.

### Text Features

Pattern notes are processed with spaCy. The text is lemmatized and cleaned, then converted into TF-IDF features.

All three feature groups are combined into a sparse feature matrix. A scikit-learn `NearestNeighbors` model using cosine distance finds the closest patterns when a recommendation is requested.

### Why the Recommender Was Refactored

The original version calculated and stored pairwise cosine distances for every pattern in a large `rav_rec.csv` file. That file was approximately 4 GB, which made the project difficult to distribute and deploy.

The refactored version stores only the sparse feature matrix and calculates nearest neighbors on demand. This reduced the storage requirements dramatically while preserving the original recommendation approach.

## Running the Application

The current application can run using the included cleaned dataset and recommender feature matrix. Ravelry API credentials are not required unless you want to refresh the underlying data.

### 1. Clone the Repository

```bash
git clone https://github.com/FragariaChemist/ravelry_project.git
cd ravelry_project
```

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start the Streamlit App

```powershell
python -m streamlit run .\src\app.py
```

The application will open in your browser. Enter the name of a knitting pattern and the app will make a best-match guess, then return five similar patterns with links to their Ravelry pages.

## Checking Recommendations

`check_recommender.py` is a diagnostic tool for inspecting how the recommender behaves for a specific pattern.

For example:

```powershell
python .\src\check_recommender.py "The Weekender"
```

The script shows:

- the selected pattern
- its five nearest neighbors
- cosine distances
- original numerical feature values
- scaled numerical values
- diagnostic distances for categorical, numerical, and text feature groups

This is useful when evaluating changes to the dataset, cleaning logic, or recommender model.

## Refreshing the Dataset

Refreshing the underlying Ravelry data is optional. The included cleaned dataset and feature matrix are enough to run the Streamlit application.

A full refresh follows this pipeline:

```text
Ravelry API
    ↓
collect_data.py
    ↓
raw pattern CSV files
    ↓
clean_data.py
    ↓
rav_clean.csv
    ↓
build_recommender.py
    ↓
feature_matrix.npz
```

### 1. Add Ravelry API Credentials

Create a local `.env` file in the project root containing your Ravelry API credentials:

```text
ravname=YOUR_USERNAME
password=YOUR_PASSWORD
```

The `.env` file is ignored by Git and should not be committed.

### 2. Collect Current Pattern Data

```powershell
python .\src\collect_data.py
```

This collects the current most-popular patterns for the supported garment categories and stores the refreshed raw data under `data/refresh/`.

### 3. Clean the Refreshed Data

```powershell
python .\src\clean_data.py
```

The cleaning pipeline normalizes values, handles missing data, calculates derived features such as `gauge_per_inch`, and creates a cleaned `rav_clean.csv`.

### 4. Build the Recommender Matrix

After promoting or placing the cleaned dataset at:

```text
data/rav_clean.csv
```

run:

```powershell
python .\src\build_recommender.py
```

This rebuilds the sparse recommender feature matrix and supporting preprocessing artifacts in `artifacts/`.

Because spaCy processes the pattern notes during this step, rebuilding the matrix may take several minutes.

## Current Dataset and Cleaning

The recommender currently uses approximately 15,000 popular Ravelry knitting patterns across three categories:

- hats
- mid-calf socks
- pullovers

The current cleaned dataset contains 14,999 patterns.

The cleaning pipeline includes several steps to make the pattern data more consistent and useful for modeling:

- normalize yarn-weight labels
- remove unsupported very rare yarn-weight values
- fill missing gauge values using typical values for the yarn weight
- calculate `gauge_per_inch`
- fill missing notes with a placeholder
- treat missing prices as free patterns
- estimate missing `max_yardage` values

For missing yardage, the current pipeline calculates the mean yardage for each yarn-weight and garment-type combination when there are enough observations available. Historical fallback values are used for groups that are too small to produce a reliable current mean.

## Original Project Materials

The original version of this project has been preserved rather than overwritten.

The original Jupyter notebooks are available in:

```text
original_notebooks/
```

They include the original work for:

- Ravelry API data collection
- data cleaning
- recommender development
- photo collection
- image-model experimentation
- exploratory plots and analysis

The original README is preserved at:

```text
legacy/README_original.md
```

It contains the original project description, data dictionaries, analysis, conclusions, limitations, and ideas for future improvements.

The first Streamlit implementation is preserved at:

```text
legacy/original_streamlit_app.py
```

That version used AWS S3 and a precomputed multi-gigabyte recommendation table. It is retained as a historical snapshot and is not required to run the current application.

## Experimental Image Classifier

The original project also included an experiment using knitting-pattern images to classify patterns as hats, pullovers, or socks using VGG16 transfer learning.

That work is preserved in the original notebooks but is separate from the current recommender application.

## Future Improvements

Possible future improvements include:

- expanding the recommender to additional garment categories
- experimenting with feature weighting
- adding filters for attributes such as yarn weight or difficulty
- evaluating recommendation quality more systematically
- moving refreshed pattern data into a database
- adding automated tests for the data-cleaning and recommender pipelines
- improving handling of patterns with identical or very similar names

## Ravelry API

Refreshing the dataset requires access to the Ravelry API:

- [Ravelry API Documentation](https://www.ravelry.com/api)
- [Ravelry API Group](https://www.ravelry.com/groups/ravelry-api)

Ravelry API credentials are not required to run the included Streamlit application.

## License

See [LICENSE](LICENSE).