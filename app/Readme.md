# 1. Clone / create folder
mkdir recruitment-llm && cd recruitment-llm

# 2. Create virtualenv (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install deps
pip install -r requirements.txt

# 4. Add your .env (see above)

# 5. Start server
uvicorn main:app --reload