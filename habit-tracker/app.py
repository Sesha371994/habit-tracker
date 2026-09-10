import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os
from datetime import date, timedelta

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Daily Streak Tracker", page_icon="🔥", layout="wide")

DATA_FILE = "habit_data.json"
WATER_GOAL = 8      # glasses
SLEEP_GOAL = 7       # hours

# ----------------------------
# DATA HANDLING
# ----------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"habits": ["Exercise", "Read 10 pages", "No junk food"], "logs": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()
today_str = str(date.today())

if today_str not in data["logs"]:
    data["logs"][today_str] = {"habits": {}, "water": 0, "sleep": 0.0}

# ----------------------------
# SIDEBAR — INPUTS
# ----------------------------
st.sidebar.title("✅ Today's Check-in")
st.sidebar.caption(str(date.today().strftime("%A, %d %b %Y")))

# Add new habit
with st.sidebar.expander("➕ Add new habit"):
    new_habit = st.text_input("Habit name")
    if st.button("Add Habit"):
        if new_habit and new_habit not in data["habits"]:
            data["habits"].append(new_habit)
            save_data(data)
            st.rerun()

st.sidebar.subheader("Habits")
today_log = data["logs"][today_str]
for h in data["habits"]:
    checked = today_log["habits"].get(h, False)
    val = st.sidebar.checkbox(h, value=checked, key=f"habit_{h}")
    today_log["habits"][h] = val

st.sidebar.subheader("💧 Water Intake")
water = st.sidebar.slider("Glasses (goal: 8)", 0, 15, int(today_log.get("water", 0)))
today_log["water"] = water

st.sidebar.subheader("😴 Sleep")
sleep = st.sidebar.number_input("Hours slept (goal: 7)", 0.0, 14.0, float(today_log.get("sleep", 0.0)), step=0.5)
today_log["sleep"] = sleep

if st.sidebar.button("💾 Save Today", use_container_width=True):
    data["logs"][today_str] = today_log
    save_data(data)
    st.sidebar.success("Saved!")

data["logs"][today_str] = today_log
save_data(data)

# ----------------------------
# SCORE CALCULATION
# ----------------------------
def day_score(log, num_habits):
    if num_habits == 0:
        habit_score = 0
    else:
        habit_score = sum(1 for v in log.get("habits", {}).values() if v) / num_habits
    water_score = 1 if log.get("water", 0) >= WATER_GOAL else log.get("water", 0) / WATER_GOAL
    sleep_score = 1 if log.get("sleep", 0) >= SLEEP_GOAL else log.get("sleep", 0) / SLEEP_GOAL
    return round((habit_score + water_score + sleep_score) / 3, 2)

num_habits = len(data["habits"])
scores = {}
for d_str, log in data["logs"].items():
    scores[d_str] = day_score(log, num_habits)

# ----------------------------
# STREAK CALCULATION
# ----------------------------
def calc_streaks(scores, threshold=0.5):
    current = 0
    best = 0
    d = date.today()
    # current streak: walk backwards from today
    while True:
        s = scores.get(str(d), 0)
        if s >= threshold:
            current += 1
            d -= timedelta(days=1)
        else:
            break
    # best streak: scan all sorted dates
    if scores:
        all_dates = sorted(scores.keys())
        run = 0
        for ds in all_dates:
            if scores[ds] >= threshold:
                run += 1
                best = max(best, run)
            else:
                run = 0
    return current, best

current_streak, best_streak = calc_streaks(scores)

# ----------------------------
# MAIN PAGE
# ----------------------------
st.title("🔥 Daily Streak Tracker")
st.caption("Habits + Water + Sleep — track daily, build streaks, stay consistent.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔥 Current Streak", f"{current_streak} days")
col2.metric("🏆 Best Streak", f"{best_streak} days")
col3.metric("💧 Today's Water", f"{water}/{WATER_GOAL} glasses")
col4.metric("😴 Today's Sleep", f"{sleep} hrs")

st.divider()

# ----------------------------
# GITHUB-STYLE HEATMAP (last 180 days)
# ----------------------------
st.subheader("📅 Consistency Heatmap (last 26 weeks)")

end_date = date.today()
start_date = end_date - timedelta(days=181)
all_days = [start_date + timedelta(days=i) for i in range(182)]

# align start to Sunday for clean weeks
while all_days[0].weekday() != 6:  # Sunday = 6 in python's weekday() (Mon=0..Sun=6)
    all_days.insert(0, all_days[0] - timedelta(days=1))

weeks = (len(all_days) // 7) + 1
z = np.full((7, weeks), np.nan)
hover_text = np.full((7, weeks), "", dtype=object)

for idx, d in enumerate(all_days):
    week_idx = idx // 7
    day_idx = d.weekday()  # Mon=0 ... Sun=6
    day_idx = (day_idx + 1) % 7  # shift so Sunday=0 at top
    s = scores.get(str(d), None)
    if d <= end_date:
        z[day_idx][week_idx] = s if s is not None else 0
        hover_text[day_idx][week_idx] = f"{d}: {'%.0f' % ((s or 0)*100)}% complete"

fig = go.Figure(data=go.Heatmap(
    z=z,
    text=hover_text,
    hoverinfo="text",
    colorscale=[[0, "#ebedf0"], [0.25, "#c6e48b"], [0.5, "#7bc96f"], [0.75, "#239a3b"], [1, "#196127"]],
    showscale=False,
    xgap=3,
    ygap=3,
))
fig.update_layout(
    height=220,
    margin=dict(t=10, b=10, l=10, r=10),
    yaxis=dict(
        tickvals=list(range(7)),
        ticktext=["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        autorange="reversed",
        showgrid=False,
    ),
    xaxis=dict(showgrid=False, showticklabels=False),
    plot_bgcolor="white",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ----------------------------
# TRENDS
# ----------------------------
st.subheader("📈 Trends (last 30 days)")

trend_dates = sorted(data["logs"].keys())[-30:]
water_vals = [data["logs"][d].get("water", 0) for d in trend_dates]
sleep_vals = [data["logs"][d].get("sleep", 0) for d in trend_dates]

trend_df = pd.DataFrame({"Water (glasses)": water_vals, "Sleep (hrs)": sleep_vals}, index=trend_dates)
st.line_chart(trend_df)

st.divider()
st.caption("💡 Tip: Score = average of (habit completion %, water goal %, sleep goal %). Streak counts days ≥ 50% score.")
