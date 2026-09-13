# HaqDarmand AI — Backend Handoff Notes

Backend (eligibility filtering + RAG + LLM answering) is complete and tested.
This document is for whoever picks up the frontend (Streamlit UI) and whoever
does testing.

---

## 1. Setup (run this before anything else)

1. Install dependencies (langchain, langchain-google-genai, langchain-chroma,
   pandas, streamlit, python-dotenv, openpyxl).
2. A `.env` file with `GOOGLE_API_KEY`, `GEMINI_MODEL`, and `EMBEDDING_MODEL`
   is included with this handoff — just place it in the project root
   alongside the other files, don't commit it anywhere public. If it's ever
   missing or the key is invalid, the app will fail immediately on startup
   with a clear error, instead of failing later mid-search.
3. Make sure `programs.xlsx` is present in the project root — both
   `eligibility.py` and `rag.py` read it directly from disk (`EXCEL_PATH`).
   If it's missing or missing a required column, you'll get a clear error
   message naming the problem instead of a raw pandas traceback.
4. **First run only:** `rag.py`'s `get_vector_database()` automatically
   builds a Chroma DB folder (`./chroma_db`) from `programs.xlsx` if it
   doesn't already exist. This takes a little time (one embedding call per
   program row). Every run after that reuses the existing folder — see
   "Known Issues" below for why that matters if the Excel file changes.

---

## 2. How to call the backend (no API layer needed)

Since the frontend is Streamlit running in the same Python process, just
import directly — no REST calls, no JSON serialization:

```python
from backend.backend import find_programs, ask_program_question
```

### `find_programs(age, province, education, student_status, monthly_income)`
Filters `programs.xlsx` against the user's structured inputs.

**Inputs**
- `age`: number
- `province`: string (e.g. "Sindh", "Punjab" — matched loosely, aliases like
  "KPK" are normalized in `eligibility.py`)
- `education`: one of `school`, `matric`, `intermediate`, `undergraduate`,
  `postgraduate`
- `student_status`: `"Yes"` / `"No"` (case-insensitive)
- `monthly_income`: number (PKR)

**Returns (success)**
```python
{
    "success": True,
    "programs": [ { ...program dict... }, ... ],
    "program_count": int
}
```

**Returns (failure)** — e.g. bad input or an unexpected internal error:
```python
{ "success": False, "programs": [], "program_count": 0 }
```
`app.py` already checks `result["success"]` and shows an error message, so
no extra handling is needed on the frontend side for this.

Each program dict has fixed keys: `program_id`, `program_name`,
`program_name_ur`, `category`, `agency`, `benefits`, `documents`,
`application_steps`, `official_url`, `helpline`, `special_criteria`.
**Don't rename these keys without telling the frontend dev** — the UI reads
them directly by name.

### `ask_program_question(program, question)`
Takes one program dict (as returned above) plus a free-text question, and
returns an AI answer grounded only in that program's retrieved context.

**Returns (success)**
```python
{ "success": True, "program": {...}, "answer": "..." }
```

**Returns (failure)** — no context found, RAG retrieval error, or LLM error:
```python
{ "success": False, "answer": "<user-facing message explaining what went wrong>" }
```
All three failure cases are now distinguished internally (see the console
logs — `[RAG ERROR]`, `[LLM ERROR]`) but return the same `success: False`
shape to the frontend, so `app.py`'s existing `st.error(...)` handling
covers all of them without changes.

---

## 3. Error handling — what's covered now

As of this version, the backend no longer crashes the app on:
- A missing `programs.xlsx` file or missing required column (clear error
  at startup).
- A missing `GOOGLE_API_KEY` (clear error at startup, both `llm.py` and
  `rag.py`).
- A malformed/incomplete row in `programs.xlsx` (that single row is skipped
  and logged, rest of the search continues normally).
- A row with no `program_id` (skipped — it could never be matched to its
  RAG document anyway).
- The Chroma DB being unreachable, corrupted, or failing to build (returns
  a friendly "trouble accessing program information" message).
- The Gemini API call failing/timing out (returns a friendly "trouble
  generating an answer" message).

---

## 4. Known issues — still deferred, not bugs if testing finds them

1. **Stale Chroma DB on data updates** — if `programs.xlsx` is edited/updated
   after `./chroma_db` has already been built, the vector store will keep
   serving old embeddings. No automatic rebuild/hash-check exists yet. If you
   change the Excel file, delete the `chroma_db` folder and let it rebuild.
2. **Income parsing assumes a single number** — `income_matches()` in
   `eligibility.py` extracts the *first* number found via regex in
   `max_monthly_income_pkr`. Current data only has flat numbers or
   "Not income-tested," so this is safe for now, but a future value like
   "50000-100000" would silently only use 50000.

---

## 5. Handoff flow

Backend (done, tested, error-handled) → Frontend teammate (Streamlit UI,
same process, calls backend functions directly) → Testing teammate
(validates end-to-end + the two known issues above).
