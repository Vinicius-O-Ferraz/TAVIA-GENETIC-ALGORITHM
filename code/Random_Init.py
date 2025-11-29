import os
import sys
import random

HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from Solucao import solucao
from Turma import turma
from Professores import professores


def make_turmas_from_professores(prof_dict, repeticoes=2):
    """
    Cria cópias de matérias para poder distribuí-las em múltiplos horários.
    Cada tupla em `prof_dict` deve ter a forma (materia, periodo_expected).
    Exemplo em `Professores.py`: "Taciana Pontal": [("PCO", 1), ("IHM", 1)],
    """
    turmas = []
    for prof, materias in prof_dict.items():
        for m, periodo in materias:
            for i in range(repeticoes):
                id_t = f"{m}-{i+1}"
                # cria turma com informação de semestre_letivo igual ao período esperado
                turmas.append(turma(id_t, prof, horarios=None, semestre_letivo=periodo, carga_horaria=None))
    return turmas

def agrupar_por_materia(turmas):
    """
    Agrupa as cópias, ex:
    { "PCO": [PCO-1, PCO-2], "IHM": [IHM-1, IHM-2] }
    """
    grupos = {}
    for t in turmas:
        materia = t.id_turma.split("-")[0]
        grupos.setdefault(materia, []).append(t)
    return grupos


def random_initialize_solution(sol_id=1, turmas=None, repeticoes=2):
    """
    Compatibilidade: função utilizada pelo restante do projeto.
    Gera um objeto `solucao` com turmas alocadas nos períodos correspondentes
    (usando `turma.semestre_letivo`). Quando `turmas` é None, cria turmas a
    partir do dicionário `professores`.
    """
    ri = RandomInit(repeticoes=repeticoes)
    return ri.create_solution(sol_id, turmas=turmas)


class RandomInit:
    """Helper class para inicialização aleatória respeitando períodos."""
    def __init__(self, repeticoes=2, seed=None):
        self.repeticoes = repeticoes
        self.random = random.Random(seed)

    def create_solution(self, sol_id=1, turmas=None):
        s = solucao(sol_id)

        if turmas is None:
            turmas = make_turmas_from_professores(professores, repeticoes=self.repeticoes)

        # Agrupa turmas por semestre esperado
        period_groups = {}
        for t in turmas:
            periodo = getattr(t, 'semestre_letivo', None)
            if periodo is None:
                # se não houver semestre, aloca aleatoriamente entre 1..len(periodos)
                periodo = self.random.randint(1, len(s.periodos))
            period_groups.setdefault(periodo, []).append(t)

        # Para cada período, embaralha suas turmas e preenche os slots disponíveis
        for periodo_num, turma_list in period_groups.items():
            p_idx = max(0, periodo_num - 1)
            if p_idx >= len(s.periodos):
                # período fora do alcance, pula
                continue

            periodo_obj = s.periodos[p_idx]
            # slots as list of (r,c)
            slots = [(r, c) for r in range(len(periodo_obj.matriz)) for c in range(len(periodo_obj.matriz[0]))]
            self.random.shuffle(slots)

            # Embaralha turmas e tenta alocar dentro do período correspondente
            self.random.shuffle(turma_list)
            for t, slot in zip(turma_list, slots):
                r, c = slot
                periodo_obj.matriz[r][c] = t.id_turma

        return s

def main():
    s = random_initialize_solution(sol_id=1)
    print(s)

if __name__ == '__main__':
    main()


