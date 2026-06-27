import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import time
import os

from logic import predict_win, simulate_custom_squad, simulate_squad, probability_trend_by_kills

os.makedirs("charts", exist_ok=True)

from visuals import (
    load_css,
    load_js,
    show_hero,
    show_plane,
    show_character_drop,
    show_map_zone,
    show_probability_meter,
    show_result,
    show_stats,
    run_match_simulation,
    show_rank_badge,
    show_squad_comparison,
    play_sound
)

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="PUBG Battle Win Predictor",   
    page_icon="🏜️",
    layout="wide"
)

# ==================================================
# LOAD CSS + JS
# ==================================================

load_css()
load_js()

# ==================================================
# SESSION STATE INIT
# ==================================================

if "started" not in st.session_state:
    st.session_state["started"] = False

if "intro_played" not in st.session_state:
    st.session_state["intro_played"] = False

if "view" not in st.session_state:
    st.session_state["view"] = "setup"

# ==================================================
# HERO
# ==================================================

show_hero()

# ==================================================
# LANDING SCREEN — only heading + start button
# ==================================================

if not st.session_state["started"]:

    st.markdown("<br><br>", unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 1, 1])


    with center_col:
        play_sound("assets/sounds/lobby.mp3")   
        if st.button(" Start Match", use_container_width=True):
            st.session_state["started"] = True
            st.rerun()

    st.stop()

# ==================================================
# INTRO ANIMATION — plays once after Start is clicked
# ==================================================

if not st.session_state["intro_played"]:

    intro_slot = st.empty()

    with intro_slot.container():
        show_plane()

    time.sleep(3)

    with intro_slot.container():
        show_character_drop()

    time.sleep(2.2)

    intro_slot.empty()

    st.session_state["intro_played"] = True

# ==================================================
# SETUP VIEW — sidebar, battlefield, predict button
# ==================================================

if st.session_state["view"] == "setup":

    st.sidebar.title("🎮 Match Controls")

    # Player Kills Input
    st.sidebar.subheader("🔫 Player Kills")

    # You (Player)
    your_kills = st.sidebar.slider("You (Your Kills)", 0, 20, 5, key="your_kills")

    # Squad Size
    squad_size = st.sidebar.selectbox("👥 Squad Size", [1, 2, 3, 4], key="squad_size")

    # Teammates kills
    teammate_kills = []
    for i in range(1, squad_size):
        kills = st.sidebar.slider(f"Teammate {i} Kills", 0, 20, 5, key=f"teammate_{i}")
        teammate_kills.append(kills)

    loot = st.sidebar.selectbox("🎒 Loot Level", [1, 2, 3])
    zone = st.sidebar.slider("🛡️ Zone Safety", 1, 10, 5)

    st.markdown("## 🏜️ Miramar Battlefield")

    show_map_zone(zone)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🪂 Predict Chicken Dinner"):

        run_match_simulation()

        result = predict_win(
            your_kills,      # your kills
            loot,
            squad_size,      # squad size
            zone
        )

        squad_results = simulate_custom_squad(
            your_kills, 
            teammate_kills, 
            loot, 
            zone, 
            squad_size
        )

        trend_df = probability_trend_by_kills(
            loot,
            squad_size,
            zone
        )

        st.session_state["result"] = result
        st.session_state["squad_results"] = squad_results
        st.session_state["trend_df"] = trend_df

        # keep the match inputs so the result page can reuse them
        st.session_state["kills"] = your_kills
        st.session_state["loot"] = loot
        st.session_state["squad"] = squad_size
        st.session_state["zone"] = zone

        st.session_state["view"] = "result"

        st.rerun()

    st.markdown("---")

    st.markdown(
        """
        <center>

        🎮 PUBG Inspired Battle Predictor

        <br>

        📊 Probability & Statistics Project

        </center>
        """,
        unsafe_allow_html=True
    )

    st.stop()

# ==================================================
# RESULT VIEW — its own page, no scrolling past
# the setup screen to reach it
# ==================================================

kills = st.session_state["kills"]
loot = st.session_state["loot"]
squad = st.session_state["squad"]
zone = st.session_state["zone"]

# ==================================================
# RESULT
# ==================================================

if "result" in st.session_state:

    result = st.session_state["result"]

    probability = result["probability"]

    if st.button("🔄 New Match"):
        st.session_state["view"] = "setup"
        st.rerun()

    # Load the dataset once here so every section below can reuse it
    try:
        df = pd.read_csv("dummy_data.csv")
    except FileNotFoundError:
        df = None

    st.markdown("---")

    tab_result, tab_squad, tab_charts, tab_stats = st.tabs([
        "🏆 Result",
        "👥 Squad",
        "📊 Charts",
        "📐 Statistics"
    ])

    # =============================================
    # TAB 1: RESULT
    # =============================================

    with tab_result:

        show_probability_meter(
            probability
        )

        show_rank_badge(
            result["badge"],
            result["commentary"]
        )

        show_result(
            result
        )

    # =============================================
    # TAB 2: SQUAD COMPARISON
    # =============================================

    with tab_squad:

        st.subheader(
            "👥 Squad Comparison"
        )

        if "squad_results" in st.session_state:

            show_squad_comparison(
                st.session_state["squad_results"]
            )

        st.markdown("---")

        st.subheader(
            "📈 What If? Win Probability vs Kills"
        )

        if "trend_df" in st.session_state:

            trend_df = st.session_state["trend_df"]

            fig_trend = px.line(
                trend_df,
                x="Kills",
                y="Win Probability",
                markers=True,
                title="How Win Probability Changes With Kills"
            )

            fig_trend.add_scatter(
                x=[kills],
                y=[probability],
                mode="markers",
                marker=dict(size=14, color="red", symbol="star"),
                name="Your Current Match"
            )

            st.plotly_chart(
                fig_trend,
                use_container_width=True
            )

    # =============================================
    # TAB 3: CHARTS
    # =============================================

    with tab_charts:

        chart_pie, chart_hist = st.columns(2)

        with chart_pie:

            st.subheader(
                "🥧 Factor Contribution"
            )

            pie_df = pd.DataFrame({

                "Factor": [
                    "Kills",
                    "Loot",
                    "Squad",
                    "Zone"
                ],

                "Weight": [
                    30,
                    25,
                    25,
                    20
                ]
            })

            fig_pie = px.pie(
                pie_df,
                names="Factor",
                values="Weight",
                hole=0.4
            )

            st.plotly_chart(
                fig_pie,
                use_container_width=True
            )

            fig_pie.write_image(
                "charts/factor_contribution.png"
            )

        with chart_hist:

            st.subheader(
                "📉 Win Rate Distribution"
            )

            if df is not None:

                fig_hist = px.histogram(
                    df,
                    x="win%",
                    nbins=10,
                    title="Dataset Win Rate Distribution"
                )

                st.plotly_chart(
                    fig_hist,
                    use_container_width=True
                )

                fig_hist.write_image(
                   "charts/win_distribution.png"
                )

            else:

                st.warning(
                    "dummy_data.csv not found"
                )

        chart_player, chart_compare = st.columns(2)

        with chart_player:

            st.subheader(
                "📊 Current Match Analysis"
            )

            player_df = pd.DataFrame({

                "Category": [
                    "Kills",
                    "Loot",
                    "Squad",
                    "Zone"
                ],

                "Value": [
                    kills,
                    loot,
                    squad,
                    zone
                ]
            })

            fig_bar = px.bar(
                player_df,
                x="Category",
                y="Value",
                title="Current Battle Statistics"
            )

            st.plotly_chart(
                fig_bar,
                use_container_width=True
            )

            fig_bar.write_image(
                "charts/player_stats.png"
            )

        with chart_compare:

            st.subheader(
                "📊 Player vs Average"
            )

            comparison_df = pd.DataFrame({

                "Category": [
                    "Dataset Mean",
                    "Current Player"
                ],

                "Value": [
                    result["mean"],
                    probability
                ]
            })

            fig_compare = px.bar(
                comparison_df,
                x="Category",
                y="Value",
                title="Player vs Average Performance"
            )

            st.plotly_chart(
                fig_compare,
                use_container_width=True
            )

            fig_compare.write_image(
                "charts/mean_comparison.png"
            )

        st.subheader(
            "🎯 Kills vs Win Probability"
        )

        if df is not None:

            scatter_fig = px.scatter(
                df,
                x="kills",
                y="win%",
                trendline="ols",
                title="Kills vs Win Probability"
            )

            st.plotly_chart(
                scatter_fig,
                use_container_width=True
            )

            scatter_fig.write_image(
                "charts/kills_vs_probability.png"
            )

        else:

            st.warning(
                "dummy_data.csv not found"
            )

    # =============================================
    # TAB 4: STATISTICS
    # =============================================

    with tab_stats:

        st.subheader(
            "📈 Statistical Analysis"
        )

        show_stats(
            result
        )

        st.markdown("---")

        st.subheader(
            "🎯 Performance Interpretation"
        )

        z = result["z_score"]

        if z > 1:

            st.success(
                f"""
                Your Z-Score is {z}

                You are performing ABOVE average players.
                """
            )

        elif z < -1:

            st.error(
                f"""
                Your Z-Score is {z}

                You are performing BELOW average players.
                """
            )

        else:

            st.info(
                f"""
                Your Z-Score is {z}

                You are close to average player performance.
                """
            )



