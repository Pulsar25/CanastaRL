import envutil
import copy
import numpy as np
import pickle
from collections import OrderedDict
from rlcard.agents import RandomAgent


def runGame(predictfunction,plays,models):
    teams = 3
    decks = 3
    handSize = 13
    game = envutil.Game(teams,decks,handSize)
    while True:
        chosen = predictfunction(game,models)
        chosen = envutil.numToMove(chosen)
        envutil.execute_move(game.players[game.turn], game, chosen)
        if game.finished or game.turns >= plays:
            if not game.finished:
                print("Time Out Finish")
            break
    return game

def predict(game,models):
    def _get_legal_actions():
        legal_actions = [i for i in range(50) if envutil.checkLegal(game.get_current_player(),game,envutil.numToMove(i))]
        legal_actions_ids = {action_event: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)
    output = {}
    output['obs'] = np.array(
        envutil.nodesConversion(game.get_current_player().hand, game.get_current_player().board,
                                game.get_current_player().game.discardPile,
                                game.get_current_player().game.drawn, game.get_current_player()))
    output['legal_actions'] = _get_legal_actions()
    output['raw_obs'] = output['obs']
    output['raw_legal_actions'] = list(output['legal_actions'].keys())
    prediction = (models[game.turn].step(output,testing=True))
    return prediction

def runTournamnet(models,rounds):
    avgScores = [0] * 6
    avgTurns = 0
    for round in range(rounds):
        finalState = runGame(predict,1000,models)
        for p in range(6):
            avgScores[p] += finalState.players[p].board.getScore() - finalState.players[p].getHandScore() - finalState.players[(p+3) % 6].getHandScore()
        avgTurns += finalState.turns
    for i in range(6):
        avgScores[i] /= rounds
    avgTurns /= rounds
    return avgScores,avgTurns / 6

file = open("3pmodel20.pkl", "rb")
mainModel = pickle.load(file)
file.close()

randomAgent = RandomAgent(num_actions=51)

print(runTournamnet([mainModel,randomAgent,mainModel,mainModel,randomAgent,randomAgent],200))


