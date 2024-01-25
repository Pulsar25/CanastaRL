from rlcard.agents import DQNAgent
import envutil
import copy
import pygame
import numpy as np
import pickle
from collections import OrderedDict
from rlcard.agents import RandomAgent

n_observations = 250
n_actions = 50

file = open("2episode299model2.pkl", "rb")
model = pickle.load(file)
file.close()


models = [model,model,model,model,model,model]

def runGame(predictfunction,plays):
    teams = 3
    decks = 3
    handSize = 13
    movesMade = []
    game = envutil.Game(teams,decks,handSize)
    gameStates = [copy.deepcopy(game)]
    while True:
        chosen = predictfunction(game)
        chosen = envutil.numToMove(chosen)
        envutil.executeMove(game.players[game.turn],game,chosen)
        movesMade.append(chosen)
        gameStates.append(copy.deepcopy(game))
        if game.finished or game.turns >= plays:
            if game.finished:
                print("Finished Game")
            break
    return gameStates, movesMade

def predict(game):
    global models
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

def run_user_game():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    def _get_legal_actions():
        legal_actions = [i for i in range(50) if envutil.checkLegal(game.get_current_player(),game,envutil.numToMove(i))]
        legal_actions_ids = {action_event: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)

    print("Player will play player 1")
    teams = 3
    decks = 3
    handSize = 13
    game = envutil.Game(teams,decks,handSize)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
        text = ""
        if 0 == game.turn:
            text = "> "
        text += "P" + str(1) + " Hand: "
        hand = ""
        for i in range(15):
            hand += ((numToCard(i) + " ") * game.players[0].hand[i])
        text += hand
        font1 = pygame.font.SysFont(text, 36)
        img1 = font1.render(text, True, "white")
        screen.blit(img1, (20, 20))
        for player in range(3):
            text = ""
            if player == game.turn % 3:
                text = "> "
            text += "P" + str(player + 1) + " Board: "
            board = ""
            for pile in game.players[player].board.canastas:
                text += "*(" + numToCard(pile.cardType) + ", " + str(pile.count) + ", " + str(
                    pile.jokers) + "J, " + str(pile.twos) + "Twos)*  "
            for pile in game.players[player].board.piles:
                text += "(" + numToCard(pile.cardType) + ", " + str(pile.count) + ", " + str(pile.jokers) + "J, " + str(
                    pile.twos) + "Twos)  "
            font1 = pygame.font.SysFont(text, 36)
            img1 = font1.render(text, True, "white")
            screen.blit(img1, (20, 240 + player * 60))

        if len(game.discardPile) > 0:
            font1 = pygame.font.SysFont(numToCard(game.discardPile[-1]), 36)
            img1 = font1.render(numToCard(game.discardPile[-1]), True, "white")
            screen.blit(img1, (20, 400))

            font1 = pygame.font.SysFont(numToCard(game.discardPile[0: -1]), 36)
            img1 = font1.render(numToCard(game.discardPile[0:-1]), True, "white")
            screen.blit(img1, (20, 425))

        if game.turn % 6 == 0:
            chosen = input("Enter move ")
            while not envutil.checkLegal(game.players[0],game,chosen):
                print("Illegal Move")
                chosen = input("Enter move ")
        else:
            chosen = predict(game)
            chosen = envutil.numToMove(chosen)
            print("Player " + str(game.turn+1) + " chose " + chosen)
            _ = input("Click enter when ready to move on")
        envutil.executeMove(game.players[game.turn],game,chosen)
        if game.finished:
            if game.finished:
                print("Finished Game")
            break
        envutil.executeMove(game.players[game.turn % 6], game, chosen)


    pygame.quit()

def numToCard(n):
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

def run_model_game():
    print("Started Game")
    states, moves = runGame(predict, 1000)
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    state = 0
    last = None
    timeDown = 0.0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHTBRACKET] and (last != keys[pygame.K_RIGHTBRACKET] or timeDown > 1):
            state += 1
        if keys[pygame.K_LEFTBRACKET] and (last != keys[pygame.K_RIGHTBRACKET] or timeDown > 1):
            state -= 1
        last = keys[pygame.K_RIGHTBRACKET] or keys[pygame.K_LEFTBRACKET]
        if state >= len(states):
            state = len(states) - 1
        if state < 0:
            state = len(states) + state

        if keys[pygame.K_q]:
            running = False
            break

        for player in range(6):
            text = ""
            if player == states[state].turn:
                text = "> "
            text += "P" + str(player + 1) + " Hand: "
            hand = ""
            for i in range(15):
                hand += ((numToCard(i) + " ")* states[state].players[player].hand[i])
            text += hand
            font1 = pygame.font.SysFont(text, 36)
            img1 = font1.render(text, True, "white")
            screen.blit(img1, (20, 20 + player * 30))

        for player in range(3):
            text = ""
            if player == states[state].turn % 3:
                text = "> "
            text += "P" + str(player + 1) + " Board: "
            board = ""
            for pile in states[state].players[player].board.canastas:
                text += "*(" + numToCard(pile.cardType) + ", " + str(pile.count) + ", " + str(pile.jokers) + "J, " + str(pile.twos) + "Twos)*  "
            for pile in states[state].players[player].board.piles:
                text += "(" + numToCard(pile.cardType) + ", " + str(pile.count) + ", " + str(pile.jokers) + "J, " + str(pile.twos) + "Twos)  "
            font1 = pygame.font.SysFont(text, 36)
            img1 = font1.render(text, True, "white")
            screen.blit(img1, (20, 240 + player * 60))

        if state < len(moves):
            font1 = pygame.font.SysFont((moves[state]), 36)
            img1 = font1.render((moves[state]), True, "white")
            screen.blit(img1, (20, 200))
        if len(states[state].discardPile) > 0:
            font1 = pygame.font.SysFont(numToCard(states[state].discardPile[-1]), 36)
            img1 = font1.render(numToCard(states[state].discardPile[-1]), True, "white")
            screen.blit(img1, (20, 400))

            font1 = pygame.font.SysFont(numToCard(states[state].discardPile[0: -1]), 36)
            img1 = font1.render(numToCard(states[state].discardPile[0:-1]), True, "white")
            screen.blit(img1, (20, 425))

        font1 = pygame.font.SysFont(str(state), 36)
        img1 = font1.render(str(state), True, "white")
        screen.blit(img1, (20, 450))

        pygame.display.flip()
        dt = clock.tick(60) / 1000
        timeDown += dt
        if not keys[pygame.K_LEFTBRACKET] and not keys[pygame.K_RIGHTBRACKET]:
            timeDown = 0

    pygame.quit()

run_user_game()
