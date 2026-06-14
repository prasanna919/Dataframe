# Clean DataFrame Agent

## Team Information

### Team Name

**Team 12**

### Team Members

| S.No | Name                         |
| ---- | ---------------------------- |
| 1    | KORADA SARVAN SRI            |
| 2    | PARAVADA JAGADEESWARI        |
| 3    | LAKKOJI PRASANNA SAI LAKSHMI |
| 4    | CHILAKALAPUDI VARSHIK RAM    |

### Resumes

All team member resumes are available in the `/resumes` folder.

---

## Project Overview

The Clean DataFrame Agent is an AI-assisted data cleaning solution designed to process real-world CSV datasets. The system profiles datasets, recommends cleaning operations, applies user-approved transformations, and generates cleaned outputs along with summary reports.

---

## Repository Structure

```text
Dataframe/
│
├── agents/
│   ├── profiler.py
│   ├── cleaner.py
│   └── recommender.py
│
├── sample_data/
│   ├── employees.csv
│   ├── customers.csv
│   └── organizations.csv
│
├── output/
│   ├── cleaned_data.csv
│   └── cleaning_report.md
│
├── reports/
│   ├── AI_Usage_Note.pdf
│   ├── Project_Report.pdf
│   └── Screenshots.pdf
│
├── resumes/
│   ├── Korada_Sarvan_Sri.pdf
│   ├── Paravada_Jagadeeswari.pdf
│   ├── Lakkoji_Prasanna_Sai_Lakshmi.pdf
│   └── Chilakalapudi_Varshik_Ram.pdf
│
├── test_cases/
│   ├── test_profiler.py
│   ├── test_cleaner.py
│   └── test_recommender.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── package-lock.json
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Features

* Automated CSV Profiling
* Missing Value Detection
* Duplicate Record Identification
* Data Type Validation
* Data Cleaning Recommendations
* User Confirmation Workflow
* Clean CSV Export
* Summary Report Generation

---

## Setup Instructions

### Prerequisites

* Python 3.10+
* pip

### Installation

```bash
git clone <repository-url>
cd Clean_Dataframe
pip install -r requirements.txt
```

---

## Run Instructions

Execute the application using:

```bash
python main.py
```

Follow the prompts to:

1. Upload or select a CSV file.
2. Review profiling results.
3. Approve recommended cleaning actions.
4. Generate cleaned output and reports.

---

## Architecture Overview

```text
Input CSV
    │
    ▼
Profiler Agent
    │
    ▼
Recommendation Agent
    │
    ▼
User Approval
    │
    ▼
Cleaning Agent
    │
    ▼
Clean CSV + Summary Report
```

---

## Assumptions

* Input data is provided in CSV format.
* Users review and approve cleaning recommendations.
* Files are encoded in UTF-8 whenever possible.

---

## Limitations

* Supports CSV files only.
* Extremely large datasets may require additional optimization.
* Cleaning recommendations are rule-based and may require user verification.

---

# Deliverables

## 1. Public GitHub Repository

* Complete source code
* Clean commit history
* Project documentation

Repository Link:

> https://github.com/prasanna919/Dataframe



## 2. Demo Video (5–7 Minutes)

Video Demonstration:

> https://drive.google.com/file/d/12UoYyVoaXqqZiwzuus4H7kOWR20P3n2R/view?usp=sharing

The demo should cover:

* Project introduction
* Dataset upload
* Profiling process
* Cleaning recommendations
* Cleaned output generation
* Summary report generation

---

## 3. AI Usage Note

Document available in:

```text
/docs/AI_Usage_Note.pdf
```

Contents:

* What AI helped with
* What AI got wrong
* Best prompts used
* Lessons learned

---

## 4. Sample Data Folder

Location:

```text
/sample_data
```

Includes:

* Input datasets
* Expected outputs
* Sample reports

---

## 5. Test Cases

Location:

```text
/ test_cases
```

Includes:

* Happy Path Tests
* Input Validation Tests
* Data Cleaning Verification Tests

Run tests using:

```bash
pytest
```

---

## Technology Stack

* Python
* Pandas
* NumPy
* Pytest
* Git & GitHub

---

## License

This project is developed for academic and placement evaluation purposes.
