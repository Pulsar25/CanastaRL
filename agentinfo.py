class AgentInfo:
    def __init__(self, recent):
        self.scores = []
        self.total_score = 0
        self.total_last_score = 0
        self.last_scores = []
        self.lengths = []
        self.total_length = 0
        self.total_last_length = 0
        self.last_lengths = []
        self.recent = recent
        self.perf_evals = []
        self.total_perf_evals = 0
        self.total_last_perf_evals = 0
        self.last_perf_evals = []

    def add_perf_eval(self, perf_eval):
        self.perf_evals.append(perf_eval)
        self.total_perf_evals += perf_eval
        self.total_last_perf_evals += perf_eval
        if len(self.perf_evals) > self.recent:
            self.total_last_perf_evals -= self.perf_evals[len(self.perf_evals) - self.recent - 1]
        self.last_perf_evals.append(self.get_avg_recent_perf_eval())

    def add_score(self, score):
        self.scores.append(score)
        self.total_score += score
        self.total_last_score += score
        if len(self.scores) > self.recent:
            self.total_last_score -= self.scores[len(self.scores) - self.recent - 1]
        self.last_scores.append(self.get_avg_recent_score())

    def get_last_scores(self, n):
        if len(self.last_scores) < n:
            return self.last_scores
        else:
            return self.last_scores[len(self.last_scores) - n : len(self.last_scores)]

    def get_last_perf_evals(self, n):
        if len(self.last_perf_evals) < n:
            return self.last_perf_evals
        else:
            return self.last_perf_evals[len(self.last_perf_evals) - n : len(self.last_perf_evals)]

    def get_perf_evals(self, n):
        if len(self.perf_evals) < n:
            return self.perf_evals
        else:
            return self.perf_evals[len(self.perf_evals) - n : len(self.perf_evals)]

    def get_avg_score(self):
        return self.total_score / len(self.scores)

    def get_avg_perf_eval(self):
        return self.total_perf_evals / len(self.perf_evals)

    def get_avg_recent_score(self):
        return self.total_last_score / self.recent

    def get_avg_recent_perf_eval(self):
        return self.total_last_perf_evals / self.recent

    def add_length(self, length):
        self.lengths.append(length)
        self.total_length += length
        self.total_last_length += length
        if len(self.lengths) > self.recent:
            self.total_last_length -= self.lengths[len(self.lengths) - self.recent - 1]
        self.last_lengths.append(self.get_avg_recent_length())

    def get_avg_length(self):
        return self.total_length / len(self.lengths)

    def get_avg_recent_length(self):
        return self.total_last_length / self.recent
