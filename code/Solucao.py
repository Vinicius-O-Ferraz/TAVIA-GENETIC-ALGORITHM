from Periodo import periodo
from Turma import turma

class solucao:
    def __init__(self, id_solucao):
        self.id_solucao = id_solucao
        self.periodos = [periodo() for _ in range(8)]  # Exemplo com 8 períodos

    def __repr__(self):
        return f"Solucao {self.id_solucao}:\n" + "\n".join(f"Periodo {i+1}:\n{str(p)}" for i, p in enumerate(self.periodos))
    
solucao1 = solucao("S1")
print(solucao1)