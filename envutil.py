from collections import defaultdict
import copy
import random
from typing import List


def get_card_count(i):
    if i == 1:
        return 50
    if i == 2 or i == 14:
        return 20
    if i <= 7:
        return 5
    if i <= 13:
        return 10
    return 0


def generate_deck():
    out = [1, 1, 2, 2, 2, 2, 3, 3, 15, 15]
    for i in range(4, 15):
        out += 4 * [i]
    return out


# Game Classes:


class BoardStack:
    cardType = None
    jokers = None
    twos = None
    count = None

    def __init__(self, card_type, count):
        self.cardType = card_type
        self.count = 0
        self.count = count
        self.jokers = 0
        self.twos = 0

    def get_score(self):
        return (
            self.jokers * 50
            + self.twos * 20
            + self.count * get_card_count(self.cardType)
        )

    def is_dirty(self):
        return not (self.twos == 0 and self.jokers == 0)

    def get_total_count(self):
        return self.jokers + self.twos + self.count

    def get_card_type(self):
        return self.cardType

    def __str__(self):
        return (
            "("
            + str(self.cardType)
            + ", "
            + str(self.count)
            + " count, "
            + str(self.jokers)
            + " jokers, "
            + str(self.twos)
            + " twos)"
        )


class Board:
    redThrees = None
    piles = None
    canastas = None

    def __init__(self):
        self.redThrees = 0
        self.piles = []
        self.canastas = []
        self.players = []

    def set_players(self, players):
        self.players = players

    def get_score(self, include_red_threes=False):
        out = 0
        if include_red_threes:
            if len(self.piles) == 0 and len(self.canastas) == 0:
                out -= 100 * self.redThrees
            else:
                out += 100 * self.redThrees
        for pile in self.piles:
            out += pile.get_score()
        for player in self.players:
            out -= player.get_hand_score()
        for canasta in self.canastas:
            out += canasta.get_score()
            if not canasta.is_dirty():
                out += 200
            out += 300
        return out

    def __str__(self):
        out = "(" + str(self.redThrees) + "Red 3s, Canastas: "
        for canasta in self.canastas:
            out += str(canasta) + " "
        out += "Piles: "
        for pile in self.piles:
            out += str(pile) + " "
        out += ")"
        return out


class Player:
    def __init__(self, hand, game, board):
        self.hand = defaultdict(int)
        for card in hand:
            self.hand[card] += 1
        self.board = board
        self.game = game
        self.knowledge = [defaultdict(int) for _ in range(game.playersCount - 1)]
        self.partners = []
        self.team = None

    def get_hand_size(self):
        out = 0
        for i in range(1, 15):
            out += self.hand[i]
        return out

    def get_hand_score(self):
        out = 0
        for i in self.hand:
            out += self.hand[i] * get_card_count(i)
        if out == 0:
            out = -100
        return out

    def __str__(self):
        out = ""
        for i in range(1, 15):
            out += "(" + str(i) + ", " + str(self.hand[i]) + ")"
        return out


class Team:
    players = []
    score = 0
    board = None


class Game:
    def draw(self):
        if len(self.drawPile) == 0:
            self.finished = True
            return 4  # apprently we give them a 4 when its over
        return self.drawPile.pop()

    def get_num_players(self):
        return self.playersCount

    def get_num_actions(self):
        return 51

    def init_game(self):
        self.reset()
        return (
            nodes_conversion(
                self.players[0].hand,
                self.players[0].board,
                self.discardPile,
                self.drawn,
                self.players[0],
            ),
            0,
        )

    def is_over(self):
        return self.finished

    def get_player_id(self):
        return self.turn % self.playersCount

    def get_state(self, player_id):
        return nodes_conversion(
            self.players[player_id].hand,
            self.players[player_id].board,
            self.discardPile,
            self.drawn,
            self.players[player_id],
        )

    def step(self, action):
        execute_move(self.players[self.get_player_id()], self, action)
        return (
            nodes_conversion(
                self.players[self.turn % self.playersCount].hand,
                self.players[self.turn % self.playersCount].board,
                self.discardPile,
                self.drawn,
                self.players[self.turn % self.playersCount],
            ),
            self.turn % self.playersCount,
        )

    def __init__(self, teams, players_per_team, decks, hand_size):
        self.allow_step_back = False
        self.discardPile = []
        self.drawPile = []
        self.teams = []
        self.teamsCount = teams
        self.playersPerTeam = players_per_team
        self.decks = decks
        self.boards = []
        self.players: List[Player] = [None] * (teams * players_per_team)
        self.playersCount = teams * players_per_team
        self.teamsCount = teams
        self.turns = 0
        self.handSize = hand_size
        self.drawn = False
        self.frozen = False
        self.turn = 0
        self.finished = False
        for k in range(decks):
            self.drawPile += generate_deck()
        random.shuffle(self.drawPile)
        self.discardPile.append(self.draw())
        for i in range(teams):
            player_hands = []
            for _ in range(players_per_team):
                hand = []
                for _ in range(hand_size):
                    hand.append(self.draw())
                player_hands.append(hand)
            board = Board()
            team = Team()
            players = []
            for j in range(players_per_team):
                players.append(Player(player_hands[j], self, board))
            for j in range(players_per_team):
                players[j].game = self
                players[j].team = team
                other_players = []
                for k in range(players_per_team):
                    if k != j:
                        other_players.append(players[k])
                players[j].partners = other_players
            board.set_players(players)
            team.players = players
            team.board = board
            self.teams.append(team)
            self.boards.append(board)
            for j in range(players_per_team):
                self.players[i + teams * j] = players[j]

    def reset(self):
        self.discardPile = []
        self.drawPile = []
        self.teams = []
        self.boards = []
        self.players: List[Player] = [None] * self.playersCount
        self.turns = 0
        self.drawn = False
        self.frozen = False
        self.turn = 0
        self.finished = False
        for k in range(self.decks):
            self.drawPile += generate_deck()
        random.shuffle(self.drawPile)
        self.discardPile.append(self.draw())
        for i in range(self.teamsCount):
            player_hands = []
            for _ in range(self.playersPerTeam):
                hand = []
                for _ in range(self.handSize):
                    hand.append(self.draw())
                player_hands.append(hand)
            board = Board()
            team = Team()
            players = []
            for j in range(self.playersPerTeam):
                players.append(Player(player_hands[j], self, board))
            for j in range(self.playersPerTeam):
                players[j].game = self
                players[j].team = team
                other_players = []
                for k in range(self.playersPerTeam):
                    if k != j:
                        other_players.append(players[k])
                players[j].partners = other_players
            board.set_players(players)
            team.players = players
            team.board = board
            self.teams.append(team)
            self.boards.append(board)
            for j in range(self.playersPerTeam):
                self.players[i + self.teamsCount * j] = players[j]

    def get_current_player(self):
        return self.players[self.turn % self.playersCount]

    def __str__(self):
        out = ""
        for i in range(self.teamsCount * 2):
            out += str(self.players[i]) + " " + str(self.players[i].board) + "\n"
        out += str(self.discardPile) + "\n"
        out += str(self.turn)
        return out


# 4,5,6,7,8,9,10,11,12,13,14
# 1st most common, 2nd most common, etc.
def get_transposition_tables(player):
    sorted_hand = []
    for i in range(4, 15):
        sorted_hand.append((player.hand[i], i))
    sorted_hand = sorted(sorted_hand)
    transposition_pos_to_card = {(i + 1): sorted_hand[i][1] for i in range(11)}
    transposition_card_to_pos = {sorted_hand[i][1]: (i + 1) for i in range(11)}
    return transposition_pos_to_card, transposition_card_to_pos


def check_legal(player: Player, game, move):
    while player.hand[15] > 0:
        player.board.redThrees += 1
        player.hand[15] -= 1
        player.hand[game.draw()] += 1
    hand_size = 0
    for i in range(1, 15):
        hand_size += player.hand[i]
    if move == "goOut":
        return (
            game.drawn
            and len(player.board.canastas) >= 2
            and hand_size - player.hand[3] == 1
            and (player.hand[3] >= 3 or player.hand[3] == 0)
        )
    elif move == "15":
        return False
    elif move == "d15":
        return False
    elif move == "wild215":
        return False
    elif move == "wildJ15":
        return False
    elif move == "pickupPileJ":
        if game.drawn:
            return False
        if len(game.discardPile) == 0:
            return False
        for i in player.board.piles:
            if (
                i.cardType == game.discardPile[-1]
                and hand_size + len(game.discardPile) - 1 >= 2
                and (not game.frozen)
            ):
                return True
        if hand_size <= 3 and len(game.discardPile) == 1:
            return False
        if hand_size <= 2 and len(game.discardPile) == 2:
            return False
        if game.discardPile[-1] < 4:
            return False
        if game.frozen or len(player.board.piles) + len(player.board.canastas) == 0:
            return player.hand[game.discardPile[-1]] >= 2
        return (
            (not game.frozen)
            and player.hand[1] >= 1
            and player.hand[game.discardPile[-1]] >= 1
        ) or player.hand[game.discardPile[-1]] >= 2
    elif move == "pickupPile2":
        if game.drawn:
            return False
        if len(game.discardPile) == 0:
            return False
        for i in player.board.piles:
            if (
                i.cardType == game.discardPile[-1]
                and hand_size >= 2
                and (not game.frozen)
            ):
                return True
        if hand_size <= 3 and len(game.discardPile) == 1:
            return False
        if hand_size <= 2 and len(game.discardPile) == 2:
            return False
        if game.discardPile[-1] < 4:
            return False
        if game.frozen or len(player.board.piles) + len(player.board.canastas) == 0:
            return player.hand[game.discardPile[-1]] >= 2
        return (
            (not game.frozen)
            and player.hand[2] >= 1
            and player.hand[game.discardPile[-1]] >= 1
        ) or player.hand[game.discardPile[-1]] >= 2
    elif move[0] == "w" and move[4] == "J":
        if not game.drawn:
            return False
        played_card = int(move[5:])
        if played_card <= 3:
            return False
        if hand_size <= 2 and len(player.board.canastas) < 2:
            if len(player.board.canastas) == 1:
                for pile in player.board.piles:
                    if pile.cardType == played_card and pile.get_total_count() == 6:
                        return (
                            hand_size == 2
                            and player.hand[1] >= 1
                            and pile.twos + pile.jokers + 1 <= pile.count
                        )
            return False
        if hand_size == 1:
            return False
        if player.hand[1] <= 0:
            return False
        for pile in player.board.piles:
            if pile.cardType == played_card:
                return pile.twos + pile.jokers + 1 <= pile.count
        return False
    elif move[0] == "w" and move[4] == "2":
        if not game.drawn:
            return False
        played_card = int(move[5:])
        if played_card <= 3:
            return False
        if hand_size <= 2 and len(player.board.canastas) < 2:
            if len(player.board.canastas) == 1:
                for pile in player.board.piles:
                    if pile.cardType == played_card and pile.get_total_count() == 6:
                        return (
                            hand_size == 2
                            and player.hand[2] >= 1
                            and pile.twos + pile.jokers + 1 <= pile.count
                        )
            return False
        if hand_size == 1:
            return False
        if player.hand[2] <= 0:
            return False
        for pile in player.board.piles:
            if pile.cardType == played_card:
                return pile.twos + pile.jokers + 1 <= pile.count
        return False
    elif move == "pickup":
        return not game.drawn
    elif move[0] == "d":
        if not game.drawn:
            return False
        played_card = int(move[1::])
        if player.hand[played_card] <= 0:
            return False
        return len(player.board.canastas) >= 2 or hand_size > 1
    else:
        played_card = int(move)
        if played_card <= 3:
            return False
        if (
            (not game.drawn)
            or hand_size == 1
            or (
                hand_size == 2
                and len(player.board.canastas) < 2
                and not (
                    len(player.board.canastas) == 1
                    and len(
                        [p for p in player.board.piles if p.cardType == played_card]
                    )
                    > 0
                    and [p for p in player.board.piles if p.cardType == played_card][
                        0
                    ].get_total_count()
                    == 6
                )
            )
        ):
            return False
        if player.hand[played_card] == 0:
            return False
        for pile in player.board.piles:
            if pile.cardType == played_card:
                return True
        for pile in player.board.canastas:
            if pile.cardType == played_card:
                return True
        if player.hand[played_card] >= 3 or (
            player.hand[played_card] == 2 and player.hand[1] + player.hand[2] >= 1
        ):
            return hand_size > 4 or (hand_size > 3 and len(player.board.canastas) >= 2)
        return False


def num_to_move(num, player):
    transposition_pos_to_card, _ = get_transposition_tables(player)
    if num <= 10:
        return str(transposition_pos_to_card[num + 1])
    if num == 11:
        return "d1"
    if num == 12:
        return "d2"
    if num == 13:
        return "d3"
    if num <= 24:
        return "d" + str(transposition_pos_to_card[num - 13])
    if num == 25:
        return "pickupPileJ"
    if num == 26:
        return "pickupPile2"
    if num == 27:
        return "pickup"
    if num <= 38:
        return "wildJ" + str(transposition_pos_to_card[num - 27])
    if num <= 49:
        return "wild2" + str(transposition_pos_to_card[num - 38])
    if num == 50:
        return "goOut"


def move_to_num(move, player):
    _, transposition_card_to_pos = get_transposition_tables(player)
    if move == "goOut":
        return 50
    if move == "pickupPile2":
        return 26
    if move == "pickupPileJ":
        return 25
    if move == "pickup":
        return 27
    if len(move) >= 5 and move[4] == "J":
        return transposition_card_to_pos[int(move[5::])] + 27
    if len(move) >= 5 and move[4] == "2":
        return transposition_card_to_pos[int(move[5::])] + 38
    if move == "d1":
        return 11
    if move == "d2":
        return 12
    if move == "d3":
        return 13
    if move[0] == "d":
        return transposition_card_to_pos[int(move[1::])] + 13
    return transposition_card_to_pos[int(move)] - 4


def execute_move(player: Player, game: Game, move):
    if game.turns >= 360:
        game.finished = True
    knowledge_update = defaultdict(int)
    while player.hand[15] > 0:
        player.board.redThrees += 1
        player.hand[15] -= 1
    if move == "goOut":
        card = 0
        for i in range(4, 15):
            if player.hand[i] == 1:
                card = i
                break
        game.discardPile.append(card)
        player.hand[card] -= 1
        knowledge_update[card] -= 1
        game.turn += 1
        game.turns += 1
        game.turn = game.turn % game.playersCount
        game.drawn = False
        if int(card) <= 2:
            game.frozen = True
        player.hand[3] = 0
        game.finished = True
    elif move == "pickupPileJ":
        game.drawn = True
        done = False
        for pile in player.board.piles:
            if pile.cardType == game.discardPile[-1]:
                pile.count += 1
                done = True
                break
        if not done:
            if player.hand[game.discardPile[-1]] >= 2:
                player.hand[game.discardPile[-1]] -= 2
                knowledge_update[game.discardPile[-1]] -= 2
                player.board.piles.append(BoardStack(game.discardPile[-1], 3))
            else:
                player.hand[game.discardPile[-1]] -= 1
                player.hand[1] -= 1
                knowledge_update[1] -= 1
                knowledge_update[game.discardPile[-1]] -= 1
                new_stack = BoardStack(game.discardPile[-1], 2)
                new_stack.jokers += 1
                player.board.piles.append(new_stack)
        for card in game.discardPile:
            player.hand[card] += 1
            knowledge_update[card] += 1
        player.hand[player.game.discardPile[-1]] -= 1
        knowledge_update[player.game.discardPile[-1]] -= 1
        game.frozen = False
        game.discardPile = []
    elif move == "pickupPile2":
        game.drawn = True
        done = False
        for pile in player.board.piles:
            if pile.cardType == game.discardPile[-1]:
                pile.count += 1
                done = True
                break
        if not done:
            if player.hand[game.discardPile[-1]] >= 2:
                player.hand[game.discardPile[-1]] -= 2
                knowledge_update[game.discardPile[-1]] -= 2
                player.board.piles.append(BoardStack(game.discardPile[-1], 3))
            else:
                player.hand[game.discardPile[-1]] -= 1
                knowledge_update[game.discardPile[-1]] -= 1
                player.hand[2] -= 1
                knowledge_update[2] -= 1
                new_stack = BoardStack(game.discardPile[-1], 2)
                new_stack.twos += 1
                player.board.piles.append(new_stack)
        for card in game.discardPile:
            player.hand[card] += 1
            knowledge_update[card] += 1
        player.hand[player.game.discardPile[-1]] -= 1
        knowledge_update[player.game.discardPile[-1]] -= 1
        game.frozen = False
        game.discardPile = []
    elif move[0] == "w" and move[4] == "J":
        player.hand[1] -= 1
        knowledge_update[1] -= 1
        for pile in player.board.piles:
            if int(move[5::]) == pile.cardType:
                pile.jokers += 1
                break
    elif move[0] == "w" and move[4] == "2":
        player.hand[2] -= 1
        knowledge_update[2] -= 1
        for pile in player.board.piles:
            if int(move[5::]) == pile.cardType:
                pile.twos += 1
                break
    elif move == "pickup":
        game.drawn = True
        new_card = game.draw()
        while new_card == 15:
            player.board.redThrees += 1
            new_card = game.draw()
        player.hand[new_card] += 1
    elif move[0] == "d":
        game.discardPile.append(int(move[1::]))
        player.hand[int(move[1::])] -= 1
        knowledge_update[int(move[1::])] -= 1
        game.turn += 1
        game.turns += 1
        game.turn = game.turn % game.playersCount
        game.drawn = False
        if int(move[1::]) <= 2:
            game.frozen = True
    else:
        done = False
        for pile in player.board.piles:
            if pile.cardType == int(move):
                pile.count += 1
                player.hand[int(move)] -= 1
                knowledge_update[int(move)] -= 1
                done = True
                break
        if not done:
            for pile in player.board.canastas:
                if pile.cardType == int(move):
                    pile.count += 1
                    player.hand[int(move)] -= 1
                    knowledge_update[int(move)] -= 1
                    done = True
                    break
        if not done:
            if player.hand[int(move)] >= 3:
                player.hand[int(move)] -= 3
                knowledge_update[int(move)] -= 3
                player.board.piles.append(BoardStack(int(move), 3))
            else:
                if player.hand[1] >= 1:
                    player.hand[int(move)] -= 2
                    player.hand[1] -= 1
                    knowledge_update[int(move)] -= 2
                    knowledge_update[1] -= 1
                    new_pile = BoardStack(int(move), 2)
                    new_pile.jokers += 1
                    player.board.piles.append(new_pile)
                else:
                    player.hand[int(move)] -= 2
                    player.hand[2] -= 1
                    knowledge_update[int(move)] -= 2
                    knowledge_update[2] -= 1
                    new_pile = BoardStack(int(move), 2)
                    new_pile.twos += 1
                    player.board.piles.append(new_pile)
    if len(player.board.piles) > 0:
        i = 0
        for j in range(len(player.board.piles)):
            if player.board.piles[i].get_total_count() >= 7:
                player.board.canastas.append(copy.deepcopy(player.board.piles[i]))
                del player.board.piles[i]
                i -= 1
            i += 1
    while player.hand[15] > 0:
        player.board.redThrees += 1
        player.hand[15] -= 1
    start = 0
    for i in game.players:
        if i == player:
            break
        start += 1
    for i in range(game.playersCount - 1):
        for j in range(1, 15):
            game.players[(start + i + 1) % game.playersCount].knowledge[
                game.playersCount - 2 - i
            ][j] += knowledge_update[j]
    hand_size = 0
    for i in range(1, 15):
        hand_size += player.hand[i]
    if hand_size == 0:
        game.finished = True


def nodes_conversion(hand, board, discard_pile, drawn, player):
    return nodes_conversion_linear(hand, board, discard_pile, drawn, player)


def nodes_conversion_non_linear(hand, board, discard_pile, drawn, player):
    # currently starting only with knowledge of hand and board and discardPile top and what is in it
    nodes = []
    for i in range(14):
        nodes.append(0)
    for card in discard_pile:
        if card == 15:
            continue
        nodes[card - 1] += 1
    curr = len(nodes)
    for i in range(14):
        nodes.append(0)
    if len(discard_pile) > 0 and discard_pile[-1] != 15:
        nodes[discard_pile[-1] + curr - 1] = 1
    for i in range(1, 15):
        nodes.append(hand[i])
    dirty_count = 0
    clean_count = 0
    for canasta in board.canastas:
        if canasta.is_dirty:
            dirty_count += 1
        else:
            clean_count += 1
    nodes.append(dirty_count)
    nodes.append(clean_count)
    curr = len(nodes)
    for i in range(4, 15):
        nodes.append(0)
    for pile in board.piles:
        nodes[curr + pile.cardType - 4] = pile.get_total_count()
    curr = len(nodes)
    for i in range(4, 15):
        nodes.append(0)
    for pile in board.piles:
        nodes[curr + pile.cardType - 4] = pile.twos + pile.jokers
    nodes.append(int(drawn))
    nodes.append(int(check_legal(player, player.game, "pickupPileJ")))
    nodes.append(int(check_legal(player, player.game, "pickupPile2")))
    nodes.append(player.game.turns)
    turn = player.game.turn
    for j in range(player.game.teamsCount):
        curr = len(nodes)
        for i in range(4, 15):
            nodes.append(0)
        for pile in player.game.players[
            (turn + j) % player.game.playersCount
        ].board.piles:
            nodes[curr + pile.cardType - 4] = pile.get_total_count()
    for i in range(player.game.playersCount - 1):
        for j in range(1, 15):
            nodes.append(player.knowledge[i][j])
    for i in range(player.game.playersCount):
        nodes.append(
            player.game.players[(turn + i) % player.game.playersCount].get_hand_size()
        )
    curr = len(nodes)
    for i in range(14):
        nodes.append(0)
    if len(discard_pile) > 0 and discard_pile[-1] != 15:
        nodes[discard_pile[-1] + curr - 1] = 1
    return nodes


def nodes_conversion_linear(hand, board, discard_pile, drawn, player):
    # player cards 14 * 8 * 6
    # player boards count 14 * 5 (3-7) * 3
    # player canasta count (number) * 3
    # discard pile top * 14
    # discard pile size (number)
    # drawn
    # frozen
    transposition_pos_to_card, transposition_card_to_pos = get_transposition_tables(
        player
    )
    turn = player.game.turn
    nodes = []
    for i in range(6):
        for j in range(1, 12):
            for k in range(1, 9):
                if (
                    player.game.players[(turn + i) % player.game.playersCount].hand[
                        transposition_pos_to_card[j]
                    ]
                    >= k
                ):
                    nodes.append(1)
                else:
                    nodes.append(0)
    for i in range(3):
        curr = len(nodes)
        nodes += [0] * (11 * 5)
        for canasta in player.game.players[
            (turn + i) % player.game.playersCount
        ].board.canastas:
            for j in range(5):
                if canasta.get_total_count() - 3 >= j:
                    nodes[
                        curr + (transposition_card_to_pos[canasta.cardType] - 1) * 5 + j
                    ] = 1
        for pile in player.game.players[
            (turn + i) % player.game.playersCount
        ].board.piles:
            for j in range(5):
                if pile.get_total_count() - 3 >= j:
                    nodes[
                        curr + (transposition_card_to_pos[pile.cardType] - 1) * 5 + j
                    ] = 1
    for i in range(3):
        nodes.append(
            len(
                player.game.players[
                    (turn + i) % player.game.playersCount
                ].board.canastas
            )
        )
    curr = len(nodes)
    for i in range(14):
        nodes.append(0)
    if len(discard_pile) > 0 and discard_pile[-1] != 15:
        nodes[discard_pile[-1] + curr - 1] = 1
    nodes.append(len(discard_pile))
    nodes.append(int(player.game.drawn))
    nodes.append(int(player.game.frozen))
    return nodes
