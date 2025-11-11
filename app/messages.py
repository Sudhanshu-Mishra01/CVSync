# messages.py
# All user-facing and system error messages

# === SUCCESS ===
PROFILE_CREATED = "Job profile created successfully"
RESUME_ANALYZED = "Resume analyzed and saved successfully"
CANDIDATES_RETRIEVED = "Candidates retrieved"

# === CLIENT ERRORS (4xx) ===
PROFILE_EXISTS = "A job profile with this name already exists"
PROFILE_NOT_FOUND = "Job profile not found"
RESUME_NOT_FOUND = "Resume not found"
INVALID_PDF = "Only PDF files are allowed"
INVALID_FILE = "No file uploaded or invalid file"

# === SERVER / AI ERRORS (5xx) ===
PDF_PARSE_ERROR = "Failed to read the PDF file. Ensure it's not corrupted or password-protected."
LLM_ERROR = "AI analysis failed. Please try again or use a different model."
DB_ERROR = "Database error occurred"

# === INFO / DEBUG ===
APP_STARTED = "CVSync API started. No authentication required."
DB_INITIALIZED = "SQLite database initialized at recruitment.db"