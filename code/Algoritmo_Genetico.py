from Random_Init import random_initialize_solution
import random
from Solucao import solucao
import matplotlib.pyplot as plt
import random
from abc import ABC, abstractmethod

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
        selecionados = [max(self.population, key=lambda ind: self.checar_restrições(ind))]  # Elitismo: mantém o melhor indivíduo
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
    
class ExperimentoAG:
    def __init__(self, ag_class, n_execucoes=100, max_geracoes=2000):
        self.ag_class = ag_class
        self.n_execucoes = n_execucoes
        self.max_geracoes = max_geracoes
        self.resultados = []  # Guarda dicts {'gen_found': int|None, 'time': float}

    def executar_experimentos(self):
        import time
        for i in range(self.n_execucoes):
            print(f"Execução {i+1}/{self.n_execucoes}")

            ag = self.ag_class(
                tamanho_populacao=200,
                taxa_mutacao=0.3,
                taxa_crossover=0.9,
                numero_geracoes=500
            )

            ag.inicializar_populacao()

            start = time.perf_counter()
            gen_found = None

            # Executa geração por geração
            for geracao in range(ag.numero_geracoes):
                ag.avaliar_populacao()

                # Se existe aptidão 2, registra
                if 2 in ag.fitness_scores:
                    gen_found = geracao
                    break

                selecionados = ag.selecao()
                ag.population = ag.nova_geracao(selecionados)

            elapsed = time.perf_counter() - start
            self.resultados.append({'gen_found': gen_found, 'time': elapsed})

        return self.resultados

    def plotar_resultados(self):
        # Construir listas apenas com execuções que encontraram solução
        all_execs = list(range(1, self.n_execucoes + 1))
        found_execs = []
        found_gens = []
        not_found_count = 0

        for idx, r in enumerate(self.resultados):
            gen = None
            if isinstance(r, dict):
                gen = r.get('gen_found')
            # Considera não encontrado quando None ou igual ao limite de gerações
            if gen is None or gen == self.max_geracoes:
                not_found_count += 1
            else:
                found_execs.append(idx + 1)
                found_gens.append(gen)

        plt.figure(figsize=(12,6))

        if found_execs:
            plt.scatter(found_execs, found_gens, c='tab:blue')

        plt.xlabel("Execução")
        plt.ylabel("Geração em que aptidão = 2")
        plt.title("Execuções do AG e geração onde aptidão=2 foi atingida")
        plt.grid(True)
        plt.show()

        print(f"Número de execuções que não encontraram solução: {not_found_count} de {self.n_execucoes}")

if __name__ == "__main__":
    exp = ExperimentoAG(AlgoritmoGenetico, n_execucoes=10)
    
    resultados = exp.executar_experimentos()
    print("Resultados:", resultados)

    # Calcula e exibe estatísticas solicitadas
    import statistics

    # Excluir execuções que não encontraram solução (None) ou que atingiram o máximo de gerações
    max_gen = exp.max_geracoes
    filtered = [r for r in resultados if isinstance(r, dict) and r.get('gen_found') is not None and r.get('gen_found') != max_gen]

    excluded_count = len(resultados) - len(filtered)

    times = [r['time'] for r in filtered]
    gens = [r['gen_found'] for r in filtered]

    if times:
        mean_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        var_time = statistics.pvariance(times)

        print('\nEstatísticas de Tempo (somente execuções válidas):')
        print(f'  Média tempo: {mean_time:.6f}s')
        print(f'  Menor tempo: {min_time:.6f}s')
        print(f'  Maior tempo: {max_time:.6f}s')
        print(f'  Variância tempo: {var_time:.6f}')
    else:
        print('\nEstatísticas de Tempo: nenhuma execução válida para calcular (todas falharam ou atingiram max de gerações)')

    if gens:
        mean_gen = statistics.mean(gens)
        min_gen = min(gens)
        max_gen_val = max(gens)
        var_gen = statistics.pvariance(gens)

        print('\nEstatísticas de Gerações (somente execuções válidas):')
        print(f'  Média gerações: {mean_gen:.2f}')
        print(f'  Menor geração: {min_gen}')
        print(f'  Maior geração: {max_gen_val}')
        print(f'  Variância gerações: {var_gen:.2f}')
    else:
        print('\nEstatísticas de Gerações: nenhuma execução válida para calcular (todas falharam ou atingiram max de gerações)')

    print(f"\nExecuções excluídas (não encontraram ou atingiram {max_gen}): {excluded_count} de {len(resultados)}")

    exp.plotar_resultados()