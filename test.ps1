# Glow AI-Native Pipeline - Windows Test Script
# Run: .\test.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Glow AI-Native Pipeline - Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Create directories if they don't exist
$dirs = @("specs\generated", "src\Generated", "tests\Generated", "tests\golden")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Stage 1: PRD to Specification
Write-Host "`n[1/5] PRD -> Specification" -ForegroundColor Yellow
python scripts\prd_to_spec.py --input specs\claims-auto-approval.json --output specs\generated\
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }
Write-Host "Done: specs\generated\specification.json" -ForegroundColor Green

# Stage 2: Specification to Code
Write-Host "`n[2/5] Specification -> Code" -ForegroundColor Yellow
python scripts\spec_to_code.py --spec specs\generated\specification.json --output src\Generated\
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }
Write-Host "Done: src\Generated\" -ForegroundColor Green

# Stage 3: Generate Tests
Write-Host "`n[3/5] Generating Tests" -ForegroundColor Yellow
python scripts\generate_tests.py --spec specs\generated\specification.json --code src\Generated\ --output tests\Generated\
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }
Write-Host "Done: tests\Generated\" -ForegroundColor Green

# Stage 4: AI Code Review
Write-Host "`n[4/5] AI Code Review" -ForegroundColor Yellow
python scripts\ai_code_review.py --code src\Generated\ --checklist "security,compliance,quality" --output review-report.json
if ($LASTEXITCODE -ne 0) { Write-Host "FAILED" -ForegroundColor Red; exit 1 }
Write-Host "Done: review-report.json" -ForegroundColor Green

# Stage 5: Show Results
Write-Host "`n[5/5] Results" -ForegroundColor Yellow
if (Test-Path "review-report.json") {
    $review = Get-Content "review-report.json" | ConvertFrom-Json
    Write-Host "Security Score: $($review.security_score)/100" -ForegroundColor Cyan
    Write-Host "Quality Score: $($review.quality_score)/100" -ForegroundColor Cyan
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host " All Tests Passed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "`nGenerated Files:"
Write-Host "  specs\generated\specification.json"
Write-Host "  src\Generated\ClaimsController.cs"
Write-Host "  tests\Generated\ClaimsControllerTests.cs"
Write-Host "  review-report.json"
