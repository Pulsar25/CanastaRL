import cProfile
from rlcard.agents import DQNAgent
from rlcard.agents import RandomAgent
import canastaenv
from random import shuffle
import matplotlib.pyplot as plt
import pickle
import numpy as np
from rlcard.utils import reorganize
import multiprocessing as mp
import matplotlib
import torch

total_turns = 0

is_ipython = "inline" in matplotlib.get_backend()
if is_ipython:
    from IPython import display

env = canastaenv.CanastaEnv(resetScoreLog=True)

agent = DQNAgent(
    num_actions=env.num_actions,
    state_shape=env.state_shape[0],
    mlp_layers=[512, 512, 512, 512, 512, 512, 256, 256, 128, 128],
    epsilon_decay_steps=200000,
    learning_rate=0.01,
    train_every=1000,
    device="cuda:0",
)
agent2 = DQNAgent(
    num_actions=env.num_actions,
    state_shape=env.state_shape[0],
    mlp_layers=[512, 512, 512, 512, 512, 512, 256, 256, 128, 128],
    epsilon_decay_steps=200000,
    learning_rate=0.01,
    train_every=1000,
    device="cuda:0",
)

randomAgent = RandomAgent(
    num_actions=env.num_actions,
)

env.set_agents([agent, agent, randomAgent, agent2, randomAgent, randomAgent])
playerScoreLog = np.zeros((6,))
maxScores = []


def run_with_trajectories(_):
    global playerScoreLog
    global total_turns
    trajectories, payoffs, max_score, game_turns = env.run(is_training=True)
    # Reorganize the data to be state, action, reward, next_state, done
    trajectories = reorganize(trajectories, payoffs)
    total_turns += game_turns
    # Feed transitions into agent memory, and train the agent
    for ts in trajectories[0]:
        agent.feed(ts)
        agent2.feed(ts)
    return payoffs, max_score


def plot_durations(show_result=False):
    global maxScores
    plt.figure(1)
    durations_t = torch.tensor(maxScores, dtype=torch.float)
    if show_result:
        plt.title("Result")
    else:
        plt.clf()
        plt.title("Training...")
    plt.xlabel("Episode")
    plt.ylabel("Score")
    plt.plot(durations_t.numpy())
    # Take 100 episode averages and plot them too
    if len(durations_t) >= 100:
        means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy())

    plt.pause(0.05)  # pause a bit so that plots are updated
    if is_ipython:
        if not show_result:
            display.display(plt.gcf())
            display.clear_output(wait=True)
        else:
            display.display(plt.gcf())


def main(multithread=True):
    for episode in range(2001):
        # Generate data from the environment
        if multithread:
            with mp.Pool(10) as pool:
                output = pool.map(run_with_trajectories, range(10))
                pool.close()
                for i in output:
                    maxScores.append(i[1])
        else:
            output = run_with_trajectories(0)
            maxScores.append(output[1])

        prefix = "4episode"
        if episode % 100 == 0:
            print("Episode : " + str(episode))
            print("Total Turns: " + str(total_turns) + "\n")
            file = open("modelgen4/" + prefix + str(episode) + "model1" + ".pkl", "wb")
            pickle.dump(agent, file)
            file.close()

        shuffle(env.agents)

    plt.ion()
    plot_durations(show_result=True)
    plt.show(block=True)


if __name__ == "__main__":
    main(multithread=False)
    # cProfile.run("main(multithread=False)")
