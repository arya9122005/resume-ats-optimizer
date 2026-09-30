# Resume & ATS Optimizer

GenAI + prompt engineering college project. Flask backend, HTML/CSS/JS frontend.

## Run it (Windows)
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env
    python app.py

## Run it (Mac/Linux)
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    python app.py

Open http://127.0.0.1:5000

## Real AI mode (Gemini)
1. Get a free key at https://aistudio.google.com/apikey
2. In `.env` set `USE_MOCK=false` and `GEMINI_API_KEY=your_key`
3. Restart `python app.py`
4. Optional terminal test: `python try_analysis.py`

## Status
- [x] Step 1-3: setup, themed UI, validation, demo mode
- [x] Step 4-5: Gemini client, shared system prompt, comparison + keyword prompts
- [ ] Step 6-7: improvement suggestions, bullet rewriting, score
