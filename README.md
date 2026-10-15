# Merck Commitment Report Automation

Automated data transformation and report generation pipeline for monthly regulatory commitment reports. Developed as a CS 491 Capstone project for sponsor **Merck & Co.**.

---

## 📌 Project Overview

This project automates the manual, multi-step process outlined in SOP **RPP-200-ER03 (Preparation of Monthly Commitment Reports)**. It takes raw commitment export data (e.g., from Veeva Registrations / VReg), applies complex business rules, filters, date calculations, and generates formatted Excel workbooks (e.g., GRT/SPMT reports, Red-Late, Purple-Pending views) with frozen headers and conditional formatting.

---

## 🏗️ Project Architecture

```text
Merck-Commitment-Report-Automation/
├── .github/
│   ├── dependabot.yml           # Automated dependency vulnerability scanning
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI quality gate
├── resources/                   # SOPs, scope docs, reference templates (git-ignored)
├── src/
│   ├── __init__.py
│   ├── app.py                   # Streamlit interactive UI entry point
│   ├── transforms.py            # Business logic, lifecycle filtering & date rules
│   └── excel_generator.py       # Excel formatting, multi-tab generation & styling
├── tests/
│   ├── test_smoke.py            # Environment & dependency verification
│   ├── test_transforms.py       # Unit tests for data transformation logic
│   └── test_excel_output.py     # Unit tests for workbook creation & layout
├── pyproject.toml               # Tooling configs (Ruff, Pytest)
├── requirements.txt             # Production runtime dependencies
├── requirements-dev.txt         # Developer tooling (pytest, ruff, pip-audit)
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** (Python 3.10 is used in the CI environment)
- **Git**

### 2. Local Setup

Clone the repository and set up a Python virtual environment:

```bash
# Clone repository
git clone https://github.com/<your-org>/Merck-Commitment-Report-Automation.git
cd Merck-Commitment-Report-Automation

# Create and activate virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Running the Streamlit Web Application

To launch the interactive dashboard locally:

```bash
streamlit run src/app.py
```

---

## 🧪 Testing & Code Quality

Continuous Integration (CI) enforces that all code merged to `main` meets automated quality gates. Always run these checks locally before opening a pull request:

### 1. Run Unit Tests (Pytest)
```bash
pytest tests/ -v
```

### 2. Linting & Formatting Check (Ruff)
```bash
ruff check .
```

### 3. Dependency Security Scan (pip-audit)
```bash
pip-audit
```

---

## 👥 Guidelines for Developers

1. **Test-Driven / Feature Responsibility**:
   - When assigned a ticket or implementing a feature in `src/transforms.py` or `src/excel_generator.py`, **you are required to provide or update corresponding tests** in the `tests/` directory.
   - For functions with existing stubbed tests, un-skip them by removing the `@pytest.mark.skip` decorator and ensure `pytest tests/ -v` passes.
2. **Branching & PRs**:
   - Never push directly to `main`.
   - Create a feature branch: `git checkout -b feature/your-feature-name`.
   - Open a pull request against `main`. All CI checks (`Lint, Audit, and Test`) must be green before merging.
3. **Sensitive / Sponsor Documents**:
   - Never commit raw sponsor data, client spreadsheets, or proprietary SOPs into Git.
   - Use the `resources/` folder for local reference materials—it is permanently ignored by `.gitignore`.



# comment to verify ci setup