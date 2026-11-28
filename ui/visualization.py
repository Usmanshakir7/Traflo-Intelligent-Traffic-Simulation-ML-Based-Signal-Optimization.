
"""Draw a readable four-way intersection snapshot using Matplotlib."""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def draw_intersection(snapshot):
    """Return a Matplotlib figure for one stored simulation step."""
    signal = snapshot["signal"]
    queues = snapshot["queues"]

    fig, ax = plt.subplots(figsize=(7, 5.5))
    fig.patch.set_facecolor("#132823")
    ax.set_facecolor("#18372f")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-4.3, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")

    # Road surfaces: crossing North-South and East-West routes.
    ax.add_patch(Rectangle((-1.15, -4.3), 2.3, 8.6, color="#46515b"))
    ax.add_patch(Rectangle((-5, -1.15), 10, 2.3, color="#46515b"))
    ax.plot([0, 0], [1.25, 4.3], "--", color="#d7ca76", linewidth=1.4)
    ax.plot([0, 0], [-4.3, -1.25], "--", color="#d7ca76", linewidth=1.4)
    ax.plot([-5, -1.25], [0, 0], "--", color="#d7ca76", linewidth=1.4)
    ax.plot([1.25, 5], [0, 0], "--", color="#d7ca76", linewidth=1.4)

    # Colored car icons represent queue samples, not vehicle coordinates.
    car_locations = {
        "North": [(-0.72, 1.45 + i * 0.36) for i in range(7)],
        "South": [(0.42, -1.83 - i * 0.36) for i in range(7)],
        "West": [(-1.83 - i * 0.42, -0.75) for i in range(7)],
        "East": [(1.44 + i * 0.42, 0.46) for i in range(7)],
    }
    for road, positions in car_locations.items():
        for x, y in positions[:min(queues[road], 7)]:
            car_width, car_height = (0.34, 0.23) if road in {"East", "West"} else (0.23, 0.34)
            ax.add_patch(Rectangle((x, y), car_width, car_height,
                                   facecolor="#78c5f7", edgecolor="#d9f3ff", linewidth=0.5))

    ns_color = "#48d87b" if signal == "NS_GREEN" else "#ff6464"
    ew_color = "#48d87b" if signal == "EW_GREEN" else "#ff6464"
    for x, y, color in [(-1.42, 1.40, ns_color), (1.42, -1.40, ns_color),
                         (-1.40, -1.40, ew_color), (1.40, 1.40, ew_color)]:
        ax.add_patch(Circle((x, y), 0.16, facecolor=color, edgecolor="white", linewidth=1))

    labels = {
        "North": (0, 4.07),
        "South": (0, -4.07),
        "West": (-3.5, 1.43),
        "East": (3.5, -1.52),
    }
    for road, (x, y) in labels.items():
        ax.text(x, y, f"{road}: {queues[road]} waiting", ha="center", va="center",
                fontsize=10, fontweight="bold", color="white",
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "#223b37", "edgecolor": "none"})
    ax.text(0, 0, signal.replace("_", " "), ha="center", va="center",
            fontsize=10, fontweight="bold", color="white",
            bbox={"boxstyle": "round,pad=0.5", "facecolor": "#24323b", "edgecolor": "none"})
    fig.tight_layout(pad=0.3)
    return fig
