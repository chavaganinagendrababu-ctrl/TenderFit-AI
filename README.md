# 🏛️ TenderFit – AI-Powered Government Tender Discovery and Eligibility Checker

> **Tagline:** *Find. Match. Win.*  
> An enterprise-grade, modular full-stack application that discovers relevant public government tenders, extracts eligibility criteria using **PyMuPDF** & **Gemini 2.5 Flash**, and matches them against company capabilities and statutory proof documents.

---

## 📌 Project Overview

Government e-procurement portals publish thousands of tender notices every day. Bidding contractors (civil construction, electrical engineering, IT, MSMEs) struggle with:
1. **Discovery:** Manually searching across fragmented public procurement portals.
2. **Eligibility Verification:** Sifting through 80+ page tender PDFs to extract minimum turnover, required experience, EMD, GST, and technical qualifications.
3. **Evidence Compliance:** Verifying whether their audited accounts and statutory certificates meet all non-negotiable clauses before spending money on bid preparation.

**TenderFit** solves this problem through an automated pipeline:
- **Playwright Browser Automation (Module 2):** Ingests live opportunities from permitted public portals with strict ethical security gate checks.
- **PyMuPDF & Gemini 2.5 Flash (Modules 3 & 4):** Extracts eligibility clauses with exact verbatim text references for audit compliance (with rule-based heuristic fallback if API key is not configured).
- **Deterministic Python Matching Engine (Module 6):** Compares company financials and certificates against tender criteria (`MET`, `MISSING`, `NEEDS VERIFICATION`).
- **Streamlit Modern SaaS Interface (Module 7):** Interactive dashboard with executive metrics, tender details, and exportable reports in a clean navy-blue and light-blue aesthetic.
- **FastAPI & PostgreSQL Backend (Modules 1 & 9):** Validated, transactional persistence with automated fallback to SQLite for seamless local execution.

---

## 🏗️ Architecture & Data Flow

```text
       +---------------------------------------------+
       |           Company Profile & Docs            |
       |  (Turnover, Experience, GST, Udyam, Proofs) |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |     Playwright Browser Discovery & Search   |
       |    • Public Portal Search & Navigation      |
       |    • Ethical Security Gate Checks (CAPTCHA) |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |         Tender PDF Ingestion & Storage      |
       |    • Automated download or direct upload    |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |     PyMuPDF Document Text Extractor         |
       |    • Digital text extraction & OCR review   |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |      Gemini 2.5 Flash Condition Extractor   |
       |    • Strict JSON & Verbatim Clause Evidence |
       |    • Heuristic regex fallback pre-fill      |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |        Pydantic Strict Validation           |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |       Python Eligibility Matching Engine    |
       |       (MET / MISSING / NEEDS VERIFICATION)  |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |      PostgreSQL / SQLite Database Storage   |
       +---------------------------------------------+
                              |
                              v
       +---------------------------------------------+
       |          Streamlit SaaS Dashboard           |
       |    • Executive Metrics & Pipeline           |
       |    • Downloadable Compliance Report (.md)   |
       +---------------------------------------------+
```

---

## 📂 Project Structure

```text
TenderFit/
├── config/
│   ├── __init__.py
│   └── settings.py              # Environment configuration & typed paths
│
├── backend/
│   ├── main.py                  # FastAPI application entrypoint
│   ├── database.py              # PostgreSQL engine with auto-fallback to SQLite
│   ├── models/
│   │   ├── __init__.py
│   │   ├── company.py           # Company & CompanyDocument models
│   │   ├── tender.py            # Tender, TenderRequirement, Eligibility models
│   │   └── log.py               # Automation audit log model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── company.py           # Pydantic validation for company profile
│   │   ├── tender.py            # Pydantic schemas for tenders & matching
│   │   └── log.py               # Pydantic schemas for logs
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── companies.py         # REST endpoints for company profiles & upload
│   │   ├── tenders.py           # REST endpoints for tender queries
│   │   └── logs.py              # REST endpoints for automation logs
│   └── services/
│       ├── __init__.py
│       ├── company_service.py   # Company business logic & document storage
│       └── tender_service.py    # Tender persistence & audit logging
│
├── automation/
│   ├── __init__.py
│   ├── browser_manager.py       # Playwright browser lifecycle manager
│   ├── download_manager.py      # Tender PDF download & verification manager
│   ├── portal_base.py           # BasePortalScraper with security gate detection
│   └── tender_scraper.py        # Scraper coordinator & public portal scraper
│
├── frontend/
│   ├── app.py                   # Streamlit Main Dashboard
│   ├── components/
│   │   ├── api_client.py        # Client connecting frontend to FastAPI & DB
│   │   └── theme.py             # Navy blue, white & blue SaaS styling
│   └── pages/
│       ├── 1_🏢_My_Company.py   # Company registration & profile management
│       ├── 2_🔍_Find_Tenders.py  # Playwright tender discovery & PDF ingestion
│       ├── 3_📁_My_Documents.py # Company proof document repository
│       ├── 4_📊_Eligibility_Reports.py # Full criteria evaluation matrix & report
│       └── 5_⚙️_Settings.py     # System configuration & diagnostic viewer
│
├── pdf_processing/
│   ├── __init__.py
│   └── pdf_extractor.py         # PyMuPDF digital text extraction & OCR review
│
├── ai/
│   ├── __init__.py
│   ├── gemini_service.py        # Gemini 2.5 Flash integration & heuristic fallback
│   └── prompts.py               # Structured extraction prompts
│
├── eligibility/
│   ├── __init__.py
│   ├── matching_engine.py       # Deterministic rule-based evaluation engine
│   └── rules.py                 # Eligibility status definitions
│
├── reports/
│   └── report_generator.py      # Markdown & text report generator
│
├── documents/
│   ├── company_documents/       # Storage for company proofs (GST, Audits, etc.)
│   └── tender_documents/        # Downloaded tender specification PDFs
│
├── tests/
│   ├── __init__.py
│   ├── test_company.py          # Pydantic schema validation tests
│   ├── test_database.py         # Database CRUD & relationship tests
│   ├── test_api.py              # FastAPI endpoint tests
│   ├── test_automation.py       # Security gates & download manager tests
│   └── test_engine_and_reports.py # Matching engine & report tests
│
├── .streamlit/
│   └── config.toml              # Streamlit SaaS UI theme configuration
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment variable templates
├── .env                         # Active configuration
├── .gitignore                   # Deployment and repository ignore rules
└── README.md                    # Documentation & portfolio guide
```

---

## 🛠️ Technology Stack & Rationale

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Rapid, reactive modern SaaS dashboard with custom CSS theme |
| **Backend API** | FastAPI | High-performance, asynchronous REST API with automatic Swagger docs |
| **Database** | PostgreSQL | Robust relational storage with ACID compliance (auto-falls back to SQLite for local MVP) |
| **ORM** | SQLAlchemy | Clean ORM models for companies, tenders, requirements, and audit logs |
| **Validation** | Pydantic v2 | Strict type safety and data hygiene across APIs and AI outputs |
| **Browser Automation** | Playwright (Python) | Resilient browser automation for public portal search and document download |
| **PDF Extraction** | PyMuPDF (fitz) | Fast extraction of text from tender specifications and corrigendums |
| **AI Integration** | Gemini 2.5 Flash | Natural-language tender clause extraction into structured JSON with evidence traceability |
| **Testing** | Pytest & TestClient | 100% test pass rate across schemas, database, endpoints, and matching engine |

---

## 🚀 Execution & Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.13)
- PowerShell or bash terminal

### 2. Activate Virtual Environment
```powershell
# In PowerShell (from project root D:\Tenderfit):
.\myenv\Scripts\Activate.ps1
```
*(If you get a script execution policy notice, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first)*

### 3. Install Dependencies & Playwright Browsers
```powershell
pip install -r requirements.txt
playwright install chromium
```

### 4. Database Setup (PostgreSQL)
By default, TenderFit is configured to connect to PostgreSQL:
```ini
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tenderfit_db
```
- **Zero-Friction Fallback:** If PostgreSQL is not yet installed or running locally, TenderFit automatically falls back to an embedded SQLite database (`tenderfit.db`) with zero manual configuration.

### 5. Running the Application

You can launch TenderFit with either or both options:

#### Option A: Launch Streamlit SaaS Dashboard (Primary Full Application)
```powershell
.\myenv\Scripts\Activate.ps1
streamlit run frontend/app.py
```
- The dashboard will open in your default browser at: **`http://localhost:8501`**

#### Option B: Launch FastAPI Backend Server (Optional REST Service)
```powershell
.\myenv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```
- Interactive API Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Status: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 🧪 Running Automated Tests

Run the full Pytest test suite:

```powershell
pytest -v
```

**16 out of 16 tests pass:**
- ✅ Company profile schema validation & normalization (GST uppercase, positive values).
- ✅ Database transactional operations, foreign key cascades, and duplicate rejection.
- ✅ FastAPI REST endpoints (registration, retrieval, listing, health checks).
- ✅ Browser automation security gate detection (CAPTCHA and login halt mechanisms).
- ✅ Heuristic and regex tender requirement extraction.
- ✅ Deterministic matching engine (MET, MISSING, NEEDS VERIFICATION).
- ✅ Audit report generation with verbatim clause references.

---

## ☁️ Deployment Guide

### Deploying to Streamlit Community Cloud (Recommended for MVP)
1. Push your repository to GitHub (ensure `.env` is ignored by `.gitignore`).
2. Visit [share.streamlit.io](https://share.streamlit.io/) and click **New app**.
3. Select your repository, branch (`main`), and set **Main file path** to: `frontend/app.py`.
4. In **Advanced settings > Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   GEMINI_MODEL = "gemini-2.5-flash"
   # Optional: external PostgreSQL URL (e.g. Supabase, Neon, ElephantSQL):
   # DATABASE_URL = "postgresql://user:password@host:5432/dbname"
   ```
5. Click **Deploy!** Streamlit Community Cloud will install dependencies and launch your application.
