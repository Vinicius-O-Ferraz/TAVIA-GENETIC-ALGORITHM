from Turma import turma

class periodo:
    def __init__(self):
        self.matriz = [[0 for _ in range(5)] for _ in range(2)]

    def __repr__(self):
        return "\n".join(str(linha) for linha in self.matriz)

# periodo1 = periodo()
# print(periodo1)