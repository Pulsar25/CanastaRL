import matplotlib.pyplot as plt

current_plot = None
legend_labels = None
plot_title = "Agent Scores VS Random Agent"

custom_colors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#FF1493",
    "#00CED1",
    "#008B8B",
    "#556B2F",
    "#800000",
    "#8B008B",
    "#483D8B",
    "#00FA9A",
]


def update_scores_plot(agent_scores, last=False):
    global current_plot, legend_labels, custom_colors
    if current_plot is None:
        current_plot, ax = plt.subplots(figsize=(10, 6))
        for i, scores in enumerate(agent_scores):
            color = custom_colors[i % len(custom_colors)]
            ax.plot(
                range(1, len(scores) + 1), scores, label=f"Agent {i + 1}", color=color
            )
        ax.set_title(plot_title)
        ax.set_xlabel("Game Number")
        ax.set_ylabel("Score")
        ax.legend(loc="upper left")  # Set legend location to the upper left
        ax.grid(True)
        legend_labels = [f"Agent {i + 1}" for i in range(len(agent_scores))]
        plt.pause(0.1)
    else:
        ax = current_plot.get_axes()[0]
        ax.clear()
        for i, scores in enumerate(agent_scores):
            color = custom_colors[i % len(custom_colors)]
            ax.plot(
                range(1, len(scores) + 1), scores, label=legend_labels[i], color=color
            )
        ax.legend(loc="upper left")  # Set legend location to the upper left
        ax.set_title(plot_title)
        ax.grid(True)
        # Adjust the plot limits if needed
        ax.relim()
        ax.autoscale_view()

    # Draw the updated plot without bringing it to the front
    if last:
        plt.show(block=False)
    else:
        plt.draw()

    # Pause to allow time for the plot to be updated
    plt.pause(0.05)
