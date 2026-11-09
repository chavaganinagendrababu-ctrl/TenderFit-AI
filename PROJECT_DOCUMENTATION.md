# MCA MAJOR PROJECT DOCUMENTATION
# TENDERFIT: AI-POWERED GOVERNMENT TENDER DISCOVERY AND ELIGIBILITY CHECKER

---

## 1. PROJECT SYNOPSIS

### 1.1 Project Title
**TenderFit – AI-Powered Government Tender Discovery and Eligibility Verification System**

### 1.2 Academic Profile
- **Degree:** Master of Computer Applications (MCA)
- **Domain:** Artificial Intelligence, Full-Stack Web Development, Robotic Process Automation (RPA), Legal Cheminformatics & Procurement
- **Architecture:** Client-Server, Microservices-Ready, Event-Driven

### 1.3 Abstract
Government procurement in India represents a multi-billion dollar market across state and central departments (such as NHAI, CPWD, Railways, and Municipal Corporations). However, micro, small, and medium enterprises (MSMEs) and regional contractors struggle to discover relevant tenders across dozens of fragmented e-procurement portals. Furthermore, verifying eligibility requires manual scrutiny of 80+ page technical specification documents (NIT / RFP) containing strict conditions regarding annual financial turnover, years of technical experience, completed project thresholds, EMD requirements, and statutory certifications (GSTIN, PAN, Class-A contractor enlistment). Bidding without meeting non-negotiable clauses results in disqualification and forfeiture of bid preparation costs.

**TenderFit** resolves this challenge through an automated end-to-end software pipeline. The application employs **Playwright** browser automation to monitor and ingest tender notices from permitted public e-procurement listings with ethical security gates. Tender specification PDFs are parsed using **PyMuPDF**, and technical requirements are extracted into strict Pydantic schemas using **Gemini 2.5 Flash** with verbatim clause evidence preservation. A deterministic **Python Matching Engine** cross-references the extracted criteria against the company's verified financial track record and uploaded statutory documents, computing an indicative compliance score, identifying missing documents, recognizing MSME statutory EMD exemptions, and generating audit-ready downloadable verification reports.

---

## 2. PROBLEM STATEMENT & OBJECTIVES

### 2.1 Existing System Limitations
1. **Manual Ingestion Bottleneck:** Procurement officers and bidding managers spend 15–20 hours weekly manually searching portals like CPPP, GeM, and State PWD websites.
2. **High Document Scrutiny Overhead:** Tender conditions are buried in complex legal phrasing across large PDF documents.
3. **Risk of Bid Disqualification:** Bidders frequently overlook mandatory clauses (such as average annual turnover in the last 3 financial years or specific contractor classification), leading to immediate rejection during technical bid opening.
4. **Lack of Evidence Auditing:** No automated tool cross-checks claimed qualifications against actual uploaded balance sheets and GST certificates with clause-level traceability.

### 2.2 Proposed System Objectives
- **Automated Public Portal Discovery:** Automate web search across permitted public listing feeds using Playwright without violating portal access terms.
- **High-Fidelity Document Processing:** Extract text rapidly from digital PDFs using PyMuPDF while automatically detecting scanned bitmap PDFs requiring OCR.
- **Zero-Hallucination AI Extraction:** Leverage Gemini 2.5 Flash with structured JSON schemas and mandatory verbatim clause references.
- **Deterministic Multi-Criteria Matching:** Formulate a rule-based engine yielding `MET`, `MISSING`, `NEEDS VERIFICATION`, or `NOT APPLICABLE` verdicts with explicit rationales.
- **Audit-Ready Reporting:** Generate downloadable compliance reports detailing company claims, tender requirements, and missing statutory proofs.

---

## 3. SYSTEM SPECIFICATIONS

### 3.1 Software Requirements
- **Operating System:** Windows 10/11, Ubuntu 22.04 LTS, or macOS Sonoma
- **Programming Language:** Python 3.10+ (Tested on Python 3.13)
- **Frontend Framework:** Streamlit 1.67+
- **Backend Framework:** FastAPI 0.115+, Uvicorn 0.30+
- **Browser Automation:** Playwright with Chromium 1.64+
- **PDF Engine:** PyMuPDF (fitz) 2.1+
- **AI Model:** Google Gemini 2.5 Flash (`google-genai` SDK)
- **Database:** PostgreSQL (Production) / SQLite3 (Local Zero-Delay Fallback)
- **Object Relational Mapper (ORM):** SQLAlchemy 2.0+
- **Validation:** Pydantic v2
- **Testing:** Pytest 8.3+

### 3.2 Hardware Requirements
- **Processor:** Intel Core i3/i5/i7 (8th Gen+) or AMD Ryzen 3/5/7
- **RAM:** Minimum 8 GB (16 GB recommended for concurrent headless browser sessions)
- **Disk Space:** Minimum 2 GB free disk space for Python virtual environment, Chromium binary, and local tender PDF storage

---

## 4. ARCHITECTURAL DESIGN & WORKFLOW

### 4.1 Data Flow Diagram (DFD Level 1)

```text
+-------------------+              1. Register Profile
|  Company Bidder   | -----------------------------------------> [ 1.0 Company Module ]
+-------------------+                                                    |
         |                                                               v
         | 2. Upload Proofs (GST, Audits)                      [( Database Storage )]
         +-------------------------------------> [ 2.0 Storage Engine ]    |
                                                         |                 |
+-------------------+    3. Trigger Search               v                 |
| Public Procurement| <------------------------- [ 3.0 Playwright ]        |
|      Portals      | ------------------------->    Automation             |
+-------------------+    4. Download PDF                 |                 |
                                                         v                 |
                                                 [ 4.0 PyMuPDF ]           |
                                                         |                 |
                                                         v (Text)          |
                                                 [ 5.0 Gemini AI ]         |
                                                         |                 |
                                                         v (JSON Schema)   |
                                                 [ 6.0 Matching Engine ] <-+
                                                         |
                                                         v
                                                 [ 7.0 Report Generator ]
                                                         |
                                                         v (Downloadable .md)
                                                 +-------------------+
                                                 | Bid Reviewer/Exec |
                                                 +-------------------+
```

---

## 5. DATABASE DESIGN & SCHEMA

The database is designed with full relational normalization (3NF) using SQLAlchemy ORM.

### 5.1 Entity Relationship (ER) Overview
- **Companies (1) $\rightarrow$ CompanyDocuments (N):** One registered company can upload multiple supporting proof documents (GST, PAN, Audited Balance Sheet, Udyam MSME, Experience).
- **Tenders (1) $\rightarrow$ TenderRequirements (1):** One tender specification has one structured requirements record.
- **Companies (1) $\rightarrow$ EligibilityResults (N) $\leftarrow$ Tenders (1):** Associative entity storing the computed match verdict, percentage score, and breakdown matrix.
- **AutomationLogs:** Standalone audit trail capturing all scraping actions, timestamps, and CAPTCHA/security gate events.

### 5.2 Table Schemas

#### Table: `companies`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-Increment | Unique enterprise ID |
| `name` | String(255) | Unique, Not Null, Index | Legal business name |
| `business_category`| String(100) | Not Null, Index | Industry sector |
| `location` | String(150) | Not Null | Operational headquarters |
| `annual_turnover` | Float | Not Null, Default 0.0 | Audited 3-year turnover in INR |
| `years_of_experience` | Integer | Not Null, Default 0 | Years in operation |
| `previous_projects_count`| Integer | Not Null, Default 0 | Completed project count |
| `gst_registered` | Boolean | Not Null, Default False | GST active status |
| `gst_number` | String(30) | Nullable | 15-digit GSTIN |
| `udyam_registered` | Boolean | Not Null, Default False | MSME status |
| `udyam_number` | String(50) | Nullable | Udyam certificate ID |
| `specialisations` | Text | Nullable | Core capabilities |
| `created_at` | DateTime | Not Null | Timestamp in UTC |
| `updated_at` | DateTime | Not Null | Timestamp in UTC |

#### Table: `tenders`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-Increment | Internal tender ID |
| `tender_id` | String(100) | Unique, Not Null, Index | Portal tender reference number |
| `title` | String(500) | Not Null | Tender contract title |
| `department` | String(255) | Not Null | Procuring authority |
| `location` | String(150) | Not Null | Project execution site |
| `estimated_value` | Float | Nullable | Tender value in INR |
| `closing_date` | DateTime | Nullable | Submission deadline |
| `tender_url` | String(1000)| Not Null | Portal source link |
| `pdf_path` | String(500) | Nullable | Path to downloaded PDF on disk |
| `portal_name` | String(100) | Not Null | Source portal identifier |

---

## 6. MODULE-BY-MODULE IMPLEMENTATION

### Module 1: Company Profile Management
Allows enterprises to register their profile with strict Pydantic input validation (e.g. validating positive turnover, normalizing GSTIN to uppercase, stripping whitespace). Handles document uploads and stores files in segregated company folders under `documents/company_documents/company_<id>/`.

### Module 2: Playwright Tender Discovery
Implemented in `automation/tender_scraper.py` using Chromium.
- **BrowserManager:** Encapsulates the Playwright lifecycle, context creation, realistic user-agents, and cleanup.
- **DownloadManager:** Handles file downloads, sanitizes illegal operating system characters (`/ \ : * ? " < > |`), and verifies downloaded PDF integrity.
- **Security Gates:** `BasePortalScraper` inspects page content for CAPTCHA patterns (`g-recaptcha`, `hcaptcha`, `turnstile`) or authentication prompts (`enter otp`, `login required`). If detected, it raises `SecurityGateInterventionRequired`, logs the event, and halts execution cleanly.

### Module 3: PDF Processing Engine
Implemented in `pdf_processing/pdf_extractor.py` using PyMuPDF.
Extracts page counts, text blocks, and detects scanned/bitmap documents where extracted character count is below standard thresholds, automatically alerting users when manual verification or OCR is needed.

### Module 4: Gemini 2.5 Flash Requirement Extraction
Implemented in `ai/gemini_service.py`.
Sends extracted tender text to Gemini 2.5 Flash with structured schema instructions.
- **Evidence Traceability:** The model returns the exact original clause from the tender for every condition.
- **Regex Heuristic Fallback:** If `GEMINI_API_KEY` is not configured, the system executes a rule-based regex extractor that parses turnover, experience, completed works, EMD, and GST criteria so that absence of an API key never crashes the workflow.

### Module 5: Deterministic Eligibility Engine
Implemented in `eligibility/matching_engine.py`.
Compares company profile and uploaded documents against tender conditions:
- **Turnover:** Compares company turnover with required threshold. If met but no audited balance sheet is uploaded, flags as `NEEDS VERIFICATION`. If below threshold, flags as `MISSING` with exact deficit calculation.
- **Experience & Projects:** Validates operational years and completed projects against technical conditions.
- **GST Compliance:** Validates active GSTIN and uploaded GST registration certificate.
- **MSME / Udyam EMD Exemption:** Identifies statutory MSME benefits under Indian public procurement policy, classifying EMD requirement as `MET (Exempt under MSME)`.
- **Disclaimer Enforcement:** Appends a mandatory legal disclaimer indicating that the score is algorithmic guidance and not an official government pre-qualification award.

### Module 6: Audit Report Generator
Implemented in `reports/report_generator.py`.
Assembles an executive compliance report in GitHub-flavored Markdown detailing the enterprise profile, tender specifications, criterion-by-criterion evidence matrix, pending document warnings, and source clauses, downloadable directly via Streamlit.

---

## 7. AUTOMATED TEST SUITE & QA RESULTS

The application includes a comprehensive Pytest automated test suite across 5 test suites.

| Test File | Target Module | Test Case | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `test_company.py` | Schema Validation | `test_valid_company_creation` | Validates and normalizes GST to uppercase | Normalized successfully | ✅ PASSED |
| `test_company.py` | Schema Validation | `test_negative_turnover_rejected` | Negative turnover raises ValidationError | ValidationError raised | ✅ PASSED |
| `test_company.py` | Schema Validation | `test_negative_experience_rejected`| Negative experience raises ValidationError| ValidationError raised | ✅ PASSED |
| `test_database.py`| Database Operations | `test_create_and_retrieve_company` | Inserts and queries company record | Retrieved with identical values | ✅ PASSED |
| `test_database.py`| Database Operations | `test_duplicate_company_rejected` | Duplicate company name raises exception | Exception raised | ✅ PASSED |
| `test_database.py`| Database Operations | `test_update_company_profile` | Updates fields on company profile | Updated values verified | ✅ PASSED |
| `test_api.py` | FastAPI Endpoints | `test_health_endpoints` | Returns HTTP 200 and healthy status | Status 200 returned | ✅ PASSED |
| `test_api.py` | FastAPI Endpoints | `test_company_api_flow` | POST create, GET by ID, GET listing | 201 Created, 200 OK | ✅ PASSED |
| `test_api.py` | FastAPI Endpoints | `test_duplicate_company_api_rejected`| Returns HTTP 400 on duplicate name | HTTP 400 returned | ✅ PASSED |
| `test_automation.py`| Browser Automation | `test_security_gate_triggers_on_captcha`| CAPTCHA HTML raises SecurityGateIntervention| SecurityGate raised | ✅ PASSED |
| `test_automation.py`| Browser Automation | `test_security_gate_triggers_on_login`| Login HTML raises SecurityGateIntervention | SecurityGate raised | ✅ PASSED |
| `test_automation.py`| Browser Automation | `test_download_manager_sanitization` | Removes illegal filename characters | Sanitized filename output | ✅ PASSED |
| `test_engine_and_reports.py`| Heuristic Engine | `test_heuristic_requirement_extractor`| Parses turnover, exp, EMD from text | Extracted accurately | ✅ PASSED |
| `test_engine_and_reports.py`| Matching Engine | `test_matching_engine_eligible_company`| Eligible profile returns status MET | Status MET, Score 100% | ✅ PASSED |
| `test_engine_and_reports.py`| Matching Engine | `test_matching_engine_ineligible_turnover`| Deficit turnover returns status MISSING | Status MISSING, Score < 50% | ✅ PASSED |
| `test_engine_and_reports.py`| Report Generator | `test_report_generation` | Generates formatted Markdown report | Report assembled cleanly | ✅ PASSED |

**Total Tests:** 16  
**Passed:** 16 (100%)  
**Failed:** 0  
**Warnings:** 0  

---

## 8. DEPLOYMENT & EXECUTION

### 8.1 Local Execution
```powershell
# 1. Activate Virtual Environment
.\myenv\Scripts\Activate.ps1

# 2. Start Streamlit Application
streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501

# 3. Optional: Start FastAPI REST Backend
uvicorn backend.main:app --reload --port 8000
```

### 8.2 Streamlit Cloud Deployment
1. Repository is committed to Git (`git push origin main`).
2. Log into [share.streamlit.io](https://share.streamlit.io/).
3. Connect repository and set entrypoint to `frontend/app.py`.
4. Configure environment secrets (`GEMINI_API_KEY`) under Advanced Settings.
5. Deploy.

---

## 9. CONCLUSION & FUTURE ENHANCEMENTS

### 9.1 Conclusion
TenderFit successfully bridges the gap between complex public procurement notices and prospective bidders. By integrating browser automation, high-speed PDF text parsing, large language model condition extraction, and deterministic rule evaluation, the system reduces tender evaluation time from hours to seconds while maintaining audit compliance through verbatim source clause preservation.

### 9.2 Future Scope
- **Optical Character Recognition (OCR):** Integrate Tesseract OCR or Google Cloud Vision API for scanned image tender documents.
- **Automated Bid Document Drafting:** Generate pre-filled technical bid proposal templates (BOQ and covering letters) based on extracted criteria.
- **Multi-Portal Push Notifications:** Email/SMS notifications when tenders matching a company's sector are published on GeM or state portals.

