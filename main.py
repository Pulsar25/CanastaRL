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


is_ipython = "inline" in matplotlib.get_backend()
if is_ipython:
    from IPython import display


env = canastaenv.CanastaEnv(resetScoreLog=True)

agent = DQNAgent(
    num_actions=env.num_actions,
    state_shape=env.state_shape[0],
    mlp_layers=[512, 512, 512, 512, 512, 512, 256, 256, 128, 128],
    epsilon_decay_steps=1000,
    learning_rate=0.01,
    train_every=1,
    device="cuda:0",
)
agent2 = DQNAgent(
    num_actions=env.num_actions,
    state_shape=env.state_shape[0],
    mlp_layers=[512, 512, 512, 512, 512, 512, 256, 256, 128, 128],
    epsilon_decay_steps=1000,
    learning_rate=0.01,
    train_every=1,
    device="cuda:0",
)
agent3 = DQNAgent(
    num_actions=env.num_actions,
    state_shape=env.state_shape[0],
    mlp_layers=[512, 512, 512, 512, 512, 512, 256, 256, 128, 128],
    epsilon_decay_steps=1000,
    learning_rate=0.01,
    train_every=1,
    device="cuda:0",
)
agent4 = DQNAgent(
    num_actions=env.num_actions,
    state_shape=env.state_shape[0],
    mlp_layers=[512, 512, 512, 512, 512, 512, 256, 256, 128, 128],
    epsilon_decay_steps=1000,
    learning_rate=0.01,
    train_every=1,
    device="cuda:0",
)

randomAgent = RandomAgent(
    num_actions=env.num_actions,
)

env.set_agents([agent, agent2, randomAgent, agent3, agent4, randomAgent])
playerScoreLog = np.zeros((6,))
maxScores = []


def runWithTrajectories(_):
    global playerScoreLog
    trajectories, payoffs, maxScore = env.run(is_training=True)
    # Reorganaize the data to be state, action, reward, next_state, done
    trajectories = reorganize(trajectories, payoffs)
    # Feed transitions into agent memory, and train the agent
    for ts in trajectories[0]:
        agent.feed(ts)
        agent2.feed(ts)
        agent3.feed(ts)
        agent4.feed(ts)
    return payoffs, maxScore


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
    for episode in range(1000):
        # Generate data from the environment
        if multithread:
            with mp.Pool(10) as pool:
                output = pool.map(runWithTrajectories, range(10))
                pool.close()
                for i in output:
                    maxScores.append(i[1])
        else:
            output = runWithTrajectories(0)
            maxScores.append(output[1])
        print(episode)

        file = open("3episode" + str(episode) + "model1" + ".pkl", "wb")
        pickle.dump(agent, file)
        file.close()
        file = open("3episode" + str(episode) + "model2" + ".pkl", "wb")
        pickle.dump(agent2, file)
        file.close()
        file = open("3episode" + str(episode) + "model3" + ".pkl", "wb")
        pickle.dump(agent3, file)
        file.close()
        file = open("3episode" + str(episode) + "model4" + ".pkl", "wb")
        pickle.dump(agent4, file)
        file.close()

        shuffle(env.agents)

    plt.ion()
    plot_durations(show_result=True)
    plt.show(block=True)


if __name__ == "__main__":
    main(multithread=False)
    # cProfile.run("main(multithread=False)")
