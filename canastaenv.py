import numpy as np
from collections import OrderedDict
import envutil
from rlcard.envs import Env


class CanastaEnv(Env):
    def __init__(
        self,
        team_count,
        reset_score_log=False,
    ):
        self.name = "canasta"
        self.game = envutil.Game(team_count, 2, 13)
        super().__init__(config={"allow_step_back": False, "seed": 1023012030123})
        self.state_shape = [[138] for _ in range(self.game.playersCount)]
        self.action_shape = [None for _ in range(self.game.playersCount)]
        self.num_actions = 51
        if reset_score_log:
            self.winningScores = []
            self.playerScoreLog = [0] * self.game.playersCount

    def run(self, is_training=False):
        a, b = super().run(is_training=is_training)
        return a, b, self.get_max_score(), self.game.turns

    def get_max_score(self):
        player_scores = [
            (
                player.board.get_score()
                - player.get_hand_score()
                - player.partner.get_hand_score()
            )
            for player in self.game.players
        ]
        player_scores[self.game.turn - 1] += 100
        player_scores[
            (self.game.turn + (self.game.teamsCount - 1)) % self.game.playersCount
        ] += 100
        return max(player_scores)

    def _get_legal_actions(self):
        legal_actions = [
            i
            for i in range(self.num_actions)
            if envutil.check_legal(
                self.game.get_current_player(), self.game, envutil.num_to_move(i)
            )
        ]
        legal_actions_ids = {action_event: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)

    def _extract_state(self, state):  # 200213 don't use state ???
        output = {}
        output["obs"] = np.array(
            envutil.nodes_conversion(
                self.game.get_current_player().hand,
                self.game.get_current_player().board,
                self.game.get_current_player().game.discardPile,
                self.game.get_current_player().game.drawn,
                self.game.get_current_player(),
            )
        )
        output["legal_actions"] = self._get_legal_actions()
        output["raw_obs"] = output["obs"]
        output["raw_legal_actions"] = list(output["legal_actions"].keys())
        return output

    def get_payoffs(self):
        if not self.game.finished:
            return np.zeros((self.game.playersCount,))
        player_scores = [
            (
                player.board.get_score()
                - player.get_hand_score()
                - player.partner.get_hand_score()
            )
            for player in self.game.players
        ]
        player_scores[self.game.turn - 1] += 100
        player_scores[
            (self.game.turn + (self.game.teamsCount - 1)) % self.game.playersCount
        ] += 100
        # subtract other players scores for payoffs
        player_payoffs = [
            player_scores[i]
            - sum(
                [
                    player_scores[(i + j) % self.game.playersCount]
                    for j in range(1, self.game.teamsCount)
                ]
            )
            for i in range(self.game.playersCount)
        ]
        for i in range(self.game.playersCount):
            self.playerScoreLog[i] += player_payoffs[i]
        self.winningScores.append(max(player_scores))
        return np.array(player_payoffs)

    def _decode_action(self, action_id):
        return envutil.num_to_move(action_id)
