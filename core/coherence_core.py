class CoherenceSystem:
    def __init__(self, G=1.0, V=1.0, alpha=0.1, beta=0.1):
        self.G = G
        self.V = V
        self.alpha = alpha
        self.beta = beta

    def compute_coherence(self):
        # Limitar C para ser sempre positivo (não-negativo)
        return max(0, self.G / (1 + self.V))

    def step(self, E):
        C = self.compute_coherence()

        self.G = self.G + self.alpha * (C - self.V)
        self.V = self.V + self.beta * (E - C)

        # Proteger o sistema: G e V devem ser sempre >= 0
        self.G = max(self.G, 0)
        self.V = max(self.V, 0)

        return {
            "C": C,
            "G": self.G,
            "V": self.V
        }
