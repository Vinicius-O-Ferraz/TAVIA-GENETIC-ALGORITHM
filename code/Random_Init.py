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
    """
    turmas = []
    for prof, materias in prof_dict.items():
        for m in materias:
            for i in range(repeticoes):
                id_t = f"{m}-{i+1}"
                turmas.append(turma(id_t, prof, horarios=None, semestre_letivo=None, carga_horaria=None))
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
    s = solucao(sol_id)

    if turmas is None:
        turmas = make_turmas_from_professores(professores, repeticoes=repeticoes)

    # ORGANIZA as cópias por matéria
    grupos = agrupar_por_materia(turmas)

    # Mapeia cada matéria para um período fixo
    materia_para_periodo = {}
    for materia in grupos.keys():
        materia_para_periodo[materia] = random.choice(range(len(s.periodos)))

    # PARA CADA MATÉRIA:
    for materia, grupo in grupos.items():

        # pega o período escolhido
        p_idx = materia_para_periodo[materia]
        periodo = s.periodos[p_idx]

        # coleta posições livres nesse período
        slots = [(r, c) for r in range(len(periodo.matriz)) for c in range(len(periodo.matriz[0]))]
        random.shuffle(slots)

        # aloca TODAS as cópias *no mesmo período*
        for t, (r, c) in zip(grupo, slots):
            periodo.matriz[r][c] = t.id_turma

    return s

if __name__ == '__main__':
    pop = []
    for i in range(10):
        s = random_initialize_solution(sol_id=i+1, repeticoes=2)
        pop.append(s)

    print(pop)
