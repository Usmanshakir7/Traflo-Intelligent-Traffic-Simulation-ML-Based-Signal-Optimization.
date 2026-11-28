
"""Streamlit sidebar inputs for traffic scenarios."""

import streamlit as st

ROADS = ("North", "South", "East", "West")

PRESETS = {
    "Normal traffic": {
        "initial": {"North": 12, "South": 8, "East": 6, "West": 10},
        "intervals": {"North": 3, "South": 4, "East": 5, "West": 4},
    },
    "North–South rush hour": {
        "initial": {"North": 45, "South": 35, "East": 10, "West": 10},
        "intervals": {"North": 2, "South": 2, "East": 5, "West": 5},
    },
    "East–West rush hour": {
        "initial": {"North": 8, "South": 12, "East": 40, "West": 35},
        "intervals": {"North": 5, "South": 5, "East": 2, "West": 2},
    },
    "Balanced traffic": {
        "initial": {"North": 20, "South": 20, "East": 20, "West": 20},
        "intervals": {"North": 4, "South": 4, "East": 4, "West": 4},
    },
}


def render_controls():
    st.sidebar.header("Traffic settings")
    scenario = st.sidebar.selectbox("Choose a scenario", list(PRESETS))
    defaults = PRESETS[scenario]
    duration = st.sidebar.slider("Simulation duration (seconds)", 60, 600, 180, 10)

    st.sidebar.subheader("Initial waiting vehicles")
    initial = {}
    for road in ROADS:
        initial[road] = st.sidebar.slider(
            road, 0, 100, defaults["initial"][road],
            key=f"initial_{scenario}_{road}",
        )

    st.sidebar.subheader("Vehicle arrival interval")
    st.sidebar.caption("Lower seconds = more vehicles arrive.")
    intervals = {}
    for road in ROADS:
        intervals[road] = st.sidebar.slider(
            f"{road} — seconds/car", 1, 15, defaults["intervals"][road],
            key=f"interval_{scenario}_{road}",
        )

    run_clicked = st.sidebar.button("Run simulation", type="primary", use_container_width=True)
    return {
        "initial_vehicles": initial,
        "arrival_intervals": intervals,
        "duration": duration,
    }, run_clicked
