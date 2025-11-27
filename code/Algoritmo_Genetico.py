from algoritmo_abstrato import AlgoritmoAbstrato
from Random_Init import random_initialize_solution
import random
from Solucao import solucao

class AGSimples(AlgoritmoAbstrato):

    def __init__(self, tamanho_populacao, taxa_mutacao, taxa_crossover, numero_geracoes):
        self.tamanho_populacao = tamanho_populacao
        self.taxa_mutacao = taxa_mutacao
        self.taxa_crossover = taxa_crossover
        self.numero_geracoes =  numero_geracoes
        self.population = []
        self.fitness_scores = []


    # -------------------------------
    # 1) População inicial
    # -------------------------------
    def inicializar_populacao(self):
        self.population = [random_initialize_solution(i) for i in range(self.tamanho_populacao)]

    # -------------------------------
    # 2) Função de avaliação
    # -------------------------------

    def checar_restrições(self, individuo):
        s = 0

        # individuo is expected to be a `solucao` object with `periodos`,
        # each `periodo` having a 2x5 `matriz` containing subject ids (or 0).
        try:
            from Professores import professores as prof_dict
        except Exception:
            prof_dict = {}

        # Build subject -> professor mapping
        subject_to_prof = {}
        for prof, subjects in prof_dict.items():
            for sub in subjects:
                subject_to_prof[sub] = prof

        # 1) Penalize empty slots
        for p in individuo.periodos:
            for r in p.matriz:
                for cell in r:
                    if cell == 0 or cell is None:
                        s += 1

        # 2) Penalize duplicate subject in the same period
        for p in individuo.periodos:
            counts = {}
            for r in p.matriz:
                for cell in r:
                    if cell and cell != 0:
                        counts[cell] = counts.get(cell, 0) + 1
            for subj, cnt in counts.items():
                if cnt > 1:
                    s += (cnt - 1)

        # 3) Penalize professor conflicts at the same time-slot across periods
        # For each timeslot (row,col) gather subjects across all periods
        if len(individuo.periodos) > 0:
            rows = len(individuo.periodos[0].matriz)
            cols = len(individuo.periodos[0].matriz[0]) if rows > 0 else 0
            for r in range(rows):
                for c in range(cols):
                    prof_counts = {}
                    for p in individuo.periodos:
                        subj = p.matriz[r][c]
                        if subj and subj != 0:
                            # subj may be like 'PCO-1', map to base code
                            base = subj.split("-")[0] if isinstance(subj, str) else subj
                            prof = subject_to_prof.get(base)
                            if prof:
                                prof_counts[prof] = prof_counts.get(prof, 0) + 1
                    for prof, cnt in prof_counts.items():
                        if cnt > 1:
                            s += (cnt - 1)

        # Keep original return convention: if no violations, higher score
        if s == 0:
            return 2
        else:
            return 1 / s

    def avaliar_populacao(self):
        # Avalia cada indivíduo (objeto `solucao`) e guarda os scores em uma lista
        self.fitness_scores = [self.checar_restrições(ind) for ind in self.population]

    # -------------------------------
    # 3) Seleção por torneio
    # -------------------------------
    def selecao(self):
        pass
    # -------------------------------
    # 4) Crossover de um ponto
    # -------------------------------
    def crossover(self, pai1, pai2):
        pass

    # -------------------------------
    # 5) Mutação bit-flip
    # -------------------------------
    def mutacao(self, individuo):
       pass

    # -------------------------------
    # 6) Geração da nova população
    # -------------------------------
    def nova_geracao(self, selecionados):
        pass

if __name__ == "__main__":

    test = AGSimples(tamanho_populacao=100, taxa_mutacao=0.01, taxa_crossover=0.7, numero_geracoes=2000)
    test.inicializar_populacao()
    print(test.population)
    test.avaliar_populacao()
    print(test.fitness_scores)