
"""Controller comparison metrics and charts."""

import pandas as pd
import streamlit as st


def render_comparison(fixed, adaptive):
    st.subheader("Fixed-time vs adaptive control")
    st.caption("Both controllers use identical initial queues, arrival intervals, and simulation duration.")

    rows = [
        ("Vehicles arrived", "arrived"),
        ("Vehicles passed", "passed"),
        ("Vehicles remaining", "remaining"),
        ("Queue-seconds", "queue_seconds"),
        ("Accrued wait per arrival (s)", "average_wait_per_arrival"),
        ("Average completed wait (s)", "average_completed_wait"),
    ]
    table = pd.DataFrame({
        "Metric": [label for label, _ in rows],
        "Fixed-time": [round(fixed[key], 2) for _, key in rows],
        "Adaptive": [round(adaptive[key], 2) for _, key in rows],
    })
    st.dataframe(table, hide_index=True, use_container_width=True)

    if fixed["queue_seconds"] > 0:
        improvement = 100 * (fixed["queue_seconds"] - adaptive["queue_seconds"]) / fixed["queue_seconds"]
        st.metric("Adaptive change in accumulated waiting", f"{improvement:+.2f}%")
        if improvement < 0:
            st.info("The adaptive controller performed worse on this scenario. That is a valid result.")
    else:
        st.info("The fixed-time controller recorded no queue waiting in this experiment.")

    st.subheader("Vehicle queues over time")
    wait_frame = pd.DataFrame({
        "Fixed-time": [point["total_waiting"] for point in fixed["history"]],
        "Adaptive": [point["total_waiting"] for point in adaptive["history"]],
    }, index=[point["time"] for point in fixed["history"]])
    wait_frame.index.name = "Simulation second"
    st.line_chart(wait_frame)

    st.subheader("Vehicles processed")
    summary_frame = pd.DataFrame({
        "Fixed-time": [fixed["passed"], fixed["remaining"]],
        "Adaptive": [adaptive["passed"], adaptive["remaining"]],
    }, index=["Passed", "Still waiting"])
    st.bar_chart(summary_frame)
    st.caption(
        "Queue-seconds are an end-of-step approximation. This educational model does not "
        "represent real Karachi traffic measurements or control live signals."
    )
