import os
import sys
import random

HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from Solucao import solucao
from Turma import turma
from Professores import professores


def make_turmas_from_professores(prof_dict):
    """Cria uma lista de objetos `turma` a partir do dicionário de professores.

    Cada par (professor, materia) vira uma turma com id formatado como "MATERIA - PROFESSOR".
    Horários, semestre e carga ficam como None por padrão; ajuste conforme necessário.
    """
    turmas = []
    for prof, materias in prof_dict.items():
        for m in materias:
            id_t = f"{m}"
            turmas.append(turma(id_t, prof, horarios=None, semestre_letivo=None, carga_horaria=None))
    return turmas


def random_initialize_solution(sol_id=1, turmas=None):
    s = solucao(sol_id)

    if turmas is None:
        turmas = make_turmas_from_professores(professores)

    slots = []
    for p_idx, p in enumerate(s.periodos):
        rows = len(p.matriz)
        cols = len(p.matriz[0]) if rows > 0 else 0
        for r in range(rows):
            for c in range(cols):
                slots.append((p_idx, r, c))

    random.shuffle(slots)

    for i, t in enumerate(turmas):
        if i >= len(slots):
            break
        p_idx, r, c = slots[i]
        s.periodos[p_idx].matriz[r][c] = t.id_turma
    return s

def main():
    s = random_initialize_solution(sol_id=1)

if __name__ == '__main__':
    main()
