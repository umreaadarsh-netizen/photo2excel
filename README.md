# Photo2Excel AI — Android + GitHub Actions

Push this project to GitHub. Open **Actions → Build Photo2Excel APK → Run workflow**. GitHub will build a debug APK and upload it as an artifact.

## Important backend note
The current OCR backend uses FastAPI at `http://localhost:8000`. On a real phone, localhost means the phone, not your PC. For a real app, host the FastAPI backend online or move OCR processing on-device.
