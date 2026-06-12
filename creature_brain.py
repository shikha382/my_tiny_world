import numpy as np

INPUTS = 9
HIDDEN = 8
OUTPUTS = 2


class Brain:
    def __init__(self):
        self.w1 = np.random.randn(INPUTS, HIDDEN) * 0.5
        self.w2 = np.random.randn(HIDDEN, HIDDEN) * 0.5
        self.w3 = np.random.randn(HIDDEN, OUTPUTS) * 0.5
        self.b1 = np.zeros(HIDDEN)
        self.b2 = np.zeros(HIDDEN)
        self.b3 = np.zeros(OUTPUTS)

    def think(self, inputs):
        hidden1 = np.tanh(inputs @ self.w1 + self.b1)
        hidden2 = np.tanh(hidden1 @ self.w2 + self.b2)
        output = np.tanh(hidden2 @ self.w3 + self.b3)
        return output

    def copy(self):
        new_brain = Brain()
        new_brain.w1 = self.w1.copy()
        new_brain.w2 = self.w2.copy()
        new_brain.w3 = self.w3.copy()
        new_brain.b1 = self.b1.copy()
        new_brain.b2 = self.b2.copy()
        new_brain.b3 = self.b3.copy()
        return new_brain

    def mutate(self, rate=0.1, strength=0.2):
        if np.random.rand() < rate:
            self.w1 += np.random.randn(*self.w1.shape) * strength
        if np.random.rand() < rate:
            self.w2 += np.random.randn(*self.w2.shape) * strength
        if np.random.rand() < rate:
            self.w3 += np.random.randn(*self.w3.shape) * strength
        if np.random.rand() < rate:
            self.b1 += np.random.randn(*self.b1.shape) * strength
        if np.random.rand() < rate:
            self.b2 += np.random.randn(*self.b2.shape) * strength
        if np.random.rand() < rate:
            self.b3 += np.random.randn(*self.b3.shape) * strength
