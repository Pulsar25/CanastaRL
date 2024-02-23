import cProfile
import random
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
from agentinfo import AgentInfo
import torch

total_turns = 0

is_ipython = "inline" in matplotlib.get_backend()
if is_ipython:
    from IPython import display

env = canastaenv.CanastaEnv(resetScoreLog=True)


def make_agents(n):
    out = []
    for i in range(n):
        agent = DQNAgent(
            num_actions=env.num_actions,
            state_shape=env.state_shape[0],
            mlp_layers=[512, 512, 256, 256, 128, 128],
            epsilon_decay_steps=6000000,
            learning_rate=0.01,
            train_every=10000,
            device="cuda:0"
        )
        out.append((agent,(i+1),AgentInfo()))
    return out

def run_with_trajectories(enviornment):
    trajectories, payoffs, max_score, game_turns = enviornment.run(is_training=True)
    # Reorganize the data to be state, action, reward, next_state, done
    trajectories = reorganize(trajectories, payoffs)
    # Feed transitions into agent memory, and train the agent
    for i in range(6):
        for ts in trajectories[i]:
            enviornment.agents[i].feed(ts)
    return payoffs, max_score


def multi_agent_train(training_cycles, num_enviornments):
    envs = [canastaenv.CanastaEnv(resetScoreLog=True) for _ in range(num_enviornments)]
    agents = make_agents(num_enviornments * 6)
    for cycle in range(1,training_cycles+1):
        random.shuffle(agents)
        for i in range(num_enviornments):
            envs[i].set_agents([a[0] for a in agents[(i * 6) : 6 + (i * 6)]])
        with mp.Pool(num_enviornments) as pool:
            output = pool.map(run_with_trajectories, envs)
        for i in range(num_enviornments):
            payoffs, _ = output[i]
            for j in range(6):
                agents[(i * 6) + j][2].addScore(payoffs[j])
        print("Cycle: " + str(cycle))

"""
def normal_train(multithread=True):
    global env
    env.set_agents([agent, agent, randomAgent, agent2, randomAgent, randomAgent])
    for episode in range(100001):
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
        if episode % 10000 == 0:
            print("Episode : " + str(episode))
            print("Total Turns: " + str(total_turns) + "\n")
            file = open("modelgen6/" + prefix + str(episode) + "model1" + ".pkl", "wb")
            pickle.dump(agent, file)
            file.close()

        shuffle(env.agents)

    plt.ion()
    plot_durations(show_result=True)
    plt.show(block=True)
"""

if __name__ == "__main__":
    multi_agent_train(10000, 3)
    # cProfile.run("main(multithread=False)")
