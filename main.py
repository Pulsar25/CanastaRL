import cProfile
import random
from rlcard.agents import DQNAgent
from rlcard.agents import RandomAgent
import canastaenv
import matplotlib.pyplot as plt
import pickle
from rlcard.utils import reorganize
import multiprocessing as mp
from agentinfo import AgentInfo


def make_agents(n):
    out = []
    env = canastaenv.CanastaEnv(resetScoreLog=True)
    for i in range(n):
        agent = DQNAgent(
            num_actions=env.num_actions,
            state_shape=env.state_shape[0],
            mlp_layers=[512, 512, 256, 256, 128, 128],
            epsilon_decay_steps=400,
            learning_rate=0.01,
            update_target_estimator_every=100,
            train_every=100,
        )
        out.append((agent, (i + 1), AgentInfo()))
    return out


def save_model(model, file_name, folder_name):
    print("Saving: " + str(file_name))
    file = open("modelgen" + folder_name + "/" + file_name + ".pkl", "wb")
    pickle.dump(model, file)
    file.close()


current_plot = None
legend_labels = None
plot_title = "Agent Scores Over Different Games"

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


def run_with_trajectories(enviornment):
    trajectories, payoffs, max_score, game_turns = enviornment.run(is_training=True)
    # Reorganize the data to be state, action, reward, next_state, done
    trajectories = reorganize(trajectories, payoffs)
    # Feed transitions into agent memory, and train the agent
    for i in range(6):
        for ts in trajectories[i]:
            enviornment.agents[i].feed(ts)
    return payoffs, max_score


def multi_agent_train(training_cycles, num_enviornments, graph_all=False, print_each_game=False):
    envs = [canastaenv.CanastaEnv(resetScoreLog=True) for _ in range(num_enviornments)]
    agents = make_agents(num_enviornments * 6)
    for cycle in range(1, training_cycles + 1):
        random.shuffle(agents)
        for i in range(num_enviornments):
            envs[i].set_agents([a[0] for a in agents[(i * 6) : 6 + (i * 6)]])
        output = []
        for i in envs:
            output.append(run_with_trajectories(i))
        for i in range(num_enviornments):
            payoffs, _ = output[i]
            for j in range(6):
                agents[(i * 6) + j][2].add_score(payoffs[j])
        if print_each_game:
            print("Cycle: " + str(cycle))
            for out in sorted([(agent[1], agent[2].scores[-1]) for agent in agents]):
                print(str(out[0]) + ": " + str(int(out[1])))
        if (graph_all and cycle % 5 == 0) or cycle == training_cycles:
            update_scores_plot(
                [
                    a[1]
                    for a in sorted(
                        [(agent[1], agent[2].last_scores) for agent in agents]
                    )
                ],
                cycle == training_cycles,
            )
    while True:
        model_to_save = input("What model to save? (stop to stop) ")
        if model_to_save == "stop":
            break
        model_to_save = int(model_to_save)
        file_name = input("File name? ")
        folder_name = input("Folder name? ")
        save_model(
            [a for a in agents if a[1] == model_to_save][0][0], file_name, folder_name
        )


if __name__ == "__main__":
    multi_agent_train(100, 2,graph_all=True)
