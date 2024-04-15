import random
from rlcard.agents import DQNAgent
import canastaenv
import pickle
from rlcard.utils import reorganize
from agentinfo import AgentInfo
import graphing
from copy import deepcopy


def make_agents(n):
    out = []
    env = canastaenv.CanastaEnv(team_count=2, reset_score_log=True)
    for i in range(n):
        agent = DQNAgent(
            num_actions=env.num_actions,
            state_shape=env.state_shape[0],
            mlp_layers=[512, 512, 256, 256, 128, 128],
            epsilon_decay_steps=100000,
            learning_rate=0.01,
            update_target_estimator_every=1000,
            train_every=1000,
            discount_factor=1.0,
        )
        out.append((agent, (i + 1), AgentInfo(100)))
    return out


def make_agents_linear(n):
    out = []
    env = canastaenv.CanastaEnv(team_count=2, reset_score_log=True)
    for i in range(n):
        agent = DQNAgent(
            num_actions=env.num_actions,
            state_shape=env.state_shape[0],
            mlp_layers=[],
            epsilon_decay_steps=100000,
            learning_rate=0.01,
            update_target_estimator_every=1000,
            train_every=1000,
            discount_factor=1.0,
        )
        out.append((agent, (i + 1), AgentInfo(100)))
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
    for i in range(enviornment.game.playersCount):
        for ts in trajectories[i]:
            enviornment.agents[i].feed(ts)
    return payoffs, max_score


def agent_sort_key(agent):
    return agent[2].get_avg_recent_score()


def kill_bad_agents(agents, num_kill):
    new_agents = deepcopy(agents)
    new_agents = sorted(new_agents, key=agent_sort_key, reverse=True)
    replaced_nums = [
        a[1] for a in new_agents[len(new_agents) - num_kill : len(new_agents)]
    ]
    replaced_history = [
        deepcopy(a[2]) for a in new_agents[len(new_agents) - num_kill : len(new_agents)]
    ]
    new_agents = new_agents[0 : len(new_agents) - num_kill]
    for i in range(num_kill):
        new_agents.append(
            (deepcopy(agents[i][0]), replaced_nums[i], replaced_history[i])
        )
    return new_agents


def multi_agent_train(
    training_cycles, num_enviornments, graph_all=False, print_each_game=False
):
    envs = [
        canastaenv.CanastaEnv(team_count=2, reset_score_log=True)
        for _ in range(num_enviornments)
    ]
    agents = make_agents_linear(num_enviornments * 4)
    for cycle in range(1, training_cycles + 1):
        random.shuffle(agents)
        for i in range(num_enviornments):
            envs[i].set_agents([a[0] for a in agents[(i * 4) : (4 + (i * 4))]])
        output = [run_with_trajectories(env) for env in envs]
        for i in range(num_enviornments):
            payoffs, _ = output[i]
            for j in range(4):
                agents[(i * 4) + j][2].add_score(payoffs[j])
        if print_each_game:
            print("Cycle: " + str(cycle))
            for out in sorted([(agent[1], agent[2].scores[-1]) for agent in agents]):
                print(str(out[0]) + ": " + str(int(out[1])))
        if cycle % 100 == 0:
            print(cycle)
            agents = kill_bad_agents(agents, 2)
        if (graph_all and cycle % 20 == 0) or cycle == training_cycles:
            graphing.update_scores_plot(
                [
                    a[1]
                    for a in sorted(
                        [(agent[1], agent[2].get_last_scores(300)) for agent in agents]
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
    multi_agent_train(1000, 2, graph_all=True)
