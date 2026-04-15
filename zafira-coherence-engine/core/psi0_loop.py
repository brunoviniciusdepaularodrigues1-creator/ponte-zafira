from core.coherence_core import CoherenceSystem
from core.psi0_controller import Psi0Controller

def psi0_cycle(E, steps=50):
    system = CoherenceSystem()
    controller = Psi0Controller()
    history = []

    for t in range(steps):
        state = system.step(E)
        
        # Nova lógica de decisão baseada no estado dinâmico (C, G, V)
        stage = controller.select_stage(state["C"], state["G"], state["V"])

        history.append({
            "t": t,
            "C": state["C"],
            "G": state["G"],
            "V": state["V"],
            "stage": stage
        })

    return history
