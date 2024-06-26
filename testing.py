import envutil
import copy
import numpy as np
import pickle
from collections import OrderedDict
import pandas as pd

n_observations = 902
n_actions = 51


def run_game(predict_function, plays):
    teams = 2
    decks = 2
    hand_size = 13
    moves_made = []
    game = envutil.Game(teams, decks, hand_size)
    game_states = [copy.deepcopy(game)]
    while True:
        chosen, _ = predict_function(game)
        chosen = envutil.num_to_move(chosen, game.players[game.turn])
        envutil.execute_move(game.players[game.turn], game, chosen)
        moves_made.append(chosen)
        game_states.append(copy.deepcopy(game))
        if game.finished or game.turns >= plays:
            if game.finished:
                print("Finished Game")
            else:
                print("Broke Game")
            break
    return game_states, moves_made


def predict(game, models=None):
    global computer_models

    if models is None:
        models = computer_models

    def get_legal_actions():
        legal_actions = [
            i
            for i in range(51)
            if envutil.check_legal(
                game.get_current_player(),
                game,
                envutil.num_to_move(i, game.players[game.turn]),
            )
        ]
        legal_actions_ids = {action_event: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)

    output = {
        "obs": np.array(
            envutil.nodes_conversion(
                game.get_current_player().hand,
                game.get_current_player().board,
                game.get_current_player().game.discardPile,
                game.get_current_player().game.drawn,
                game.get_current_player(),
            )
        ),
        "legal_actions": get_legal_actions(),
    }
    output["raw_obs"] = output["obs"]
    output["raw_legal_actions"] = list(output["legal_actions"].keys())
    prediction, q_values = models[game.turn % len(models)].eval_step(output)
    return prediction, q_values


def run_user_game():
    print()
    print("Human player will play player 1")
    teams = 2
    players_per_team = 1
    players_count = teams * players_per_team
    decks = 2
    hand_size = 13
    game = envutil.Game(teams, players_per_team, decks, hand_size)
    while True:
        print("Player " + str(game.turn + 1) + " playing")
        for p in range(players_count):
            text = ""
            if game.turn == p:
                text += "> "
            text += "P" + str(p + 1) + " Hand: "
            hand = ""
            for i in range(15):
                hand += (num_to_card(i) + " ") * game.players[p].hand[i]
            text += hand
            print(text)
        for player in range(game.teamsCount):
            text = ""
            if player == game.turn % game.teamsCount:
                text = "> "
            text += "P" + str(player + 1) + " Board: "
            for pile in game.players[player].board.canastas:
                text += (
                    "*("
                    + num_to_card(pile.cardType)
                    + ", "
                    + str(pile.count)
                    + ", "
                    + str(pile.jokers)
                    + "J, "
                    + str(pile.twos)
                    + "Twos)*  "
                )
            for pile in game.players[player].board.piles:
                text += (
                    "("
                    + num_to_card(pile.cardType)
                    + ", "
                    + str(pile.count)
                    + ", "
                    + str(pile.jokers)
                    + "J, "
                    + str(pile.twos)
                    + "Twos)  "
                )
            text += "\n" + ("Frozen" if game.frozen else "")
            print(text)
        if len(game.discardPile) > 0:
            print(num_to_card(game.discardPile[-1]))
        if game.turn % game.playersCount == 0:
            chosen = input("Enter move ")
            while chosen == "" or (
                not envutil.check_legal(game.players[0], game, chosen)
            ):
                print("Illegal Move")
                chosen = input("Enter move ")
        else:
            chosen, q_values = predict(game, models=[model1, model2, model3, model4])
            q_values = sorted(
                [
                    (q_values[i], envutil.num_to_move(i, game.players[game.turn]))
                    for i in range(len(q_values))
                ],
                reverse=True,
            )
            chosen = envutil.num_to_move(chosen, game.players[game.turn])
            print("Player " + str(game.turn + 1) + " chose " + chosen)
            text = ""
            for i in range(5):
                text += "(" + q_values[i][1] + " : " + str(q_values[i][0])[0:10] + "), "
            print(text)
            _ = input("Click enter when ready to move on")
        envutil.execute_move(game.players[game.turn % 6], game, chosen)
        print()
        if game.finished:
            print("Finished Game")
            for i in range(game.teamsCount):
                print(
                    "Player "
                    + str(i + 1)
                    + " Score: "
                    + str(
                        game.players[i].board.get_score()
                        - game.players[i].get_hand_score()
                        - game.players[(i + 2) % game.playersCount].get_hand_score()
                    )
                )
            break


def num_to_card(n):
    if n == 1:
        return "W"
    if n == 11:
        return "J"
    if n == 12:
        return "Q"
    if n == 13:
        return "K"
    if n == 14:
        return "A"
    return str(n)


def tournament_game(agent_models):
    teams = 2
    decks = 2
    hand_size = 13
    players_per_team = 1
    game = envutil.Game(teams, players_per_team, decks, hand_size)
    history = []
    while True:
        chosen, q_values = predict(game, models=agent_models)
        history.append((copy.deepcopy(game), chosen, q_values))
        chosen = envutil.num_to_move(chosen, game.players[game.turn])
        envutil.execute_move(game.players[game.turn % (teams * players_per_team)], game, chosen)
        if game.finished:
            break
    scores = []
    for i in range(teams):
        scores.append(
            game.players[i].board.get_score()
            - game.players[i].get_hand_score()
            - game.players[(i + teams) % (teams * players_per_team)].get_hand_score()
        )
    return scores, history


def tournament(games, files):
    agent_models = []
    for model_file in files:
        model_file = open(model_file, "rb")
        loaded_model = pickle.load(model_file)
        model_file.close()
        agent_models.append(loaded_model)
    total_scores = [0] * 2
    for i in range(games):
        results, _ = tournament_game(agent_models)
        for j in range(2):
            total_scores[j] += results[j]
    for j in range(2):
        total_scores[j] /= games
    print("Final Avg Scores: " + str(total_scores))


# 0-13 discard Pile
# 14-97 players hands 1-14
# 98-103 board (dirty,clean)
# 104-202 boards 3 boards, 11 cards, card count, two count j count
# 203 turn
def get_output_lables():
    out = []
    for i in range(1, 15):
        out.append("discardPile" + str(i))
    for i in range(1, 5):
        for j in range(1, 15):
            out.append("player" + str(i) + "cardNum" + str(j))
    for i in range(1, 3):
        out.append("board" + str(i) + "dirties")
        out.append("board" + str(i) + "cleans")
    for i in range(1, 3):
        for j in range(4, 15):
            out.append("board" + str(i) + "pile" + str(j) + "cardcount")
            out.append("board" + str(i) + "pile" + str(j) + "twos")
            out.append("board" + str(i) + "pile" + str(j) + "jokers")
    out.append("turn")
    out.append("total_turns")
    out.append("move")
    out.append("finalscores1")
    out.append("finalscores2")
    for i in range(1, 61):
        out.append("q_value" + str(i))
    return out


output_labels = get_output_lables()


def game_to_data(game: envutil.Game) -> [int]:
    output = []
    discard_pile = game.discardPile
    for i in range(14):
        output.append(0)
    for card in discard_pile:
        output[card - 2] += 1
    for player in game.players:
        for i in range(1, 15):
            output.append(player.hand[i])
    for board in game.boards:
        dirty_count = 0
        clean_count = 0
        for canasta in board.canastas:
            if canasta.is_dirty:
                dirty_count += 1
            else:
                clean_count += 1
        output.append(dirty_count)
        output.append(clean_count)
    curr = len(output)
    for i in range(66):
        output.append(0)
    for board_i in range(len(game.boards)):
        for pile in game.boards[board_i].canastas + game.boards[board_i].piles:
            output[curr + 33 * board_i + 3 * (pile.cardType - 4)] = pile.count
            output[curr + 33 * board_i + 3 * (pile.cardType - 4) + 1] = pile.twos
            output[curr + 33 * board_i + 3 * (pile.cardType - 4) + 2] = pile.jokers
    output.append(game.turn % 6)
    output.append(game.turns)
    return output


def get_data(games, files):
    agent_models = []
    for model_file in files:
        model_name = model_file
        model_file = open(model_file, "rb")
        loaded_model = pickle.load(model_file)
        model_file.close()
        agent_models.append(loaded_model)
        print(model_name + " " + str(type(loaded_model)))
    data = []
    output = [tournament_game(agent_models=agent_models) for _ in range(games)]
    for i in output:
        scores, history = i
        for state, move, q_values in history:
            data.append(game_to_data(state) + [move] + scores + list(q_values))
    return data


def export_to_csv(games, files, filepath):
    global output_labels
    data = get_data(games, files)
    df = pd.DataFrame(data, columns=output_labels)
    df.to_csv(filepath, index=False)


if __name__ == "__main__":
    file = open("modelgencurr/model0.pkl", "rb")
    model1 = pickle.load(file)
    file.close()
    file = open("modelgencurr/model0.pkl", "rb")
    model2 = pickle.load(file)
    file.close()
    file = open("modelgencurr/model0.pkl", "rb")
    model3 = pickle.load(file)
    file.close()
    file = open("modelgencurr/model0.pkl", "rb")
    model4 = pickle.load(file)
    file.close()

    computer_models = [model1, model1, model1, model1, model1, model1]
    #run_user_game()
    export_to_csv(
        300,
        [
            "modelgencurr/model0.pkl",
            "modelgencurr/model2.pkl",
            "modelgencurr/model0.pkl",
            "modelgencurr/model2.pkl",
        ],
        "testoutput43.csv",
    )
    export_to_csv(
        300,
        [
            "modelgencurr/model3.pkl",
            "modelgencurr/model4.pkl",
            "modelgencurr/model3.pkl",
            "modelgencurr/model4.pkl",
        ],
        "testoutput44.csv",
    )
