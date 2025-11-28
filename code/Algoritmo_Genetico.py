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
    # -------------------------------
    # 4) Crossover com matriz binária 5x2
    # -------------------------------
    def crossover(self, pai1, pai2):
        """
        Realiza crossover usando uma matriz binária 5x2.
        Cada posição (r, c) da matriz representa um slot de horário:
        - 0: herda a matéria do pai1
        - 1: herda a matéria do pai2
        
        Retorna um novo indivíduo (solucao) filho.
        """
        # Se não deve fazer crossover, retorna cópia do pai1
        if random.random() > self.taxa_crossover:
            filho = solucao(pai1.id_solucao)
            # Copia a estrutura do pai1
            for p_idx, periodo_pai in enumerate(pai1.periodos):
                for r in range(len(periodo_pai.matriz)):
                    for c in range(len(periodo_pai.matriz[0])):
                        filho.periodos[p_idx].matriz[r][c] = periodo_pai.matriz[r][c]
            return filho
        
        # Gera matriz binária de máscara 2x5 (cada período tem sua máscara)
        # Usa máscara aleatória para cada período
        filho = solucao(pai1.id_solucao)
        
        for p_idx in range(len(pai1.periodos)):
            # Gera máscara binária aleatória para este período
            mascara = [[random.randint(0, 1) for _ in range(5)] for _ in range(2)]
            
            periodo_pai1 = pai1.periodos[p_idx]
            periodo_pai2 = pai2.periodos[p_idx]
            
            # Aplica a máscara: 0 = pai1, 1 = pai2
            for r in range(len(mascara)):
                for c in range(len(mascara[0])):
                    if mascara[r][c] == 0:
                        # Herda do pai1
                        filho.periodos[p_idx].matriz[r][c] = periodo_pai1.matriz[r][c]
                    else:
                        # Herda do pai2
                        filho.periodos[p_idx].matriz[r][c] = periodo_pai2.matriz[r][c]
        
        return filho

    # -------------------------------
    # 5) Mutação - correção de violações
    # -------------------------------
    def mutacao(self, individuo):
        """
        Corrige violações de restrição no indivíduo:
        1. Remove slots vazios realocando matérias aleatoriamente
        2. Remove duplicatas de matérias no mesmo período
        3. Resolve conflitos de professor no mesmo horário
        
        Modifica o indivíduo in-place e retorna ele.
        """
        try:
            from Professores import professores as prof_dict
        except Exception:
            prof_dict = {}
        
        # Build subject -> professor mapping
        subject_to_prof = {}
        for prof, subjects in prof_dict.items():
            for sub in subjects:
                subject_to_prof[sub] = prof
        
        # ==========================================
        # 1) Corrige slots vazios
        # ==========================================
        # Coleta todos os slots vazios
        empty_slots = []
        for p_idx, periodo in enumerate(individuo.periodos):
            for r in range(len(periodo.matriz)):
                for c in range(len(periodo.matriz[0])):
                    if periodo.matriz[r][c] == 0 or periodo.matriz[r][c] is None:
                        empty_slots.append((p_idx, r, c))
        
        # Coleta matérias que podem ser movidas (heurística: pega duplicatas ou aleatórias)
        subjects_to_move = []
        for p_idx, periodo in enumerate(individuo.periodos):
            counts = {}
            for r in range(len(periodo.matriz)):
                for c in range(len(periodo.matriz[0])):
                    subj = periodo.matriz[r][c]
                    if subj and subj != 0:
                        counts[subj] = counts.get(subj, 0) + 1
            
            # Se houver duplicatas neste período, marca para remoção
            for subj, cnt in counts.items():
                if cnt > 1:
                    # Remove cnt-1 instâncias
                    removed = 0
                    for r in range(len(periodo.matriz)):
                        for c in range(len(periodo.matriz[0])):
                            if removed < cnt - 1 and periodo.matriz[r][c] == subj:
                                subjects_to_move.append(subj)
                                periodo.matriz[r][c] = 0
                                removed += 1
        
        # Move matérias para slots vazios
        for subject in subjects_to_move:
            if empty_slots:
                p_idx, r, c = empty_slots.pop(0)
                individuo.periodos[p_idx].matriz[r][c] = subject
        
        # ==========================================
        # 2) Corrige conflitos de professor
        # ==========================================
        # Para cada horário (r, c), verifica conflitos de professor
        if len(individuo.periodos) > 0:
            rows = len(individuo.periodos[0].matriz)
            cols = len(individuo.periodos[0].matriz[0]) if rows > 0 else 0
            
            for r in range(rows):
                for c in range(cols):
                    prof_subjects = {}  # professor -> lista de subjects neste slot
                    
                    for p_idx, periodo in enumerate(individuo.periodos):
                        subj = periodo.matriz[r][c]
                        if subj and subj != 0:
                            base = subj.split("-")[0] if isinstance(subj, str) else subj
                            prof = subject_to_prof.get(base)
                            if prof:
                                if prof not in prof_subjects:
                                    prof_subjects[prof] = []
                                prof_subjects[prof].append((p_idx, subj))
                    
                    # Se houver professor com múltiplas matérias neste slot, remove extras
                    for prof, subjects_list in prof_subjects.items():
                        if len(subjects_list) > 1:
                            # Mantém a primeira, move as outras
                            for p_idx, subj in subjects_list[1:]:
                                # Encontra um slot vazio neste período e move
                                periodo = individuo.periodos[p_idx]
                                for r2 in range(len(periodo.matriz)):
                                    for c2 in range(len(periodo.matriz[0])):
                                        if periodo.matriz[r2][c2] == 0 or periodo.matriz[r2][c2] is None:
                                            periodo.matriz[r2][c2] = subj
                                            periodo.matriz[r][c] = 0
                                            r, c = r2, c2  # Atualiza slot ocupado
                                            break
        
        return individuo

    # -------------------------------
    # 6) Geração da nova população
    # -------------------------------
    def nova_geracao(self, selecionados):
        """
        Cria a nova geração a partir dos indivíduos selecionados.
        Realiza crossover entre pares consecutivos e mutação em cada filho.
        Retorna a nova população com tamanho_populacao indivíduos.
        """
        nova_populacao = []
        
        # Cria filhos via crossover entre pares consecutivos
        for i in range(0, len(selecionados) - 1, 2):
            pai1 = selecionados[i]
            pai2 = selecionados[i + 1]
            
            # Crossover
            filho1 = self.crossover(pai1, pai2)
            filho2 = self.crossover(pai2, pai1)
            
            # Mutação (correção de restrições)
            self.mutacao(filho1)
            self.mutacao(filho2)
            
            nova_populacao.append(filho1)
            nova_populacao.append(filho2)
        
        # Se a população tiver tamanho ímpar, cria um filho extra
        if len(selecionados) % 2 == 1:
            pai_ultimo = selecionados[-1]
            pai_anterior = selecionados[-2]
            filho_extra = self.crossover(pai_ultimo, pai_anterior)
            self.mutacao(filho_extra)
            nova_populacao.append(filho_extra)
        
        # Garante que temos exatamente tamanho_populacao indivíduos
        # (remove o excesso se houver)
        nova_populacao = nova_populacao[:self.tamanho_populacao]
        
        return nova_populacao


def executar_experimentos(runs: int = 100,
                          tamanho_pop: int = 100,
                          taxa_mut: float = 0.1,
                          taxa_cross: float = 0.8,
                          num_geracoes: int = 2000,
                          fitness_alvo: float = 2.0):
    """
    Executa o AG `runs` vezes e imprime uma tabela com a geração
    em que a solução ótima (fitness >= fitness_alvo) foi encontrada.

    Retorna a lista de gerações encontradas (int) ou -1 quando não encontrada.
    """
    results = []
    for run in range(1, runs + 1):
        ag = AGSimples(tamanho_populacao=tamanho_pop,
                       taxa_mutacao=taxa_mut,
                       taxa_crossover=taxa_cross,
                       numero_geracoes=num_geracoes)
        ag.inicializar_populacao()
        ag.avaliar_populacao()

        melhor_fitness = max(ag.fitness_scores)
        found_gen = -1

        if melhor_fitness >= fitness_alvo:
            found_gen = 0
        else:
            for geracao in range(1, num_geracoes + 1):
                selecionados = ag.selecao()
                nova_pop = ag.nova_geracao(selecionados)
                ag.population = nova_pop
                ag.avaliar_populacao()

                melhor_fitness = max(ag.fitness_scores)
                if melhor_fitness >= fitness_alvo:
                    found_gen = geracao
                    break

        results.append(found_gen)

    # Imprime tabela simples
    print("\nResultados dos experimentos:")
    print("Run\tGeração encontrada")
    for i, gen in enumerate(results, start=1):
        label = str(gen) if gen >= 0 else "Not found"
        print(f"{i}\t{label}")

    # Estatísticas básicas
    founds = [g for g in results if g >= 0]
    print()
    print(f"Runs: {runs}")
    print(f"Encontradas: {len(founds)}")
    if founds:
        print(f"Geração média (entre achadas): {sum(founds)/len(founds):.2f}")
        print(f"Geração mínima: {min(founds)}")
        print(f"Geração máxima: {max(founds)}")

    return results

if __name__ == "__main__":
    # Configuração do AG
    tamanho_pop = 100
    taxa_mut = 0.1
    taxa_cross = 0.8
    num_geracoes = 2000
    fitness_alvo = 2.0
    
    # Cria instância do AG
    ag = AGSimples(
        tamanho_populacao=tamanho_pop,
        taxa_mutacao=taxa_mut,
        taxa_crossover=taxa_cross,
        numero_geracoes=num_geracoes
    )
    
    # print("=" * 70)
    # print("ALGORITMO GENÉTICO - PROBLEMA DE AGENDAMENTO")
    # print("=" * 70)
    # print(f"Tamanho da população: {tamanho_pop}")
    # print(f"Taxa de mutação: {taxa_mut}")
    # print(f"Taxa de crossover: {taxa_cross}")
    # print(f"Máximo de gerações: {num_geracoes}")
    # print(f"Fitness alvo: {fitness_alvo}")
    # print("=" * 70)
    # print()
    
    # Inicializa população
    ag.inicializar_populacao()
    ag.avaliar_populacao()
    
    # Rastreia melhor solução encontrada
    melhor_fitness = max(ag.fitness_scores)
    melhor_solucao = ag.population[ag.fitness_scores.index(melhor_fitness)]
    
    print(f"Geração 0 (inicial):")
    print(f"  Melhor fitness: {melhor_fitness:.6f}")
    print(f"  Fitness médio: {sum(ag.fitness_scores)/len(ag.fitness_scores):.6f}")
    print(f"  Fitness mínimo: {min(ag.fitness_scores):.6f}")
    print()
    
    # Loop principal do AG
    geracao = 0
    encontrou_solucao = False
    
    for geracao in range(1, num_geracoes + 1):
        # Seleção por torneio
        selecionados = ag.selecao()
        
        # Cria nova geração
        nova_populacao = ag.nova_geracao(selecionados)
        
        # Substitui população antiga
        ag.population = nova_populacao
        
        # Avalia nova população
        ag.avaliar_populacao()
        
        # Atualiza melhor solução
        fitness_geracao = max(ag.fitness_scores)
        if fitness_geracao > melhor_fitness:
            melhor_fitness = fitness_geracao
            melhor_solucao = ag.population[ag.fitness_scores.index(melhor_fitness)]
        
        # Imprime progresso a cada 100 gerações
        # if geracao % 100 == 0 or geracao == 1:
        #     print(f"Geração {geracao}:")
        #     print(f"  Melhor fitness: {melhor_fitness:.6f}")
        #     print(f"  Fitness médio: {sum(ag.fitness_scores)/len(ag.fitness_scores):.6f}")
        #     print(f"  Fitness mínimo: {min(ag.fitness_scores):.6f}")
        #     print()
        
        # Verifica convergência (fitness == fitness_alvo)
        if melhor_fitness >= fitness_alvo:
            encontrou_solucao = True
            print(f"✓ SOLUÇÃO ÓTIMA ENCONTRADA NA GERAÇÃO {geracao}!")
            print(f"  Fitness: {melhor_fitness:.6f}")
            print("Melhor Solução Encontrada:")
            print(melhor_solucao)
            break
    
    # Resultado final
    print("=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    print(f"Gerações executadas: {geracao}")
    print(f"Melhor fitness encontrado: {melhor_fitness:.6f}")
    print(f"Fitness médio final: {sum(ag.fitness_scores)/len(ag.fitness_scores):.6f}")
    
    if encontrou_solucao:
        print("✓ Convergência alcançada (fitness = 2.0)")
    else:
        print(f"✗ Fitness alvo ({fitness_alvo}) não alcançado")
        print(f"  Diferença: {fitness_alvo - melhor_fitness:.6f}")
    
    print("=" * 70)