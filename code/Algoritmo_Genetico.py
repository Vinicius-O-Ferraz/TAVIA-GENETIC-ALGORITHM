from algoritmo_abstrato import AlgoritmoAbstrato
from Random_Init import random_initialize_solution
import random
from Solucao import solucao

import random
from abc import ABC, abstractmethod

# -------------------------------------
# Classe Abstrata
# -------------------------------------
class AlgoritmoGenetico(ABC):

    def __init__(self, tamanho_populacao, taxa_mutacao, taxa_crossover, numero_geracoes):
        self.tamanho_populacao = tamanho_populacao
        self.taxa_mutacao = taxa_mutacao
        self.taxa_crossover = taxa_crossover
        self.numero_geracoes = numero_geracoes
        self.populacao = []

    def inicializar_populacao(self):
        self.population = [random_initialize_solution(i) for i in range(self.tamanho_populacao)]


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
    # 3) Seleção por torneio binário
    # -------------------------------
    def selecao(self):
        """
        Realiza seleção por torneio binário.
        Para cada posição na nova população, sorteia 2 indivíduos aleatoriamente
        e seleciona aquele com maior fitness.
        Retorna um array de tamanho_populacao indivíduos selecionados para crossover.
        """
        selecionados = []
        for _ in range(self.tamanho_populacao):
            # Sorteia 2 índices aleatórios distintos
            idx1, idx2 = random.sample(range(self.tamanho_populacao), 2)
            
            # Compara fitnesses e seleciona o melhor (maior fitness)
            if self.fitness_scores[idx1] >= self.fitness_scores[idx2]:
                selecionados.append(self.population[idx1])
            else:
                selecionados.append(self.population[idx2])
        
        return selecionados

    def mutacao(self, individuo):
        """
        Corrige violações no indivíduo (objeto `solucao`) in-place.
        Estratégia:
        - Remove duplicatas dentro de um mesmo período (mantém uma ocorrência)
        - Preenche slots vazios dentro do mesmo período com matérias removidas
        - Tenta resolver conflitos de professor movendo matérias para slots livres no mesmo período
        """
        try:
            from Professores import professores as prof_dict
        except Exception:
            prof_dict = {}

        # Build subject -> professor mapping (subjects are tuples in Professores)
        subject_to_prof = {}
        for prof, subjects in prof_dict.items():
            for subj, _ in subjects:
                subject_to_prof[subj] = prof

        # 1) Remove duplicatas por período
        for periodo in individuo.periodos:
            counts = {}
            for r in periodo.matriz:
                for cell in r:
                    if cell and cell != 0:
                        counts[cell] = counts.get(cell, 0) + 1
            # remove extras (leave one)
            for subj, cnt in counts.items():
                if cnt > 1:
                    to_remove = cnt - 1
                    for i_r in range(len(periodo.matriz)):
                        for i_c in range(len(periodo.matriz[0])):
                            if to_remove <= 0:
                                break
                            if periodo.matriz[i_r][i_c] == subj:
                                # keep first occurrence, remove extras
                                periodo.matriz[i_r][i_c] = 0
                                to_remove -= 1
                        if to_remove <= 0:
                            break

        # 2) Preenche slots vazios no período com matérias removidas (se existirem)
        # Coleta matérias não alocadas (vazios serão preenchidos from pool)
        pool = []
        for periodo in individuo.periodos:
            for r in periodo.matriz:
                for cell in r:
                    if cell and cell != 0 and cell not in pool:
                        pool.append(cell)

        for periodo in individuo.periodos:
            for i_r in range(len(periodo.matriz)):
                for i_c in range(len(periodo.matriz[0])):
                    if (periodo.matriz[i_r][i_c] == 0 or periodo.matriz[i_r][i_c] is None) and pool:
                        periodo.matriz[i_r][i_c] = pool.pop(0)

        # 3) Tenta resolver conflitos de professor (mesmo slot, períodos diferentes)
        if len(individuo.periodos) > 0:
            rows = len(individuo.periodos[0].matriz)
            cols = len(individuo.periodos[0].matriz[0]) if rows > 0 else 0
            for r in range(rows):
                for c in range(cols):
                    prof_occ = {}
                    for p_idx, periodo in enumerate(individuo.periodos):
                        subj = periodo.matriz[r][c]
                        if subj and subj != 0:
                            base = subj.split("-")[0] if isinstance(subj, str) else subj
                            prof = subject_to_prof.get(base)
                            if prof:
                                prof_occ.setdefault(prof, []).append((p_idx, subj))
                    for prof, occ in prof_occ.items():
                        if len(occ) > 1:
                            # keep first occurrence, move others to other slots in same period if possible
                            for p_idx, subj in occ[1:]:
                                periodo = individuo.periodos[p_idx]
                                moved = False
                                for rr in range(len(periodo.matriz)):
                                    for cc in range(len(periodo.matriz[0])):
                                        if periodo.matriz[rr][cc] == 0 or periodo.matriz[rr][cc] is None:
                                            periodo.matriz[rr][cc] = subj
                                            # remove from original slot
                                            periodo.matriz[r][c] = 0
                                            moved = True
                                            break
                                    if moved:
                                        break

        return individuo

    def nova_geracao(self, selecionados):
        """
        Gera nova população a partir de indivíduos selecionados.
        Para cada par consecutivo faz crossover (por período) e em seguida aplica mutação.
        """
        nova = []
        # itera em pares
        for i in range(0, len(selecionados) - 1, 2):
            pai1 = selecionados[i]
            pai2 = selecionados[i+1]

            # Crossover por períodos correspondentes
            filho1 = solucao(pai1.id_solucao)
            filho2 = solucao(pai1.id_solucao)
            for p_idx in range(min(len(pai1.periodos), len(pai2.periodos))):
                per1 = pai1.periodos[p_idx]
                per2 = pai2.periodos[p_idx]
                rows = len(per1.matriz)
                cols = len(per1.matriz[0]) if rows > 0 else 0
                # máscara aleatória
                mask = [[random.randint(0,1) for _ in range(cols)] for _ in range(rows)]
                for r in range(rows):
                    for c in range(cols):
                        if mask[r][c] == 0:
                            filho1.periodos[p_idx].matriz[r][c] = per1.matriz[r][c]
                            filho2.periodos[p_idx].matriz[r][c] = per2.matriz[r][c]
                        else:
                            filho1.periodos[p_idx].matriz[r][c] = per2.matriz[r][c]
                            filho2.periodos[p_idx].matriz[r][c] = per1.matriz[r][c]

            # aplica mutação/correção
            self.mutacao(filho1)
            self.mutacao(filho2)

            nova.append(filho1)
            nova.append(filho2)

        # se lista selecionados for ímpar, copia o último
        if len(selecionados) % 2 == 1:
            ultimo = selecionados[-1]
            copia = solucao(ultimo.id_solucao)
            for p_idx, p in enumerate(ultimo.periodos):
                for r in range(len(p.matriz)):
                    for c in range(len(p.matriz[0])):
                        copia.periodos[p_idx].matriz[r][c] = p.matriz[r][c]
            self.mutacao(copia)
            nova.append(copia)

        # garante tamanho
        nova = nova[:self.tamanho_populacao]
        # atualiza população
        self.population = nova
        return nova

    def executar(self):
        self.inicializar_populacao()

        for geracao in range(self.numero_geracoes):
            self.avaliar_populacao()
            selecionados = self.selecao()
            self.population = self.nova_geracao(selecionados)

        # retorna o melhor indivíduo final
        self.avaliar_populacao()
        # retorna o objeto solucao com melhor fitness
        best_idx = max(range(len(self.fitness_scores)), key=lambda i: self.fitness_scores[i])
        return self.population[best_idx]


if __name__ == '__main__':
    # Executa AG com as configurações solicitadas
    ag = AlgoritmoGenetico(tamanho_populacao=100, taxa_mutacao=0.1, taxa_crossover=0.8, numero_geracoes=2000)
    best = ag.executar()
    # Avalia e imprime o resultado
    ag.avaliar_populacao()
    best_idx = max(range(len(ag.fitness_scores)), key=lambda i: ag.fitness_scores[i])
    print('Melhor fitness encontrado:', ag.fitness_scores[best_idx])
    print('Melhor solução:')
    print(best)
