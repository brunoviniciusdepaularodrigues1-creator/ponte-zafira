class Psi0Controller:
    def __init__(self):
        self.last_stage = None

    def select_stage(self, C, G, V):
        # Ajuste 3: Transição Progressiva C -> F -> A
        # Se o último estágio foi Caos (C), força a passagem por Forma (F) antes de Ação (A)
        if self.last_stage == "C":
            self.last_stage = "F"
            return "F"
        
        # Lógica padrão com memória de transição
        stage = self._determine_stage(C, G, V)
        self.last_stage = stage
        return stage

    def _determine_stage(self, C, G, V):
        if V > 1.2:
            return "C"  # Caos (alta tensão)

        if C < 0.2:
            return "F"  # Forma (organizar)

        if G > 0.5 and C > 0.3:
            return "A"  # Ação (estrutura suficiente)

        if 0.3 <= C <= 0.7:
            return "V"  # Validação (equilíbrio)

        if C > 0.7:
            return "L"  # Learning (alta coerência)

        return "F"

    def run_cycle(self, E, steps=50):
        # Importação local para evitar circularidade
        from core.psi0_loop import psi0_cycle
        return psi0_cycle(E, steps)
