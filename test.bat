@echo off
REM Glow AI-Native Pipeline - Windows Test Script
REM Run: test.bat

echo ==========================================
echo  Glow AI-Native Pipeline - Test
echo ==========================================

REM Create directories
if not exist "specs\generated" mkdir "specs\generated"
if not exist "src\Generated" mkdir "src\Generated"
if not exist "tests\Generated" mkdir "tests\Generated"
if not exist "tests\golden" mkdir "tests\golden"

echo.
echo [1/4] PRD -^> Specification
python scripts\prd_to_spec.py --input specs\claims-auto-approval.json --output specs\generated\
if %ERRORLEVEL% neq 0 (echo FAILED & exit /b 1)
echo Done: specs\generated\specification.json

echo.
echo [2/4] Specification -^> Code
python scripts\spec_to_code.py --spec specs\generated\specification.json --output src\Generated\
if %ERRORLEVEL% neq 0 (echo FAILED & exit /b 1)
echo Done: src\Generated\

echo.
echo [3/4] Generating Tests
python scripts\generate_tests.py --spec specs\generated\specification.json --code src\Generated\ --output tests\Generated\
if %ERRORLEVEL% neq 0 (echo FAILED & exit /b 1)
echo Done: tests\Generated\

echo.
echo [4/4] AI Code Review
python scripts\ai_code_review.py --code src\Generated\ --checklist "security,compliance,quality" --output review-report.json
if %ERRORLEVEL% neq 0 (echo FAILED & exit /b 1)
echo Done: review-report.json

echo.
echo ==========================================
echo  All Tests Passed!
echo ==========================================
echo.
echo Generated Files:
echo   specs\generated\specification.json
echo   src\Generated\ClaimsController.cs
echo   tests\Generated\ClaimsControllerTests.cs
echo   review-report.json
