from src.simulation.program import programa
from src.simulation.utils import drp_drc_define


class Particle:
    def __init__(self, potencias, constante_energia, start_case=False,pot_total=0, num_baterias=1):
        """
                potencias: lista de floats (potência em cada barra)
                constante_energia: inteiro
                """
        self.simulacao = None
        self.drcs = None
        self.drps = None
        self.start_case = start_case
        self.num_baterias = num_baterias

        if start_case:
            self.potencias = []
            self.constante_energia = 0
            self.storage_specs = None
            self.pot_total = 0
        else:
            self.potencias = [int(p) for p in potencias]
            self.constante_energia = int(round(constante_energia))
            self.storage_specs = self.get_storage_specs(2)
            self.pot_total = pot_total


    def arredondar_potencias(self):
        """Arredonda todas as potências para múltiplos de 5."""
        self.potencias = [int(p) for p in self.potencias]

    def get_storage_specs(self,limiar):
        """
               Retorna uma lista de especificações das baterias ativas:
               [(indice_barra, potencia, constante_energia), ...]
               Apenas barras com potência >= limiar são consideradas.
        """
        specs = []

        for idx, p in enumerate(self.potencias):
            if p >= limiar:
                specs.append([idx,p, self.constante_energia*p])
        return specs

    def simular(self):
        if self.start_case:
            self.simulacao =  programa()
        else:
            self.simulacao = programa(option="with-gd-storage", storage_specs=self.storage_specs)
        self.drps, self.drcs = drp_drc_define(self.simulacao['v_indicators'])