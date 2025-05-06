class DeterministicRNG:
    def __init__(self, seed=42):
        self.state = seed

    def _next_int(self):
        self.state = (1103515245 * self.state + 12345) & 0x7fffffff
        return self.state

    def random(self):
        return self._next_int() / 2147483647.0

    def randint(self, a, b):
        if a > b:
            a, b = b, a
        return a + int(self.random() * (b - a + 1))
