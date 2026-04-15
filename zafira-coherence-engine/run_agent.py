import sys
import os

# Adiciona a raiz do projeto ao sys.path para permitir imports de core
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.psi0_agent import Psi0Agent

if __name__ == "__main__":
    # Inicia o agente com intervalo de 10 segundos
    agent = Psi0Agent(interval=10)
    agent.run()
