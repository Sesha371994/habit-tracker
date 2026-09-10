# 🔥 Daily Streak Tracker (Habit + Water + Sleep)

100% free, no API key needed. Tracks daily habits, water intake, and sleep,
with a GitHub-style consistency heatmap and streak counter.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`

## Deploy Free on Streamlit Community Cloud

1. Create a GitHub repo, push these 3 files (`app.py`, `requirements.txt`, `README.md`)
2. Go to https://share.streamlit.io
3. Sign in with GitHub → "New app"
4. Select your repo, branch `main`, main file `app.py`
5. Click **Deploy** — done, free forever, live link generated

## Notes

- Data is saved locally in `habit_data.json` (auto-created on first run).
- On Streamlit Cloud, this file resets when the app restarts/sleeps
  (free tier has no persistent disk). For permanent storage across
  restarts, you can later swap `load_data()`/`save_data()` to use a
  free database like Supabase or Google Sheets API — ask if you want
  that upgrade.
- Edit `WATER_GOAL` and `SLEEP_GOAL` constants in `app.py` to change targets.
- Add/remove habits directly from the sidebar — no code changes needed.
