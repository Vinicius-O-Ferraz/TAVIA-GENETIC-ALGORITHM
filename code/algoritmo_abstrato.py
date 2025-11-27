from abc import ABC, abstractmethod

class AlgoritmoAbstrato(ABC):

    def __init__(self, tamanho_populacao, taxa_mutacao, taxa_crossover, numero_geracoes):
        self.tamanho_populacao = tamanho_populacao
        self.taxa_mutacao = taxa_mutacao
        self.taxa_crossover = taxa_crossover
        self.numero_geracoes = numero_geracoes
        self.populacao = []


    @abstractmethod
    def inicializar_populacao(self):
        """Gera a população inicial."""
        pass

    @abstractmethod
    def avaliar_populacao(self):
        """Calcula o fitness de cada indivíduo da população."""
        pass

    @abstractmethod
    def selecao(self):
        """Seleciona indivíduos para reprodução."""
        pass

    @abstractmethod
    def crossover(self, pai1, pai2):
        """Realiza recombinação entre dois indivíduos."""
        pass

    @abstractmethod
    def mutacao(self, individuo):
        """Aplica mutação em um indivíduo."""
        pass

    @abstractmethod
    def nova_geracao(self, selecionados):
        """Gera a nova população a partir dos indivíduos selecionados."""
        pass

    def executar(self):
        """Loop principal do algoritmo genético."""
        pass
