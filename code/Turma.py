class turma:
    def __init__(self, id_turma, professor, horarios, semestre_letivo,carga_horaria):
        self.id_turma = id_turma
        self.horarios = horarios  
        self.professor = professor
        self.semestre_letivo = semestre_letivo
        self.carga_horaria = carga_horaria

    def __repr__(self):
        return f"{self.id_turma}"
    
# turma1 = turma("TAVIA", "Prof. Silva", '2T1', "2024.1")
# print(turma1)