import streamlit as st
import streamlit.components.v1 as components
import base64
import math
import time
import os
import io


# ==================================================
# HTML RENDER HELPER
# ==================================================
# Markdown treats any line indented 4+ spaces as a code
# block, even with unsafe_allow_html=True. Since our HTML
# snippets are written as indented strings inside functions,
# we strip leading whitespace from every line before handing
# it to st.markdown so it actually renders as HTML.

def render_html(content):
    lines = content.strip("\n").split("\n")
    cleaned = "\n".join(line.lstrip() for line in lines)
    st.markdown(cleaned, unsafe_allow_html=True)


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
# All visual effects now run on pure CSS (see styles.css), so
# this file is effectively a no-op kept only so the app can
# still call load_js() without changing its structure. It no
# longer reaches into the parent document, which was the
# source of the old cross-iframe flakiness on Streamlit Cloud.

def load_js():

    with open("static/animation.js") as f:
        js = f.read()

    components.html(
        f"<script>{js}</script>",
        height=0,
        width=0
    )


# ==================================================
# SOUND PLAYER (dedup'd against unnecessary replays)
# ==================================================
# Streamlit reruns the whole script on every interaction. Without
# guarding it, an autoplay <audio> tag re-renders (and therefore
# replays) on every single rerun, not just the first time it's
# shown. We track which sound keys have already played in this
# session and skip re-injecting the tag for ones that have,
# unless the caller explicitly asks to force a replay.

def play_sound(file_path, key=None, force=False):

    sound_key = key or file_path

    if "played_sounds" not in st.session_state:
        st.session_state["played_sounds"] = set()

    if not force and sound_key in st.session_state["played_sounds"]:
        return

    try:
        full_path = os.path.join(os.path.dirname(__file__), file_path)

        if not os.path.exists(full_path):
            full_path = file_path

        with open(full_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        b64 = base64.b64encode(audio_bytes).decode()

        md = f"""
        <audio autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        render_html(md)

        st.session_state["played_sounds"].add(sound_key)

    except FileNotFoundError:
        st.warning(f"Sound file not found: {file_path}")
    except Exception as e:
        st.error(f"Error playing sound {file_path}: {str(e)}")


# ==================================================
# BASE64 IMAGE HELPER
# ==================================================

def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# ==================================================
# HERO SECTION
# ==================================================

def show_hero():
    render_html(
        """
        <div class='hero-container'>
            <div class='hero-title'>
                🏜️ PUBG BATTLE WIN PREDICTOR
            </div>
            <div class='hero-subtitle'>
                MIRAMAR SURVIVAL ANALYSIS SYSTEM
            </div>
            <div class='hero-divider'></div>
        </div>
        """
    )


# ==================================================
# INTRO SEQUENCE
# ==================================================
# Rendered as ONE persistent HTML block. The plane flight,
# parachute drop, "Entering Miramar..." text, progress bar and
# status lines are all chained CSS @keyframes with
# animation-delay (see styles.css), so the whole sequence plays
# out inside a single render with nothing replacing it midway.
# Python only needs one time.sleep() for the total duration —
# there is no rerun in between to interrupt the animation, which
# is what made the old two-call (plane, then drop) version
# unreliable on Streamlit Cloud.

INTRO_DURATION_SECONDS = 5.4


def show_intro_sequence():

    plane_b64 = get_base64_image("assets/images/plane.png")
    character_b64 = get_base64_image("assets/images/character.png")

    render_html(
        f"""
        <div class='intro-stage'>
            <img src='data:image/png;base64,{plane_b64}' class='intro-plane'/>
            <img src='data:image/png;base64,{character_b64}' class='intro-character'/>
            <div class='intro-text-stack'>
                <div class='intro-entering'>🪂 ENTERING MIRAMAR...</div>
            </div>
            <div class='intro-progress-track'>
                <div class='intro-progress-fill'></div>
            </div>
            <div class='intro-status-line'>
                <span class='s1'>Preparing Match...</span>
                <span class='s2'>Loading Terrain...</span>
                <span class='s3'>Loading Squad...</span>
                <span class='s4'>Scanning Safe Zone...</span>
                <span class='s5'>Deploying Player...</span>
            </div>
        </div>
        """
    )

    play_sound("assets/sounds/plane.mp3", key="intro_plane")


# ==================================================
# PROBABILITY METER — ANIMATED CIRCULAR GAUGE
# ==================================================

def show_probability_meter(probability):

    probability = max(0, min(100, probability))

    radius = 80
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - probability / 100)

    if probability >= 70:
        color = "#4dff88"
    elif probability >= 50:
        color = "#ffcc33"
    else:
        color = "#ff4d4d"

    render_html(
        f"""
        <div class='gauge-wrap'>
            <svg class='gauge-svg' viewBox="0 0 200 200">
                <circle class='gauge-arc-bg' cx="100" cy="100" r="{radius}" />
                <circle
                    class='gauge-arc-fill'
                    cx="100" cy="100" r="{radius}"
                    stroke="{color}"
                    stroke-dasharray="{circumference:.2f}"
                    stroke-dashoffset="{circumference:.2f}"
                    transform="rotate(-90 100 100)"
                    style="animation: gauge-fill 1.2s ease forwards;"
                />
                <text x="100" y="96" text-anchor="middle" class='gauge-value'>{probability:.1f}%</text>
                <text x="100" y="124" text-anchor="middle" class='gauge-label'>WIN PROBABILITY</text>
            </svg>
            <style>
                @keyframes gauge-fill {{
                    from {{ stroke-dashoffset: {circumference:.2f}; }}
                    to   {{ stroke-dashoffset: {offset:.2f}; }}
                }}
            </style>
        </div>
        """
    )


# ==================================================
# RESULT DASHBOARD
# ==================================================

def show_result(result):

    probability = result["probability"]
    risk = result["risk"]

    if result.get("is_chicken_dinner"):
        play_sound("assets/sounds/victory.mp3", key="victory")
        show_celebration()
        banner_class = "good"
    elif probability >= 50:
        banner_class = "warn"
    else:
        play_sound("assets/sounds/danger.mp3", key="danger")
        banner_class = "bad"

    render_html(
        f"""
        <div class='risk-banner {banner_class}'>
            {risk}
        </div>
        """
    )

    render_html(
        f"""
        <div class='dashboard-grid'>
            <div class='dash-tile'>
                <div class='dash-tile-label'>Mean Win %</div>
                <div class='dash-tile-value'>{result['mean']}</div>
            </div>
            <div class='dash-tile'>
                <div class='dash-tile-label'>Variance</div>
                <div class='dash-tile-value'>{result['variance']}</div>
            </div>
            <div class='dash-tile'>
                <div class='dash-tile-label'>Std Dev</div>
                <div class='dash-tile-value'>{result['std']}</div>
            </div>
            <div class='dash-tile'>
                <div class='dash-tile-label'>Z-Score</div>
                <div class='dash-tile-value'>{result['z_score']}</div>
            </div>
        </div>
        """
    )


# ==================================================
# CHICKEN DINNER CELEBRATION
# ==================================================

def show_celebration():
    render_html(
        """
        <div class='celebration'>
            <div class='confetti-field'>
                <span class='confetti c1'>🎉</span>
                <span class='confetti c2'>🎊</span>
                <span class='confetti c3'>✨</span>
                <span class='confetti c4'>🎉</span>
                <span class='confetti c5'>🎊</span>
                <span class='confetti c6'>✨</span>
                <span class='confetti c7'>🎉</span>
                <span class='confetti c8'>🎊</span>
            </div>
            <div class='trophy-pop'>🏆</div>
            <div class='chicken-dinner-text'>WINNER WINNER CHICKEN DINNER</div>
        </div>
        """
    )


# ==================================================
# STAT CARDS (kept for the Statistics tab — native
# st.metric widgets, separate from the dashboard tiles)
# ==================================================

def show_stats(result):

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Mean Win %", result["mean"])
        st.metric("Variance", result["variance"])

    with col2:
        st.metric("Std Dev", result["std"])
        st.metric("Z Score", result["z_score"])


# ==================================================
# MAP-BASED SAFE ZONE
# ==================================================

def show_map_zone(zone_safety, player_health=80):
    size = 160 + (zone_safety * 14)

    map_b64 = get_base64_image("assets/images/mirammar.jpg")
    zone_b64 = get_base64_image("assets/images/blueZone.png")
    player_b64 = get_base64_image("assets/images/playerIcon.png")

    if player_health > 50:
        health_color = "#00ff00"
    elif player_health > 20:
        health_color = "#ffff00"
    else:
        health_color = "#ff0000"

    html_content = (
        f"<div class='map-frame' style='background-image:url(\"data:image/jpeg;base64,{map_b64}\"); "
        f"background-size: cover; position:relative; overflow:hidden; border-radius:12px; "
        f"width: 100%; height: 400px;'>"
        f"<img src='data:image/png;base64,{zone_b64}' style='position: absolute; top: 50%; left: 50%; "
        f"transform: translate(-50%, -50%); width: {size}px; height: {size}px; opacity: 0.75; "
        f"border-radius: 50%; box-shadow: 0 0 30px cyan;'>"
        f"<div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); "
        f"z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 4px;'>"
        f"<img src='data:image/png;base64,{player_b64}' style='width: 40px; height: 40px;'>"
        f"<div style='width: 40px; height: 6px; background-color: rgba(0,0,0,0.7); border: 1px solid black; "
        f"border-radius: 3px; overflow: hidden;'>"
        f"<div style='width: {player_health}%; height: 100%; background-color: {health_color}; "
        f"transition: width 0.3s ease-in-out;'></div></div></div></div>"
    )

    render_html(html_content)


# ==================================================
# ANIMATED MATCH SIMULATION
# ==================================================

def run_match_simulation():

    steps = [
        ("🛩️", "Plane entering Miramar...", 0.5),
        ("🪂", "Squad has dropped in!", 0.5),
        ("🎒", "Looting buildings...", 0.5),
        ("🛡️", "Zone is shrinking...", 0.5),
        ("🔫", "Engaging enemy squads...", 0.5),
        ("📊", "Calculating survival odds...", 0.5),
    ]

    progress = st.progress(0)
    status = st.empty()

    total = len(steps)

    for i, (emoji, message, delay) in enumerate(steps):
        status.markdown(f"### {emoji} {message}")
        time.sleep(delay)
        progress.progress(int((i + 1) / total * 100))

    status.empty()
    progress.empty()


# ==================================================
# RANK BADGE REVEAL
# ==================================================

def show_rank_badge(badge, commentary):
    render_html(
        f"""
        <div class='badge-reveal' style="border-color:{badge['color']};">
            <div class='badge-emoji'>{badge['emoji']}</div>
            <div class='badge-title' style="color:{badge['color']};">{badge['title']}</div>
            <div class='badge-commentary'>{commentary}</div>
        </div>
        """
    )


# ==================================================
# SQUAD COMPARISON — MVP highlight + ranked rows + chart
# ==================================================

def show_squad_comparison(squad_results):

    import pandas as pd
    import plotly.express as px

    df = pd.DataFrame(squad_results).sort_values("probability", ascending=False).reset_index(drop=True)
    best = df.iloc[0]

    st.success(
        f"🏅 MVP of the squad: **{best['name']}** "
        f"({best['probability']}% win probability)"
    )

    rows_html = "<div>"
    for i, row in df.iterrows():
        is_mvp = i == 0
        mvp_tag = "<span class='squad-mvp-tag'>MVP</span>" if is_mvp else ""
        row_class = "squad-row mvp" if is_mvp else "squad-row"
        rows_html += (
            f"<div class='{row_class}'>"
            f"<div class='squad-rank'>#{i + 1}</div>"
            f"<div class='squad-name'>{row['name']}{mvp_tag}</div>"
            f"<div>🔫 {row['kills']} kills</div>"
            f"<div class='squad-prob'>{row['probability']}%</div>"
            f"</div>"
        )
    rows_html += "</div>"

    render_html(rows_html)

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
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#f4f1ea",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


# ==================================================
# PDF MATCH REPORT
# ==================================================
# Built with ReportLab only (no Plotly chart images, no
# kaleido/Chrome dependency) so it stays cloud-safe. Covers
# player stats, probability, mean/variance/std/z-score, badge
# and commentary as requested.

def generate_match_report_pdf(result, kills, loot, squad, zone):

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#b8860b"),
        fontSize=22,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#444444"),
        spaceAfter=14,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1a1a1a"),
        spaceBefore=14,
        spaceAfter=8,
    )

    badge = result["badge"]

    elements = []

    elements.append(Paragraph("PUBG Battle Win Predictor", title_style))
    elements.append(Paragraph("Match Report — Miramar Survival Analysis", subtitle_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Match Inputs", heading_style))
    input_table = Table(
        [
            ["Kills", str(kills)],
            ["Loot Level", str(loot)],
            ["Squad Size", str(squad)],
            ["Zone Safety", str(zone)],
        ],
        colWidths=[8 * cm, 8 * cm],
    )
    input_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4c542")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(input_table)

    elements.append(Paragraph("Prediction Results", heading_style))
    result_table = Table(
        [
            ["Win Probability", f"{result['probability']}%"],
            ["Risk Assessment", result["risk"]],
            ["Mean Win % (dataset)", str(result["mean"])],
            ["Variance", str(result["variance"])],
            ["Standard Deviation", str(result["std"])],
            ["Z-Score", str(result["z_score"])],
        ],
        colWidths=[8 * cm, 8 * cm],
    )
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4c542")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(result_table)

    elements.append(Paragraph("Rank & Commentary", heading_style))
    elements.append(Paragraph(
        f"<b>Badge:</b> {badge['emoji']} {badge['title']}", styles["Normal"]
    ))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        f"<b>Commentary:</b> {result['commentary']}", styles["Normal"]
    ))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "Generated by the PUBG Battle Win Predictor — a probability & statistics project.",
        subtitle_style
    ))

    doc.build(elements)

    buffer.seek(0)
    return buffer
