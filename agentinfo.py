class AgentInfo():

    def __init__(self):
        self.scores = []
        self.total_score = 0

    def addScore(self,score):
        self.scores.append(score)
        self.total_score += score
