
# AI‑Enhanced Company Profile Dashboard (Streamlit)

This app helps you build a client‑facing profile, estimate WACC, compare competitors, and run an event study.

## Files
- `app.py` — Streamlit app
- `requirements.txt` — Python deps for Streamlit Community Cloud
- `sample_metrics.csv` — Example financials table
- `sample_competitors.csv` — Example competitors
- `sample_returns.csv` — Example daily returns for event study

## Local run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Easiest deployment (Streamlit Community Cloud)
1. Push these files to a **public GitHub repo** (e.g., `lmt-dashboard`).
2. Go to https://streamlit.io/cloud → **New app** → connect GitHub → select repo/branch, `app.py` as the entry file.
3. Set **Python version** to 3.10+ if prompted; `requirements.txt` will auto‑install.
4. Click **Deploy**. Share the URL with teammates.

### Notes
- If you’re working in Google Colab, you can still push to GitHub (use the built‑in Git integration or `git` CLI).
- If Streamlit Cloud sleeps due to inactivity, re-opening the URL wakes it up.

## CSV Formats

### `sample_metrics.csv`
Columns: `Year,Revenue,EBITDA,EPS,FCF,NetDebt`

### `sample_competitors.csv`
Columns: `name,ticker,segment,summary`

### `sample_returns.csv`
Columns: `date,ret,mkt_ret` (returns in decimal, e.g. 0.01 for 1%)

## Event Study Method
- Market model via OLS on an estimation window **prior to** the event date.
- Abnormal Return: `AR_t = r_t – (alpha + beta * r_mkt_t)`
- CAR is cumulative sum across the event window.
