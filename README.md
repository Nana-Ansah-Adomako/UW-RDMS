# 🏥 Patient Outcomes Dashboard

An interactive Streamlit dashboard for exploring patient treatment and diagnosis data.

## 📊 Charts

- **Donut chart** — patient distribution by treatment group
- **Bar chart** — deaths within 1 year by treatment group
- **Histogram** — age at diagnosis, filterable by race

## 🗂 Required CSV Columns

Your uploaded CSV must contain these columns:

| Column | Description |
|---|---|
| `treatment_group` | Treatment group label |
| `died_within_1_year` | `Yes` or `No` |
| `race` | Patient race/ethnicity |
| `age_at_diagnosis` | Numeric age |

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/patient-dashboard.git
cd patient-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run dashboard.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select your repo, branch `main`, and file `dashboard.py`
5. Click **Deploy** — done!

## 🔒 Data Privacy

`.gitignore` is configured to exclude all `.csv` files — your patient data will **never** be committed to the repo.
