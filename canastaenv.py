import numpy as np
from collections import OrderedDict
import envutil
from rlcard.envs import Env

class CanastaEnv(Env):
    def __init__(self,resetScoreLog=False):
        self.name = 'canasta'
        self.game = envutil.Game(3,3,13)
        super().__init__(config={'allow_step_back' : False,'seed' : 1023012030123})
        self.state_shape = [[231] for _ in range(self.game.playersCount)]
        self.action_shape = [None for _ in range(self.game.playersCount)]
        self.num_actions = 51
        if resetScoreLog:
            self.winningScores = []
            self.playerScoreLog = [0] * 6

    def getMaxScore(self):
        playerScores = [(player.board.getScore() - player.getHandScore() - player.partner.getHandScore()) for player in self.game.players]
        playerScores[self.game.turn - 1] += 100
        playerScores[(self.game.turn + 2) % 6] += 100
        return max(playerScores[0],playerScores[1])

    def _get_legal_actions(self):
        legal_actions = [i for i in range(51) if envutil.checkLegal(self.game.get_current_player(),self.game,envutil.numToMove(i))]
        legal_actions_ids = {action_event: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)

    def _extract_state(self, state):  # 200213 don't use state ???
        output = {}
        output['obs'] = np.array(envutil.nodesConversion(self.game.get_current_player().hand,self.game.get_current_player().board,self.game.get_current_player().game.discardPile,self.game.get_current_player().game.drawn,self.game.get_current_player()))
        output['legal_actions'] = self._get_legal_actions()
        output['raw_obs'] = output['obs']
        output['raw_legal_actions'] = list(output['legal_actions'].keys())
        return output

    def get_payoffs(self):
        if not self.game.finished:
            return np.zeros((6,))
        playerScores = [(player.board.getScore() - player.getHandScore() - player.partner.getHandScore()) for player in self.game.players]
        playerScores[self.game.turn-1] += 100
        playerScores[(self.game.turn+2) % 6] += 100
        playerPayoffs = [(playerScores[i] * 3) - playerScores[(i + 1) % 6] - playerScores[(i+2) % 6] for i in range(6)]
        for i in range(6):
            self.playerScoreLog[i] += playerPayoffs[i]
        self.winningScores.append(max(playerScores[0],playerScores[1]))
        return np.array(playerPayoffs)

    def _decode_action(self, action_id):
        return envutil.numToMove(action_id)
