# TenderFit - Single Click Launcher for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   TenderFit: AI Government Tender Discovery & Matcher   " -ForegroundColor Cyan
Write-Host "   Tagline: Find. Match. Win.                            " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$VenvPython = ".\myenv\Scripts\python.exe"
$VenvStreamlit = ".\myenv\Scripts\streamlit.exe"

if (-Not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Virtual environment not found in .\myenv" -ForegroundColor Red
    Write-Host "Run: python -m venv myenv; .\myenv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    Exit 1
}

Write-Host "`n[1/2] Checking database..." -ForegroundColor Green
& $VenvPython -c "from backend.database import init_db; init_db()"

Write-Host "`n[2/2] Launching TenderFit Streamlit Dashboard on http://127.0.0.1:8501..." -ForegroundColor Green
& $VenvStreamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501
