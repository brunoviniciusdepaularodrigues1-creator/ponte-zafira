import numpy as np

class LatentEncoder:

    def __init__(self, input_dim=9, latent_dim=4, lr=0.01):
        self.W = np.random.randn(input_dim, latent_dim) * 0.1
        self.lr = lr

    def encode(self, x):
        z = np.tanh(np.dot(x, self.W))
        return z

    def update(self, x, latent, error):
        # Ajuste para garantir que x e latent tenham as dimensões corretas para np.outer
        # x deve ser 1D, latent deve ser 1D
        if x.ndim > 1: # Se x for [[...]], transforma para [...] 
            x = x.flatten()
        if latent.ndim > 1: # Se latent for [[...]], transforma para [...] 
            latent = latent.flatten()

        grad = np.outer(x, latent)
        self.W += self.lr * error * grad
