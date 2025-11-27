from algoritmo_abstrato import AlgoritmoAbstrato
from Random_Init import random_initialize_solution
import random

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
                            prof = subject_to_prof.get(subj)
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
        for individuo in self.populacao:
            self.fitness_scores[individuo] = self.checar_restrições(individuo)

    # -------------------------------
    # 3) Seleção por torneio
    # -------------------------------
    def selecao(self):
        selecionados = []
        for _ in range(self.tamanho_populacao):
            a, b = random.sample(self.populacao, 2)
            vencedor = a if a["fitness"] > b["fitness"] else b
            selecionados.append(vencedor)
        return selecionados

    # -------------------------------
    # 4) Crossover de um ponto
    # -------------------------------
    def crossover(self, pai1, pai2):
        if random.random() > self.taxa_crossover:
            return pai1["genes"][:], pai2["genes"][:]  # sem crossover

        ponto = random.randint(1, self.tamanho_individuo - 1)
        filho1 = pai1["genes"][:ponto] + pai2["genes"][ponto:]
        filho2 = pai2["genes"][:ponto] + pai1["genes"][ponto:]
        return filho1, filho2

    # -------------------------------
    # 5) Mutação bit-flip
    # -------------------------------
    def mutacao(self, individuo):
        for i in range(len(individuo)):
            if random.random() < self.taxa_mutacao:
                individuo[i] = 1 - individuo[i]  # flip 0->1 ou 1->0
        return individuo

    # -------------------------------
    # 6) Geração da nova população
    # -------------------------------
    def nova_geracao(self, selecionados):
        nova_pop = []

        for i in range(0, self.tamanho_populacao, 2):
            pai1 = selecionados[i]
            pai2 = selecionados[(i+1) % self.tamanho_populacao]

            filho1_genes, filho2_genes = self.crossover(pai1, pai2)
            filho1_genes = self.mutacao(filho1_genes)
            filho2_genes = self.mutacao(filho2_genes)

            nova_pop.append({"genes": filho1_genes, "fitness": 0})
            nova_pop.append({"genes": filho2_genes, "fitness": 0})

        return nova_pop[:self.tamanho_populacao]

if __name__ == "__main__":

    test = AGSimples(tamanho_populacao=2, taxa_mutacao=0.01, taxa_crossover=0.7, numero_geracoes=2000)
    test.inicializar_populacao()
    print(test.population)