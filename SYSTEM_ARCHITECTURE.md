# System Architecture

## Overview

CodeInsight follows a simple client-server architecture where the user uploads a source file through the web interface, the Flask backend processes the request, and the analysis engine evaluates the code quality before returning scores and suggestions.

## Architecture Flow

```text
User
  |
  v
Web Browser / UI (HTML, CSS, JavaScript)
  |
  v
Flask Backend Server
  |
  v
Authentication + File Upload Handler
  |
  v
Code Analysis Engine
  |-- AST for syntax validation
  |-- Pylint for style analysis
  |-- Radon for complexity and maintainability
  |-- Custom Java Analyzer (with optional javalang parsing)
  |
  v
Scoring Module
  |
  v
Results Dashboard + PDF Report
  |
  v
Database / Storage
```

## Main Components

- **User Interface:** Provides login, registration, file upload, and results pages.
- **Flask Backend:** Handles routing, session management, and request processing.
- **Analysis Engine:** Performs Python analysis (AST, Pylint, Radon) and Java analysis (custom Java analyzer with optional javalang support).
- **Scoring Module:** Combines analysis output into a final explainable score.
- **Database / Storage:** Stores user details, uploaded file records, and analysis results.

## Data Flow

1. The user logs in and uploads a Python or Java file.
2. The Flask server receives the file and stores it safely.
3. The analysis engine inspects Python code using AST, Pylint, and Radon, and inspects Java code using the custom Java analyzer.
4. The scoring module calculates the final score and issue breakdown.
5. The dashboard displays the results and a PDF report can be generated.

## Benefits of This Architecture

- Easy to use and extend
- Clear separation between UI, backend, and analysis logic
- Supports automated and explainable code quality evaluation
- Generates consistent results and reports