import pandas as pd
from numpy import unique
from pandas import DataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import AgentBasedModel.utils.math as math


class TransitionMatrix:
    def __init__(self, states: list = None):
        self.labels = ['stationary', 'bullish', 'bearish', 'speculative', 'destructive']
        if states:
            self.matrix = self._initialize(states)
        else:
            self.matrix = self._create_empty()

    def _create_empty(self):
        matrix = list()
        for _ in range(len(self.labels)):
            tmp = list()
            for _ in range(len(self.labels)):
                tmp.append(0)
            matrix.append(tmp)
        return matrix

    def _initialize(self, states):
        # Matrix initialization
        matrix = self._create_empty()

        # Transition matrix calculation
        for i in range(len(states) - 1):
            for st1 in states[i]:
                for st2 in states[i+1]:
                    idx1 = self.labels.index(st1)
                    idx2 = self.labels.index(st2)
                    matrix[idx1][idx2] += 1
        return matrix

    def update(self, states):
        matrix = self._initialize(states)
        for i in range(len(self.labels)):
            for j in range(len(self.labels)):
                self.matrix[i][j] += matrix[i][j]

    def distance(self, other, value: bool = True, prob: bool = True):
        dist_m = list()
        m1 = self.get_matrix(prob)
        m2 = other.get_matrix(prob)
        for i in range(len(self.matrix)):
            row = list()
            for j in range(len(self.matrix[0])):
                row.append(m2[i][j] - m1[i][j])
            dist_m.append(row)

        if value:
            return sum([sum([abs(el) for el in row]) for row in dist_m])
        return dist_m

    def get_matrix(self, prob: bool = False):
        if prob:
            data = [[el / sum(row) if sum(row) > 0 else 0 for el in row] for row in self.matrix]
            return data
        else:
            return self.matrix


class TimeMatrix:
    def __init__(self, states: list = None, labels: list = None):
        self.labels = ['stationary', 'bullish', 'bearish', 'destructive', 'speculative']
        self.matrix = list() if states is None else self._initialize(states)

    def _initialize(self, states):
        matrix = list()
        for values in states:
            tmp = {label: 0 for label in self.labels}
            for v in values:
                tmp[v] += 1
            matrix.append(tmp)
        return matrix

    def update(self, states):
        if not self.matrix:
            self.matrix = self._initialize(states)
        else:
            for i, values in enumerate(states):
                for v in values:
                    self.matrix[i][v] += 1


def heatmap_transition(transition_matrix: TransitionMatrix, prob: bool = True, annot: bool = True, figsize=(6, 6)):
    vmax = None
    if prob:
        vmax = .7

    data = transition_matrix.get_matrix(prob)
    data = DataFrame(data, index=transition_matrix.labels, columns=transition_matrix.labels)

    plt.figure(figsize=figsize)
    sns.heatmap(data, annot=annot, vmin=0, vmax=vmax, cbar=False, cmap='Blues')
    plt.show()


def heatmap_distance(first: TransitionMatrix, second: TransitionMatrix, prob: bool = True, annot: bool = True,
                     figsize=(6, 6)):
    vmax = None
    if prob:
        vmax = .4
    data = first.distance(second, value=False, prob=prob).copy()
    data = DataFrame(data, index=first.labels, columns=first.labels)

    plt.figure(figsize=figsize)
    sns.heatmap(data, annot=annot, vmin=-vmax, vmax=vmax, cmap='vlag', cbar=False)
    plt.show()


def heatmap_time(matrix: TimeMatrix, size=None, window=0, prob: bool = True, annot: bool = True, figsize=(6, 6)):
    data = DataFrame(matrix.matrix)
    if prob:
        data = data / data.sum()

    if size:
        data.index = [size + i * size - window for i in range(data.shape[0])]

    plt.figure(figsize=figsize)
    sns.heatmap(data.T, annot=annot, vmin=0, cbar=False, cmap='Blues')
    plt.show()


def bar_transition(transition_matrix: TransitionMatrix, prob: bool = True, figsize=(6, 6)):
    val = [sum(row) for row in transition_matrix.matrix]
    if prob:
        val = [v / sum(val) for v in val]

    plt.figure(figsize=(6, 6))
    plt.title('Market States Frequency')
    plt.bar(transition_matrix.labels, val, color='tab:blue')
    plt.ylabel('Frequency')
    plt.ylim(0, 1)
    plt.show()
