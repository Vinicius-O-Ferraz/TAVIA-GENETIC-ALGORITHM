professores = {
    "Taciana Pontal": [("PCO", 1), ("IHM", 1)],
    "Rodrigo Rosal": [("FED", 1)],
    "Abner Barros": [("CIR", 1), ("ARQ", 2)],
    "Virginia Cavalcenti": [("PSI", 2)],
    "Arlley Antônio": [("PROD", 2)],
    "George Cabral": [("PROG", 2)],
    "Sheila Gomes": [("POL", 2)],
    "Bárbara Costa": [("CAL1", 3)],
    "Silas Carlos": [("PSI2", 3)],
    "Rafael Dueire ": [("MD1", 3)],
    "Maigan Stefanne": [("MD2", 3)],
    "Rinaldo José": [("BD", 3)],
    "Gustavo Callou": [("PROG2", 4)],
    "Jeane Melo": [("ALG", 4)],
    "José 1": [("CALC2", 4)],
    "Jose 2": [("DID", 4)],
    "Antônio Sistelos": [("EST", 4)],
    "Rozelma": [("MEC", 5)],
    "Pablo Sampaio": [("TCO", 5), ("SMA", 5)],
    "Kellyton Brito": [("METC", 5), ("GOVTI", 6)],
    "Douglas Veras": [("SO", 6)],
    "JOSE ALAN": [("AL", 6)],
    "Jeísa Domingues": [("REDES", 6)],
    "Paulo Anselmo": [("ESSI", 6)],
    "Lucas Figueiredo": [("TED", 7)],
    "Jeneffer Ferreira": [("PED", 7)],
    "André Câmara": [("IA", 7)],
    "Wagner Lins ": [("RET", 7)],
    "Emerson Andrade": [("EAD", 7)],
    "Lucas Albertins": [("POO", 8)],
    "Janaina Sampaio": [("LIB", 8)],
    "Marcos Cardoso": [("PSED", 8), ("EMP", 8)],
    "Ricardo Souza": [("ER", 8)],
    "Leandro Marques": [("JGD", 8)],
    "Fernando Aires": [("SEG", 8)]
}
def make_turmas_from_professores(professores_dict, repeticoes=2):
    """
    Cria cópias de matérias para poder distribuí-las em múltiplos horários.
    """
    from Turma import turma

    turmas = []
    for prof, materias in professores_dict.items():
        for m, _ in materias:
            for i in range(repeticoes):
                id_t = f"{m}-{i+1}"
                turmas.append(turma(id_t, prof, horarios=None, semestre_letivo=None, carga_horaria=None))
    return turmas

