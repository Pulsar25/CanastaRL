from collections import defaultdict
import copy
import random


def getCardCount(i):
    if i == 1:
        return 50
    if i == 2 or i == 14:
        return 20
    if i <= 7:
        return 5
    if i <= 13:
        return 10
    return 0


def generateDeck():
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

    def __init__(self, type, count):
        self.cardType = type
        self.count = 0
        self.count = count
        self.jokers = 0
        self.twos = 0

    def getScore(self):
        return (
            self.jokers * 50 + self.twos * 20 + self.count * getCardCount(self.cardType)
        )

    def isDirty(self):
        return not (self.twos == 0 and self.jokers == 0)

    def getTotalCount(self):
        return self.jokers + self.twos + self.count

    def getCardType(self):
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
        self.player1 = None
        self.player2 = None

    def setPlayers(self, p1, p2):
        self.player1 = p1
        self.player2 = p2

    def getScore(self):
        out = 0
        """
        if len(self.piles) == 0 and len(self.canastas) == 0:
            out -= 100 * self.redThrees
        else:
            out += 100 * self.redThrees
        """
        for pile in self.piles:
            out += pile.getScore()
        out -= self.player1.getHandScore()
        out -= self.player2.getHandScore()
        for canasta in self.canastas:
            out += canasta.getScore()
            if not canasta.isDirty():
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
        self.knowledge = [defaultdict(int) for _ in range(5)]
        self.partner = None

    def getHandSize(self):
        out = 0
        for i in range(1, 15):
            out += self.hand[i]
        return out

    def getHandScore(self):
        out = 0
        for i in self.hand:
            out += self.hand[i] * getCardCount(i)
        if out == 0:
            out = -100
        return out

    """
    def nodesConversion(self):
        # currently starting only with knowledge of hand and board and discardPile top and what is in it
        nodes = []
        for i in range(14):
            nodes.append(0)
        for card in self.game.discardPile:
            nodes[card - 2] += 1
        curr = len(nodes)
        for i in range(14):
            nodes.append(0)
        if (len(self.game.discardPile) > 0):
            nodes[self.game.discardPile[-1] + curr - 2] = 1
        for i in range(1, 15):
            nodes.append(self.hand[i] ** 2)
        dirtyCount = 0
        cleanCount = 0
        for canasta in self.board.canastas:
            if canasta.isDirty:
                dirtyCount += 1
            else:
                cleanCount += 1
        nodes.append(dirtyCount)
        nodes.append(cleanCount)
        curr = len(nodes)
        for i in range(4, 15):
            nodes.append(0)
        for pile in self.board.piles:
            nodes[curr + pile.cardType - 4] = pile.getTotalCount()
        curr = len(nodes)
        for i in range(4, 15):
            nodes.append(0)
        for pile in self.board.piles:
            nodes[curr + pile.cardType - 4] = pile.twos + pile.jokers
        nodes.append(int(self.game.drawn))
        nodes.append(int(checkLegal(self, self.game, "pickupPileJ")))
        nodes.append(int(checkLegal(self, self.game, "pickupPile2")))
        nodes.append(self.game.turns)
        turn = self.game.turn
        curr = len(nodes)
        for i in range(4, 15):
            nodes.append(0)
        for pile in self.game.players[(turn + 1) % 6].board.piles:
            nodes[curr + pile.cardType - 4] = pile.getTotalCount()
        curr = len(nodes)
        for i in range(4, 15):
            nodes.append(0)
        for pile in self.game.players[(turn + 2) % 6].board.piles:
            nodes[curr + pile.cardType - 4] = pile.getTotalCount()
        for i in range(3, 15):
            nodes.append(int(self.hand[i] >= 2))
        for i in range(5):
            for j in range(1, 15):
                nodes.append(self.knowledge[i][j])
        for i in range(6):
            nodes.append
        for i in range(51):
            nodes.append(int(checkLegal(self, self.game, numToMove(i))))
        return nodes
    """

    def __str__(self):
        out = ""
        for i in range(1, 15):
            out += "(" + str(i) + ", " + str(self.hand[i]) + ")"
        return out


class Team:
    playerOne = None
    playerTwo = None
    score = 0
    board = None


class Game:
    def draw(self):
        if len(self.drawPile) == 1:
            self.drawPile += self.discardPile
            self.discardPile = []
            self.drawPile.reverse()
        if len(self.drawPile) == 0:
            self.drawPile += self.discardPile
            self.discardPile = []
            self.drawPile.reverse()
        if len(self.drawPile) == 0:
            self.finished = True
            return 4
        return self.drawPile.pop()

    def get_num_players(self):
        return self.playersCount

    def get_num_actions(self):
        return 50

    def init_game(self):
        self.reset()
        return (
            nodesConversion(
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
        return self.turn % 6

    def get_state(self, player_id):
        return nodesConversion(
            self.players[player_id].hand,
            self.players[player_id].board,
            self.discardPile,
            self.drawn,
            self.players[player_id],
        )

    def step(self, action):
        executeMove(self.players[self.get_player_id()], self, action)
        return (
            nodesConversion(
                self.players[self.turn % 6].hand,
                self.players[self.turn % 6].board,
                self.discardPile,
                self.drawn,
                self.players[self.turn % 6],
            ),
            self.turn % 6,
        )

    def __init__(self, teams, decks, handSize):
        self.allow_step_back = False
        self.discardPile = []
        self.drawPile = []
        self.teams = []
        self.teamsCount = teams
        self.decks = decks
        self.boards = []
        self.players = [0] * (teams * 2)
        self.playersCount = None
        self.teamsCount = None
        self.turns = 0
        self.handSize = None
        self.drawn = False
        self.frozen = False
        self.turn = 0
        self.finished = False
        self.handSize = handSize
        self.playersCount = teams * 2
        self.teamsCount = teams
        for k in range(decks):
            self.drawPile += generateDeck()
        random.shuffle(self.drawPile)
        self.discardPile.append(self.draw())
        for i in range(teams):
            playerOneHand = []
            playerTwoHand = []
            for j in range(handSize):
                playerOneHand.append(self.draw())
                playerTwoHand.append(self.draw())
            board = Board()
            team = Team()
            playerOne = Player(playerOneHand, self, board)
            playerTwo = Player(playerTwoHand, self, board)
            playerOne.partner = playerTwo
            playerTwo.partner = playerOne
            board.setPlayers(playerOne, playerTwo)
            playerOne.teamate = playerTwo
            playerTwo.teamate = playerOne
            playerTwo.game = self
            playerOne.game = self
            team.playerOne = playerOne
            team.playerTwo = playerTwo
            team.board = board
            playerOne.team = team
            playerTwo.team = team
            self.teams.append(team)
            self.boards.append(board)
            self.players[i] = playerOne
            self.players[i + teams] = playerTwo

    def reset(self):
        self.discardPile = []
        self.drawPile = []
        self.teams = []
        self.boards = []
        self.players = [0] * self.playersCount
        self.turns = 0
        self.drawn = False
        self.frozen = False
        self.turn = 0
        self.finished = False
        for k in range(self.decks):
            self.drawPile += generateDeck()
        random.shuffle(self.drawPile)
        self.discardPile.append(self.draw())
        for i in range(self.teamsCount):
            playerOneHand = []
            playerTwoHand = []
            for j in range(self.handSize):
                playerOneHand.append(self.draw())
                playerTwoHand.append(self.draw())
            board = Board()
            team = Team()
            playerOne = Player(playerOneHand, self, board)
            playerTwo = Player(playerTwoHand, self, board)
            playerOne.partner = playerTwo
            playerTwo.partner = playerOne
            board.setPlayers(playerOne, playerTwo)
            playerOne.teamate = playerTwo
            playerTwo.teamate = playerOne
            playerTwo.game = self
            playerOne.game = self
            team.playerOne = playerOne
            team.playerTwo = playerTwo
            team.board = board
            playerOne.team = team
            playerTwo.team = team
            self.teams.append(team)
            self.boards.append(board)
            self.players[i] = playerOne
            self.players[i + self.teamsCount] = playerTwo

    def get_current_player(self):
        return self.players[self.turn % 6]

    def __str__(self):
        out = ""
        for i in range(self.teamsCount * 2):
            out += str(self.players[i]) + " " + str(self.players[i].board) + "\n"
        out += str(self.discardPile) + "\n"
        out += str(self.turn)
        return out


def checkLegal(player: Player, game, move):
    while player.hand[15] > 0:
        player.board.redThrees += 1
        player.hand[15] -= 1
        player.hand[game.draw()] += 1
    handSize = 0
    for i in range(1, 15):
        handSize += player.hand[i]
    if move == "goOut":
        return handSize - player.hand[3] == 1 and (
            player.hand[3] >= 3 or player.hand[3] == 0
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
        if len(game.discardPile) == 0:
            return False
        if len(game.discardPile) == 1 and handSize == 1:
            return False
        for i in player.board.piles:
            if i.cardType == game.discardPile[-1]:
                return True
        if handSize <= 2 and len(game.discardPile) == 1:
            return False
        if game.discardPile[-1] <= 2:
            return False
        if game.drawn or game.discardPile[-1] < 4:
            return False
        if game.frozen or len(player.board.piles) + len(player.board.canastas) == 0:
            return player.hand[game.discardPile[-1]] >= 2
        return (
            player.hand[1] >= 1 and player.hand[game.discardPile[-1]]
        ) >= 1 or player.hand[game.discardPile[-1]] >= 2
    elif move == "pickupPile2":
        if len(game.discardPile) == 0:
            return False
        if len(game.discardPile) == 1 and handSize == 1:
            return False
        for i in player.board.piles:
            if i.cardType == game.discardPile[-1]:
                return True
        if handSize <= 2 and len(game.discardPile) == 1:
            return False
        if game.drawn or game.discardPile[-1] < 4:
            return False
        if game.discardPile[-1] <= 2:
            return False
        if game.frozen or len(player.board.piles) + len(player.board.canastas) == 0:
            return player.hand[game.discardPile[-1]] >= 2
        return (
            player.hand[2] >= 1 and player.hand[game.discardPile[-1]] >= 1
        ) or player.hand[game.discardPile[-1]] >= 2
    elif move[0] == "w" and move[4] == "J":
        if game.drawn == False:
            return False
        playedCard = int(move[5:])
        if handSize <= 2 and len(player.board.canastas) < 2:
            return False
        if player.hand[1] <= 0:
            return False
        for pile in player.board.piles:
            if pile.cardType == playedCard:
                return pile.twos + pile.jokers + 1 <= pile.count
        return False
    elif move[0] == "w" and move[4] == "2":
        if game.drawn == False:
            return False
        playedCard = int(move[5:])
        if handSize <= 2 and len(player.board.canastas) < 2:
            return False
        if player.hand[2] <= 0:
            return False
        for pile in player.board.piles:
            if pile.cardType == playedCard:
                return pile.twos + pile.jokers + 1 <= pile.count
        return False
    elif move == "pickup":
        return not game.drawn
    elif move[0] == "d":
        if game.drawn == False:
            return False
        playedCard = int(move[1::])
        if player.hand[playedCard] <= 0:
            return False
        if len(player.board.canastas) >= 2:
            return True
        else:
            return handSize > 1
    else:
        if (
            game.drawn == False
            or handSize == 1
            or (handSize == 2 and len(player.board.canastas) < 2)
        ):
            return False
        playedCard = int(move)
        if player.hand[playedCard] == 0:
            return False
        for pile in player.board.piles:
            if pile.cardType == playedCard:
                return True
        if player.hand[playedCard] >= 3 or (
            player.hand[playedCard] == 2 and player.hand[1] + player.hand[2] >= 1
        ):
            return handSize > 4 or (handSize > 3 and len(player.board.canastas) >= 2)
        return False


def numToMove(num):
    if num <= 10:
        return str(num + 4)
    if num <= 24:
        return "d" + str(num - 10)
    if num == 25:
        return "pickupPileJ"
    if num == 26:
        return "pickupPile2"
    if num == 27:
        return "pickup"
    if num <= 38:
        return "wildJ" + str(num - 24)
    if num <= 49:
        return "wild2" + str(num - 35)
    if num == 50:
        return "goOut"


def executeMove(player: Player, game: Game, move):
    if game.turns >= 360:
        game.finished = True
    knowledgeUpdate = defaultdict(int)
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
        knowledgeUpdate[card] -= 1
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
                knowledgeUpdate[game.discardPile[-1]] -= 2
                player.board.piles.append(BoardStack(game.discardPile[-1], 3))
            else:
                player.hand[game.discardPile[-1]] -= 1
                player.hand[1] -= 1
                knowledgeUpdate[1] -= 1
                knowledgeUpdate[game.discardPile[-1]] -= 1
                newStack = BoardStack(game.discardPile[-1], 2)
                newStack.jokers += 1
                player.board.piles.append(newStack)
        for card in game.discardPile:
            player.hand[card] += 1
            knowledgeUpdate[card] += 1
        player.hand[player.game.discardPile[-1]] -= 1
        knowledgeUpdate[player.game.discardPile[-1]] -= 1
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
                knowledgeUpdate[game.discardPile[-1]] -= 2
                player.board.piles.append(BoardStack(game.discardPile[-1], 3))
            else:
                player.hand[game.discardPile[-1]] -= 1
                knowledgeUpdate[game.discardPile[-1]] -= 1
                player.hand[2] -= 1
                knowledgeUpdate[2] -= 1
                newStack = BoardStack(game.discardPile[-1], 2)
                newStack.twos += 1
                player.board.piles.append(newStack)
        for card in game.discardPile:
            player.hand[card] += 1
            knowledgeUpdate[card] += 1
        player.hand[player.game.discardPile[-1]] -= 1
        knowledgeUpdate[player.game.discardPile[-1]] -= 1
        game.frozen = False
        game.discardPile = []
    elif move[0] == "w" and move[4] == "J":
        player.hand[1] -= 1
        knowledgeUpdate[1] -= 1
        for pile in player.board.piles:
            if int(move[5::]) == pile.cardType:
                pile.jokers += 1
                break
    elif move[0] == "w" and move[4] == "2":
        player.hand[2] -= 1
        knowledgeUpdate[2] -= 1
        for pile in player.board.piles:
            if int(move[5::]) == pile.cardType:
                pile.twos += 1
                break
    elif move == "pickup":
        game.drawn = True
        newCard = game.draw()
        while newCard == 15:
            player.board.redThrees += 1
            newCard = game.draw()
        player.hand[newCard] += 1
    elif move[0] == "d":
        game.discardPile.append(int(move[1::]))
        player.hand[int(move[1::])] -= 1
        knowledgeUpdate[int(move[1::])] -= 1
        game.turn += 1
        game.turns += 1
        game.turn = game.turn % game.playersCount
        game.drawn = False
        if int(move[1::]) <= 2:
            game.frozen = True
        handSize = 0
        for i in range(1, 15):
            handSize += player.hand[i]
        if handSize == 0:
            game.finished = True
    else:
        done = False
        for pile in player.board.piles:
            if pile.cardType == int(move):
                pile.count += 1
                player.hand[int(move)] -= 1
                knowledgeUpdate[int(move)] -= 1
                done = True
                break
        if not done:
            if player.hand[int(move)] >= 3:
                player.hand[int(move)] -= 3
                knowledgeUpdate[int(move)] -= 3
                player.board.piles.append(BoardStack(int(move), 3))
            else:
                if player.hand[1] >= 1:
                    player.hand[int(move)] -= 2
                    player.hand[1] -= 1
                    knowledgeUpdate[int(move)] -= 2
                    knowledgeUpdate[1] -= 1
                    newPile = BoardStack(int(move), 2)
                    newPile.jokers += 1
                    player.board.piles.append(newPile)
                else:
                    player.hand[int(move)] -= 2
                    player.hand[2] -= 1
                    knowledgeUpdate[int(move)] -= 2
                    knowledgeUpdate[2] -= 1
                    newPile = BoardStack(int(move), 2)
                    newPile.twos += 1
                    player.board.piles.append(newPile)
    if len(player.board.piles) > 0:
        i = 0
        for j in range(len(player.board.piles)):
            if player.board.piles[i].getTotalCount() >= 7:
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
    for i in range(5):
        for j in range(1, 15):
            game.players[(start + i + 1) % 6].knowledge[4 - i][j] += knowledgeUpdate[j]
    for canasta in player.board.canastas:
        canasta.count += player.hand[canasta.cardType]
        player.hand[canasta.cardType] = 0
    handSize = 0
    for i in range(1, 15):
        handSize += player.hand[i]
    if handSize == 0:
        game.finished = True


def moveToNum(move):
    if move == "goOut":
        return 50
    if move == "pickupPile2":
        return 26
    if move == "pickupPileJ":
        return 25
    if move == "pickup":
        return 27
    if len(move) >= 5 and move[4] == "J":
        return int(move[5::]) + 24
    if len(move) >= 5 and move[4] == "2":
        return int(move[5::]) + 35
    if move[0] == "d":
        return int(move[1::]) + 10
    return int(move) - 4


def nodesConversion(hand, board, discardPile, drawn, player):
    # currently starting only with knowledge of hand and board and discardPile top and what is in it
    nodes = []
    for i in range(14):
        nodes.append(0)
    for card in discardPile:
        nodes[card - 2] += 1
    curr = len(nodes)
    for i in range(14):
        nodes.append(0)
    if len(discardPile) > 0:
        nodes[discardPile[-1] + curr - 2] = 1
    for i in range(1, 15):
        nodes.append(hand[i] ** 2)
    dirtyCount = 0
    cleanCount = 0
    for canasta in board.canastas:
        if canasta.isDirty:
            dirtyCount += 1
        else:
            cleanCount += 1
    nodes.append(dirtyCount)
    nodes.append(cleanCount)
    curr = len(nodes)
    for i in range(4, 15):
        nodes.append(0)
    for pile in board.piles:
        nodes[curr + pile.cardType - 4] = pile.getTotalCount()
    curr = len(nodes)
    for i in range(4, 15):
        nodes.append(0)
    for pile in board.piles:
        nodes[curr + pile.cardType - 4] = pile.twos + pile.jokers
    nodes.append(int(drawn))
    nodes.append(int(checkLegal(player, player.game, "pickupPileJ")))
    nodes.append(int(checkLegal(player, player.game, "pickupPile2")))
    nodes.append(player.game.turns)
    turn = player.game.turn
    curr = len(nodes)
    for i in range(4, 26):
        nodes.append(0)
    for pile in player.game.players[(turn + 1) % 6].board.piles:
        nodes[curr + pile.cardType - 4] = pile.getTotalCount()
    curr = len(nodes)
    for i in range(4, 15):
        nodes.append(0)
    for pile in player.game.players[(turn + 2) % 6].board.piles:
        nodes[curr + pile.cardType - 4] = pile.getTotalCount()
    for i in range(5):
        for j in range(1, 15):
            nodes.append(player.knowledge[i][j])
    for i in range(6):
        nodes.append(player.game.players[(turn + i) % 6].getHandSize())
    return nodes
