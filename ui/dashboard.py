"""Comparison dashboard for fixed-time, rule-based, and ML controllers."""
import pandas as pd
import streamlit as st

CONTROLLER_NAMES = {
    "fixed": "Fixed-Time",
    "adaptive": "Rule-Based",
    "ml": "ML-Assisted",
}


def render_comparison(results):
    st.subheader("Controller comparison")
    st.caption(
        "All controllers use identical initial traffic, "
        "arrival intervals, and simulation duration."
    )
    metrics = [
        ("Vehicles arrived", "arrived"),
        ("Vehicles passed", "passed"),
        ("Vehicles still waiting", "remaining"),
        ("Total queue-seconds", "queue_seconds"),
        ("Accrued wait per arrival (s)", "average_wait_per_arrival"),
        ("Completed vehicle wait (s)", "average_completed_wait"),
    ]
    records = []
    for label, metric in metrics:
        record = {"Metric": label}
        for key, name in CONTROLLER_NAMES.items():
            record[name] = round(results[key][metric], 2)
        records.append(record)

    st.dataframe(pd.DataFrame(records), hide_index=True, use_container_width=True)

    fixed_wait = results["fixed"]["queue_seconds"]
    if fixed_wait > 0:
        col1, col2 = st.columns(2)
        for column, key in ((col1, "adaptive"), (col2, "ml")):
            improvement = (
                100 * (fixed_wait - results[key]["queue_seconds"]) / fixed_wait
            )
            column.metric(
                f"{CONTROLLER_NAMES[key]} vs fixed",
                f"{improvement:+.2f}%",
            )
        st.caption("Positive improvement means less queue waiting than fixed-time control.")
    else:
        st.info("Fixed-time recorded no waiting; percentage improvement is undefined.")

    st.subheader("Waiting vehicles during the simulation")
    times = [point["time"] for point in results["fixed"]["history"]]
    queues = pd.DataFrame({
        name: [point["total_waiting"] for point in results[key]["history"]]
        for key, name in CONTROLLER_NAMES.items()
    }, index=times)
    queues.index.name = "Simulation second"
    st.line_chart(queues)

    st.subheader("Processed vs remaining vehicles")
    counts = pd.DataFrame({
        name: [results[key]["passed"], results[key]["remaining"]]
        for key, name in CONTROLLER_NAMES.items()
    }, index=["Passed", "Remaining"])
    st.bar_chart(counts)

    decisions = results["ml"].get("decisions", [])
    if decisions:
        st.subheader("ML timing decisions per cycle")
        st.dataframe(pd.DataFrame(decisions), hide_index=True, use_container_width=True)
        st.caption("Predictions estimate waiting over one cycle, not the entire simulation.")

    st.caption(
        "Synthetic traffic conditions. Accumulated waiting is an end-of-step "
        "approximation; results do not establish real-world traffic performance."
    )
