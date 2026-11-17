# Employee Data Analysis and API Testing Project

## Project Overview

This project includes employee data analysis using Python and Pandas, along with API development and integration testing using FastAPI, SQLAlchemy, and pytest.

The data analysis explores salary differences across departments and the relationship between employee age and salary. Matplotlib is used to create visualisations.

The API testing work covers customer endpoints, employee endpoints, and webhook functionality.

## Project Features

### Employee Data Analysis
- Data cleaning and analysis using Pandas.
- Salary comparison across departments.
- Analysis of age and salary relationships.
- Visualisations using Matplotlib.

### API Development
- Customer CRUD operations.
- Employee API endpoints.
- API key authentication.
- Webhook signature validation using HMAC.

### Integration Testing
- Integration tests using pytest and FastAPI TestClient.
- Separate SQLite test database.
- Tests for successful requests and erro responses.
- Webhook tests for valid, tampered, and missing signatures.
- Test coverage reporting using pytest-cov.

## Project Files

- `analysis.ipynb` – Data cleaning, analysis and visualisations.
- `analysis.html` – Exported HTML report.
- `report_summary.md` – Summary of findings and recommendations.
- `reports/figures/` – Saved charts.
- `src/` – API application, database, models, schemas and security modules.
- `tests/` – Integration test files and fixtures.

## Requirements

Python 3 and the packages listed in `requirements.txt` are required.

## Installation

1. Open the project folder in VS Code.
2. Activate your virtual environment.
3. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

## Running the Data Analysis

Start Jupyter:

```powershell
py -m jupyter notebook
```

Open `analysis.ipynb` and run the notebook cells.

## Running the API

Start the Customer API:

```powershell
py -m uvicorn src.customer_api:app --reload
```

## Running Tests

Run all tests:

```powershell
py -m pytest -v
```

Run tests with coverage:

```powershell
py -m pytest --cov=src --cov-report=term-missing
```

## Test Results

- Total tests: 23
- Passed: 23
- Customer API, Employee API and Webhook tests included.

## Visualisations

The data analysis includes:

1. Bar chart
2. Histogram
3. Scatter plot
4. Line chart
5. Box plot