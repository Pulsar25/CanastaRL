import random
from rlcard.agents import DQNAgent
from rlcard.agents import RandomAgent
import canastaenv
import pickle
from rlcard.utils import reorganize
from agentinfo import AgentInfo
import graphing
from copy import deepcopy
from testing import tournament_game
import multiprocessing as mp

random_agent = RandomAgent(
    num_actions=canastaenv.CanastaEnv(team_count=2, reset_score_log=True).num_actions
)


def test_against_random(agent, games=20):
    total_diff = 0
    for i in range(games):
        scores, _ = tournament_game([agent, random_agent, agent, random_agent])
        total_diff += scores[0] - scores[1]
    return int(total_diff / games)


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
        out.append((agent, (i + 1), AgentInfo(1)))
    return out


def make_agents_linear(n, include_random=False):
    out = []
    env = canastaenv.CanastaEnv(team_count=2, reset_score_log=True)
    for i in range(n):
        if i % 4 == 3 and include_random:
            agent = RandomAgent(num_actions=env.num_actions)
            out.append((agent, (i + 1), AgentInfo(100)))
        else:
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
            if type(enviornment.agents[i]) != RandomAgent:
                enviornment.agents[i].feed(ts)
    return payoffs, max_score


def agent_sort_key(agent):
    return agent[2].get_avg_recent_score()


def kill_bad_agents(agents, num_kill):
    new_agents = deepcopy(agents)
    new_agents = sorted(new_agents, key=agent_sort_key)
    replaced_nums = []
    replaced_history = []
    for i in range(len(new_agents)):
        if new_agents[i][1] % 4 != 3:
            replaced_nums.append(new_agents[i][1])
            replaced_history.append(new_agents[i][2])
            del new_agents[i]
            i -= 1
        if len(replaced_nums) >= num_kill:
            break
    replacing_agents = []
    for i in range(len(new_agents) - 1, -1, -1):
        if new_agents[i][1] % 4 != 3:
            replacing_agents.append(i)
        if len(replacing_agents) >= num_kill:
            break
    for i in range(num_kill):
        new_agents.append(
            (
                deepcopy(agents[replacing_agents[i]][0]),
                replaced_nums[i],
                replaced_history[i],
            )
        )
    return new_agents

def multi_agent_train(
    training_cycles, num_enviornments, graph_all=False, print_each_game=False
):
    envs = [
        canastaenv.CanastaEnv(team_count=2, reset_score_log=True)
        for _ in range(num_enviornments)
    ]
    agents = make_agents_linear(num_enviornments * 4, include_random=True)
    for cycle in range(1, training_cycles + 1):
        random.shuffle(agents)
        for i in range(num_enviornments):
            envs[i].set_agents([a[0] for a in agents[(i * 4) : (4 + (i * 4))]])
        output = []
        for env in envs:
            output.append(run_with_trajectories(env))
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
        if graph_all and cycle % 100 == 0:
            """
            with mp.Pool(num_enviornments * 4) as pool_eval:
                perf_evals = pool_eval.map(
                    test_against_random, [agent[0] for agent in agents]
                )
            for i in range(len(agents)):
                agents[i][2].add_perf_eval(perf_evals[i])
            """
            graphing.update_scores_plot(
                [
                    a[1]
                    for a in sorted(
                        [(agent[1], agent[2].get_last_scores(100)) for agent in agents]
                    )
                ],
                cycle == training_cycles,
            )
    if graph_all:
        while True:
            model_to_save = input("What model to save? (stop to stop) ")
            if model_to_save == "stop":
                break
            model_to_save = int(model_to_save)
            file_name = input("File name? ")
            folder_name = input("Folder name? ")
            save_model(
                [a for a in agents if a[1] == model_to_save][0][0],
                file_name,
                folder_name,
            )
    else:
        i = 0
        for a in agents:
            save_model(a[0], "model" + str(i), "curr")
            i += 1


if __name__ == "__main__":
    multi_agent_train(50000, 2, graph_all=False)
