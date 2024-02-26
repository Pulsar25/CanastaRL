class AgentInfo:
    def __init__(self):
        self.scores = []
        self.total_score = 0
        self.total_last_score = 0
        self.last_scores = []

    def add_score(self, score):
        self.scores.append(score)
        self.total_score += score
        self.total_last_score += score
        if len(self.scores) > 50:
            self.total_last_score -= self.scores[len(self.scores) - 51]
        self.last_scores.append(self.get_avg_recent_score())

    def get_avg_score(self):
        return self.total_score / len(self.scores)

    def get_avg_recent_score(self):
        return self.total_last_score / 50
