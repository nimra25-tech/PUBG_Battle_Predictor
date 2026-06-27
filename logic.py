import pandas as pd
import numpy as np


# ==========================================================
# PUBG BATTLE PREDICTOR
# LOGIC ENGINE
#
# FORMULAS USED:
#
# 1. Weighted Probability
# 2. Mean
# 3. Variance
# 4. Z-Score
#
# ==========================================================


def calculate_probability(kills, loot, squad, zone):

    probability = (
        (kills / 20) * 0.30 +
        (loot / 3) * 0.25 +
        (squad / 4) * 0.25 +
        (zone / 10) * 0.20
    ) * 100

    return round(probability, 2)


# ==========================================================
# MEAN
# ==========================================================

def calculate_mean(df):

    return round(df["win%"].mean(), 2)


# ==========================================================
# VARIANCE
# ==========================================================

def calculate_variance(df):

    return round(df["win%"].var(), 2)


# ==========================================================
# STANDARD DEVIATION
# ==========================================================

def calculate_std(df):

    return round(df["win%"].std(), 2)


# ==========================================================
# Z SCORE
# ==========================================================

def calculate_z_score(player_probability, mean, std):

    if std == 0:
        return 0

    z = (player_probability - mean) / std

    return round(z, 2)


# ==========================================================
# RISK LEVEL
# ==========================================================

def get_risk_level(probability):

    if probability >= 70:
        return "CHICKEN DINNER LIKELY"

    elif probability >= 50:
        return "COMPETITIVE MATCH"

    else:
        return "HIGH ELIMINATION RISK"


# ==========================================================
# RANK BADGE
# ==========================================================

def get_rank_badge(probability):

    if probability >= 85:
        return {"title": "LEGENDARY SURVIVOR", "emoji": "👑", "color": "#f4c542"}

    elif probability >= 70:
        return {"title": "CHICKEN DINNER", "emoji": "🏆", "color": "#ffd700"}

    elif probability >= 55:
        return {"title": "TOP 10 FINISHER", "emoji": "🥈", "color": "#c0c0c0"}

    elif probability >= 35:
        return {"title": "COMBAT SURVIVOR", "emoji": "⚔️", "color": "#cd7f32"}

    else:
        return {"title": "EARLY ELIMINATION", "emoji": "💀", "color": "#ff4d4d"}


# ==========================================================
# LIVE COMMENTARY
# ==========================================================

def get_commentary(probability, kills):

    if probability >= 85:
        return "Unstoppable. The squad never stood a chance. 👑"

    elif probability >= 70:
        return "Clutch rotation, clean fights — that's a Chicken Dinner play! 🍗"

    elif probability >= 55 and kills >= 5:
        return "Aggressive and effective — fighting for every zone. ⚔️"

    elif probability >= 55:
        return "Smart positioning kept the squad alive deep into the match. 🛡️"

    elif probability >= 35:
        return "Rough fights out there, but still in the game. 🔫"

    else:
        return "Dropped hot, died fast. Next match, drop smarter. 💀"


# ==========================================================
# SQUAD SIMULATION
# (generates 3 AI teammates around the player's stats so the
#  player can be compared against their own squad)
# ==========================================================

def simulate_squad(kills, loot, squad, zone, player_name="You"):

    rng = np.random.default_rng()

    teammates = []

    names = ["Falcon", "Reaper", "Nomad"]

    for name in names:

        sim_kills = int(np.clip(rng.normal(kills, 3), 0, 20))
        sim_loot = int(np.clip(round(rng.normal(loot, 1)), 1, 3))
        sim_squad = squad
        sim_zone = int(np.clip(round(rng.normal(zone, 2)), 1, 10))

        sim_probability = calculate_probability(
            sim_kills, sim_loot, sim_squad, sim_zone
        )

        teammates.append({
            "name": name,
            "kills": sim_kills,
            "probability": sim_probability
        })

    player_probability = calculate_probability(kills, loot, squad, zone)

    squad_results = [{
        "name": player_name,
        "kills": kills,
        "probability": player_probability
    }] + teammates

    squad_results.sort(key=lambda p: p["probability"], reverse=True)

    return squad_results


# ==========================================================
# MAIN PREDICTION FUNCTION
# ==========================================================

def predict_win(kills, loot, squad, zone):

    df = pd.read_csv("dummy_data.csv")

    probability = calculate_probability(
        kills,
        loot,
        squad,
        zone
    )

    mean_win = calculate_mean(df)

    variance = calculate_variance(df)

    std = calculate_std(df)

    z_score = calculate_z_score(
        probability,
        mean_win,
        std
    )

    risk = get_risk_level(probability)

    badge = get_rank_badge(probability)

    commentary = get_commentary(probability, kills)

    is_chicken_dinner = probability >= 70

    return {

        "probability": probability,

        "mean": mean_win,

        "variance": variance,

        "std": std,

        "z_score": z_score,

        "risk": risk,

        "badge": badge,

        "commentary": commentary,

        "is_chicken_dinner": is_chicken_dinner
    }


# ==========================================================
# PROBABILITY TREND (how probability changes as kills vary,
# holding loot/squad/zone fixed at current values)
# ==========================================================

def probability_trend_by_kills(loot, squad, zone):

    kills_range = list(range(0, 21))

    probabilities = [
        calculate_probability(k, loot, squad, zone)
        for k in kills_range
    ]

    return pd.DataFrame({
        "Kills": kills_range,
        "Win Probability": probabilities
    })


# ==========================================================
# CUSTOM SQUAD SIMULATION (NEW FUNCTION)
# ==========================================================

def simulate_custom_squad(your_kills, teammate_kills, loot, zone, squad_size):
    squad_results = []
   
    # You (Main Player)
    your_prob = calculate_probability(your_kills, loot, squad_size, zone)
    squad_results.append({
        "name": "You",
        "kills": your_kills,
        "probability": your_prob
    })
   
    names = ["Falcon", "Reaper", "Nomad"]
   
    for i, kills in enumerate(teammate_kills):
        if i >= len(names): break  # Safety
        prob = calculate_probability(kills, loot, squad_size, zone)
        squad_results.append({
            "name": names[i],
            "kills": kills,
            "probability": prob
        })
   
    # Sort by highest probability
    squad_results.sort(key=lambda p: p["probability"], reverse=True)
    return squad_results


# ==========================================================
# TESTING
# ==========================================================

if __name__ == "__main__":

    result = predict_win(
        kills=8,
        loot=3,
        squad=4,
        zone=8
    )

    print("\nRESULT\n")

    for key, value in result.items():
        print(key, ":", value)