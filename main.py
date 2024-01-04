from rlcard.agents import DQNAgent
from rlcard.agents import RandomAgent
from rlcard.agents import NFSPAgent
import canastaenv
import pickle
import numpy as np
from rlcard.utils import reorganize
import multiprocessing as mp

env = canastaenv.CanastaEnv(resetScoreLog=True)

agent = DQNAgent(
    num_actions=env.num_actions,
    state_shape=env.state_shape[0],
    mlp_layers=[512, 512, 512, 512, 512, 512, 256, 256, 128, 128],
    epsilon_decay_steps=1000,
    learning_rate=0.01,
    train_every=1,
    device="cuda:0"
)
agent2 = DQNAgent(
    num_actions=env.num_actions,
    state_shape=env.state_shape[0],
    mlp_layers=[512, 512, 512, 512, 512, 512, 256, 256, 128, 128],
    epsilon_decay_steps=1000,
    learning_rate=0.01,
    train_every=1,
    device="cuda:0"
)

randomAgent = RandomAgent(
    num_actions=env.num_actions,
)

env.set_agents([agent,agent2,randomAgent,agent,agent2,randomAgent])
playerScoreLog = np.zeros((6,))
def runWithTrajectories(_):
    global playerScoreLog
    trajectories,payoffs = env.run(is_training=True)
    # Reorganaize the data to be state, action, reward, next_state, done
    trajectories = reorganize(trajectories, payoffs)
    # Feed transitions into agent memory, and train the agent
    for ts in trajectories[0]:
        agent.feed(ts)
        agent2.feed(ts)
    return payoffs

if __name__ == "__main__":
    for episode in range(100):
        # Generate data from the environment
        with mp.Pool(10) as pool:
            log = pool.map(runWithTrajectories, range(100))
            pool.close()
            for i in log:
                playerScoreLog += i
        print(episode, list(playerScoreLog / 100))
        playerScoreLog = [0] * 6

        file = open("episode" + str(episode) + "model1" + ".pkl", "wb")
        pickle.dump(env.agents[0], file)
        file.close()
        file = open("episode" + str(episode) + "model2" + ".pkl", "wb")
        pickle.dump(env.agents[1], file)
        file.close()
