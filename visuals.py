import streamlit as st
import streamlit.components.v1 as components
import base64
import time
import os




# ==================================================
# HTML RENDER HELPER
# ==================================================
# Markdown treats any line indented 4+ spaces as a code
# block, even with unsafe_allow_html=True. Since our HTML
# snippets are written as indented strings inside functions,
# we strip leading whitespace from every line before handing
# it to st.markdown so it actually renders as HTML/JS.

def render_html(content):
    lines = content.strip("\n").split("\n")
    cleaned = "\n".join(line.lstrip() for line in lines)
    st.markdown(cleaned, unsafe_allow_html=True)

def show_prediction_results(win_prob=63.92):
    win_prob_html = f"<h2>WIN PROBABILITY</h2><div class='progress'><div class='progress-fill' style='width:{win_prob}%'></div></div><h1>{win_prob}%</h1>"
    badge_html = f"<div class='badge-emoji'>🥈</div><div class='badge-title' style='color:#c0c0c0;'>TOP 10 FINISHER</div><div class='badge-commentary'>Aggressive and effective — fighting for every zone. ⚔️</div>"
    render_html(win_prob_html)
    render_html(badge_html)

# ==================================================
# CSS LOADER
# ==================================================

def load_css():

    with open("static/styles.css") as f:
        css = f.read()

    # The CSS file references the map image via a relative url(),
    # which never resolves inside Streamlit's injected <style> tag.
    # Swap it for an embedded base64 data URI instead.
    map_b64 = get_base64_image("assets/images/mirammar.jpg")

    css = css.replace(
        'url("../assets/images/miramar.jpg")',
        f'url("data:image/jpeg;base64,{map_b64}")'
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )


# ==================================================
# JS LOADER
# ==================================================

def load_js():

    with open("static/animation.js") as f:

        js = f.read()

    # st.markdown() never executes <script> tags (browsers ignore
    # scripts inserted via innerHTML). components.html() renders inside
    # a real <iframe>, so the script actually runs. Since the elements
    # we want to animate (.zone, .prob-card, #player-marker, etc.) live
    # on the *parent* page, not inside this iframe, we redirect every
    # "document" lookup to "window.parent.document" so the script can
    # reach them. Streamlit's iframe is same-origin, so this is allowed.
    patched_js = js.replace(
        "document.", "window.parent.document."
    )

    components.html(
        f"<script>{patched_js}</script>",
        height=0,
        width=0
    )


# ==================================================
# SOUND PLAYER
# ==================================================

def play_sound(file_path):
    try:
        # Full relative path from project root
        full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
        
        if not os.path.exists(full_path):
            # Fallback: direct path
            full_path = file_path
        
        with open(full_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        b64 = base64.b64encode(audio_bytes).decode()
        
        md = f"""
        <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        render_html(md)
        
    except FileNotFoundError:
        st.warning(f"Sound file not found: {file_path}")
    except Exception as e:
        st.error(f"Error playing sound {file_path}: {str(e)}")
# ==================================================
# HERO SECTION
# ==================================================

def show_hero():
    render_html(
        """
        <div class='hero-container'>
            <div class='hero-title'>
                🏜️ PUBG BATTLE WIN PREDICTOR   <!-- Fixed Bug 2 -->
            </div>
            <div class='hero-subtitle'>
                MIRAMAR SURVIVAL ANALYSIS SYSTEM
            </div>
        </div>
        """
    )


# ==================================================
# PLANE ANIMATION
# ==================================================

# ==================================================
# BASE64 IMAGE HELPER
# (raw relative paths like src='assets/images/plane.png'
#  don't resolve inside Streamlit's markdown HTML, so we
#  embed images directly as base64 data URIs instead)
# ==================================================

def get_base64_image(path):

    with open(path, "rb") as f:
        data = f.read()

    return base64.b64encode(data).decode()


# ==================================================
# PLANE ANIMATION
# ==================================================

def show_plane():
    img_b64 = get_base64_image("assets/images/plane.png")
    render_html(
        f"""
        <div class='plane-container'>
            <img src='data:image/png;base64,{img_b64}' class='plane'/>
        </div>
        """
    )
    try:
        play_sound("assets/sounds/plane.mp3")
    except:
        pass


# ==================================================
# AIRDROP ANIMATION
# ==================================================

def show_character_drop():

    img_b64 = get_base64_image("assets/images/character.png")

    render_html(
        f"""
        <div class='character-container'>
            <img
            src='data:image/png;base64,{img_b64}'
            class='character'/>
        </div>
        """
    )

# ==================================================
# SAFE ZONE
# ==================================================

def show_safe_zone():

    character_b64 = get_base64_image("assets/images/character.png")

    render_html(
        f"""
        <div class='zone'>
            <img
                id='player-marker'
                class='character-marker'
                src='data:image/png;base64,{character_b64}'
            />
        </div>
        """
    )


# ==================================================
# PROBABILITY BAR
# ==================================================

def show_probability_meter(probability):

    render_html(f"<div class='prob-card'><h2>WIN PROBABILITY</h2><div class='progress'><div class='progress-fill' style='width:{probability}%'></div></div><h1>{probability}%</h1></div>")
    


# ==================================================
# RESULT CARD
# ==================================================

def show_result(result):

    probability = result["probability"]

    risk = result["risk"]

    if result.get("is_chicken_dinner"):

        play_sound(
            "assets/sounds/victory.mp3"
        )

        show_celebration()

        st.success(
            f"🏆 {risk}"
        )

    elif probability >= 50:

        st.warning(
            f"⚔️ {risk}"
        )

    else:

        play_sound(
            "assets/sounds/danger.mp3"
        )

        st.error(
            f"💀 {risk}"
        )


# ==================================================
# CHICKEN DINNER CELEBRATION (trophy + confetti)
# ==================================================

def show_celebration():

    render_html(f"""<div class='celebration'><div class='confetti-field'><span class='confetti c1'>🎉</span><span class='confetti c2'>🎊</span><span class='confetti c3'>✨</span><span class='confetti c4'>🎉</span><span class='confetti c5'>🎊</span><span class='confetti c6'>✨</span><span class='confetti c7'>🎉</span><span class='confetti c8'>🎊</span></div><div class='trophy-pop'>🏆</div><div class='chicken-dinner-text'>WINNER WINNER CHICKEN DINNER</div></div>""")



# ==================================================
# STAT CARDS
# ==================================================

def show_stats(result):

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Mean Win %",
            result["mean"]
        )

        st.metric(
            "Variance",
            result["variance"]
        )

    with col2:

        st.metric(
            "Std Dev",
            result["std"]
        )

        st.metric(
            "Z Score",
            result["z_score"]
        )


# ==================================================
# BATTLE INTRO
# ==================================================

def show_battle_intro():

    render_html(
        """
        <div class='battle-intro'>

            🛩️ Plane Entering Miramar...

            <br><br>

            📦 Airdrop Deployed...

            <br><br>

            🔫 Calculating Survival Chances...

        </div>
        """
    )


# ==================================================
# MAP-BASED SAFE ZONE
# (replaces the plain floating circle with a zone
#  that actually shrinks over the Miramar map)
# ==================================================

# 1. Updated Base64 Function (Added .decode('utf-8') to prevent raw bytes issue)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 2. Updated Render Function (Added unsafe_allow_html=True)
def render_html(html_string):
    st.markdown(html_string, unsafe_allow_html=True)

# 3. Your Main Function
def show_map_zone(zone_safety, player_health=80): 
    size = 160 + (zone_safety * 14)   

    # Images fetch karein
    map_b64 = get_base64_image("assets/images/mirammar.jpg")
    zone_b64 = get_base64_image("assets/images/blueZone.png")
    player_b64 = get_base64_image("assets/images/playerIcon.png") 

    # Dynamic Health Bar Color Logic
    if player_health > 50:
        health_color = "#00ff00"  # Green
    elif player_health > 20:
        health_color = "#ffff00"  # Yellow
    else:
        health_color = "#ff0000"  # Red

    # Single-line HTML (Player wrapper groups the icon and health bar together)
    html_content = f"<div class='map-frame' style='background-image:url(\"data:image/jpeg;base64,{map_b64}\"); background-size: cover; position:relative; overflow:hidden; border-radius:12px; width: 100%; height: 400px;'><img src='data:image/png;base64,{zone_b64}' style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: {size}px; height: {size}px; opacity: 0.75; border-radius: 50%; box-shadow: 0 0 30px cyan;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 4px;'><img src='data:image/png;base64,{player_b64}' style='width: 40px; height: 40px;'><div style='width: 40px; height: 6px; background-color: rgba(0,0,0,0.7); border: 1px solid black; border-radius: 3px; overflow: hidden;'><div style='width: {player_health}%; height: 100%; background-color: {health_color}; transition: width 0.3s ease-in-out;'></div></div></div></div>"

    render_html(html_content)
    
# ==================================================
# ANIMATED MATCH SIMULATION
# (step-by-step sequence instead of an instant result)
# ==================================================

def run_match_simulation():

    steps = [
        ("🛩️", "Plane entering Miramar...", 0.18),
        ("🪂", "Squad has dropped in!", 0.18),
        ("🎒", "Looting buildings...", 0.18),
        ("🛡️", "Zone is shrinking...", 0.18),
        ("🔫", "Engaging enemy squads...", 0.18),
        ("📊", "Calculating survival odds...", 0.18),
    ]

    progress = st.progress(0)
    status = st.empty()

    total = len(steps)

    for i, (emoji, message, frac) in enumerate(steps):

        status.markdown(f"### {emoji} {message}")
        time.sleep(0.7)
        progress.progress(int((i + 1) / total * 100))

    status.empty()
    progress.empty()


# ==================================================
# RANK BADGE REVEAL
# ==================================================

def show_rank_badge(badge, commentary):

    render_html(f"""<div class='badge-reveal' style="border-color:{badge['color']};"><div class='badge-emoji'>{badge['emoji']}</div><div class='badge-title' style="color:{badge['color']};">{badge['title']}</div><div class='badge-commentary'>{commentary}</div></div>""")


# ==================================================
# SQUAD COMPARISON
# ==================================================

def show_squad_comparison(squad_results):

    import pandas as pd
    import plotly.express as px

    df = pd.DataFrame(squad_results)

    best = df.iloc[0]

    st.success(
        f"🏅 Best performer in squad: **{best['name']}** "
        f"({best['probability']}% win probability)"
    )

    fig = px.bar(
        df,
        x="name",
        y="probability",
        color="name",
        text="probability",
        title="Squad Win Probability Comparison",
        labels={"name": "Player", "probability": "Win Probability (%)"}
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)