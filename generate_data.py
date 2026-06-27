import pandas as pd
import numpy as np

# Aap ka apna PUBG probability formula
def calculate_probability(kills, loot, squad, zone):
    probability = (
        (kills / 20) * 0.30 +
        (loot / 3) * 0.25 +
        (squad / 4) * 0.25 +
        (zone / 10) * 0.20
    ) * 100
    return round(probability, 2)

# 500 random matches ka data generate kar rahe hain
data = []
for _ in range(500):
    k = np.random.randint(0, 21)   # Kills: 0 to 20
    l = np.random.randint(1, 4)    # Loot: 1 to 3
    s = np.random.randint(1, 5)    # Squad: 1 to 4
    z = np.random.randint(1, 11)   # Zone: 1 to 10
    
    w = calculate_probability(k, l, s, z)
    data.append([k, l, s, z, w])

# Naya DataFrame bana kar CSV mein save karna
df_new = pd.DataFrame(data, columns=['kills', 'loot', 'squad', 'zone', 'win%'])
df_new.to_csv("dummy_data.csv", index=False)

print("Lo ji! 500 matches ka realistic dummy_data.csv generate ho gaya! 🚀")