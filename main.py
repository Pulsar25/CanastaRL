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
import graphing


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
            update_target_estimator_every=1000,
            train_every=1000,
        )
        out.append((agent, (i + 1), AgentInfo()))
    return out


def save_model(model, file_name, folder_name):
    print("Saving: " + str(file_name))
    file = open("modelgen" + folder_name + "/" + file_name + ".pkl", "wb")
    pickle.dump(model, file)
    file.close()


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
        output = [run_with_trajectories(env) for env in envs]
        for i in range(num_enviornments):
            payoffs, _ = output[i]
            for j in range(6):
                agents[(i * 6) + j][2].add_score(payoffs[j])
        if print_each_game:
            print("Cycle: " + str(cycle))
            for out in sorted([(agent[1], agent[2].scores[-1]) for agent in agents]):
                print(str(out[0]) + ": " + str(int(out[1])))
        if (graph_all and cycle % 50 == 0) or cycle == training_cycles:
            graphing.update_scores_plot(
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
    multi_agent_train(2000, 2,graph_all=True)
