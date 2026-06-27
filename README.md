#  PUBG Battle Win Predictor

A PUBG-themed **Streamlit web app** that predicts your chances of winning a match using probability and statistics — built as a portfolio/university project combining a real prediction engine with an immersive, game-inspired UI.

🔗 **Live App: https://pubgbattlepredictor-m6p3shtm9xdphmn3ymsdxb.streamlit.app/
 **Repo:** `nimra25-tech/PUBG_Battle_Predictor`

---

##  Overview

Enter your match stats — kills, loot level, squad size, zone safety — and the app calculates your **Win Probability**, compares you against a simulated dataset of matches, ranks your squad, and generates a downloadable match report.

It's framed entirely around PUBG's Miramar map theme: plane intro, parachute drop, blue zone visualization, rank badges, live commentary, and a Chicken Dinner celebration when you win.

---

##  Features

-  **Cinematic Intro** — plane flyover → parachute drop → "Entering Miramar..." loading sequence, built in pure CSS so it plays reliably on both localhost and Streamlit Cloud
-  **Probability Prediction Engine** — weighted formula based on kills, loot, squad size, and zone safety
-  **Statistics Engine** — Mean, Variance, Standard Deviation, and Z-Score calculated against a simulated match dataset
-  **Animated Win Probability Gauge** — circular SVG gauge with color-coded risk level
-  **Rank Badges & Commentary** — from "Early Elimination" to "Legendary Survivor," with dynamic match commentary
-  **Squad Comparison** — simulates AI teammates, ranks the squad, and highlights the MVP
-  **Interactive Plotly Charts** — factor contribution, win-rate distribution, kills vs. win probability, player vs. dataset average, "what-if" probability trend
-  **Miramar Battlefield Visualization** — animated shrinking blue zone over the map
-  **Chicken Dinner Celebration** — confetti, trophy animation, and victory sound on a win
-  **Sound Effects** — lobby, plane, victory, and danger sounds (de-duplicated so they don't replay on every rerun)
-  **PDF Match Report** — one-click download of a full report (stats, probability, badge, commentary) generated with ReportLab
- **Responsive, Glassmorphism UI** — polished gold/military color palette, animated cards, and mobile-friendly layout

---

##  How the Prediction Works

Win probability is calculated as a weighted combination of four factors:

| Factor | Weight |
|---|---|
| Kills | 30% |
| Loot Level | 25% |
| Squad Size | 25% |
| Zone Safety | 20% |

```python
probability = (
    (kills / 20) * 0.30 +
    (loot / 3)  * 0.25 +
    (squad / 4) * 0.25 +
    (zone / 10) * 0.20
) * 100
```

Your result is then compared against a simulated dataset of 500 matches (`dummy_data.csv`) using:

- **Mean** — average win % across the dataset
- **Variance** & **Standard Deviation** — spread of outcomes
- **Z-Score** — how far above/below average your performance is

Based on the probability, the app assigns a **risk level**, a **rank badge** (Legendary Survivor → Early Elimination), and generates matching **commentary**.

---

##  Project Structure

```
PUBG_Battle_Predictor/
├── app.py                  # Main Streamlit app — UI flow, pages, session state
├── visuals.py               # All visual components (intro, gauge, dashboard, PDF report, etc.)
├── logic.py                 # Prediction engine — probability, stats, squad simulation
├── generate_data.py          # Generates dummy_data.csv (500 simulated matches)
├── dummy_data.csv             # Simulated match dataset used for comparison stats
├── requirements.txt           # Python dependencies
├── Procfile                  # Process file for deployment
├── render.yaml                # Render.com deployment config
├── static/
│   ├── styles.css           # Theme, animations, gauge, dashboard, intro sequence
│   └── animation.js          # Reserved JS hook (all effects are CSS-driven)
├── assets/
│   ├── images/               # Plane, character, map, zone, and player icons
│   └── sounds/                # Lobby, plane, victory, and danger sound effects
└── charts/                    # Reserved output folder (unused — charts display in-app only)
```

---

##  Running Locally

```bash
git clone https://github.com/nimra25-tech/PUBG_Battle_Predictor.git
cd PUBG_Battle_Predictor
pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Deployment

This project is deployed on **Streamlit Community Cloud**, connected directly to this GitHub repository.

To update the live app after making changes:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

Streamlit Cloud automatically detects the push and redeploys — no manual steps needed. If it doesn't pick up the change after a minute or two, go to your app on [share.streamlit.io](https://share.streamlit.io) → **⋮ menu → Reboot app**.

---

##  Tech Stack

- **Streamlit** — web app framework
- **Pandas / NumPy** — data handling and simulation
- **Plotly** — interactive charts
- **ReportLab** — PDF match report generation
- **HTML / CSS** — custom theming and animations (no JavaScript dependency for visual effects)

---

##  Notes

- All charts are rendered for in-app display only — no image export (`write_image()`/Kaleido) is used, which keeps the app fully compatible with Streamlit Community Cloud (no headless Chrome dependency).
- The intro animation, probability gauge, badges, and celebration effects are built entirely with CSS so they behave identically on localhost and in the cloud.

---

## 📄 License

This project is for educational and portfolio purposes.
