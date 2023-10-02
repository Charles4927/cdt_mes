class Maquinas_Tabelas:
    def __init__(self, cod_maquina):
        self.cod_maquina = cod_maquina

    def lista_tabelas_sql(self):

        lista1 = ('luxor_producao', 'luxor_resumo', 'luxor_alarmes', 'luxor_maquina', 'LX-01')
        lista2 = ('lam04_producao', 'lam04_resumo', 'lam04_alarmes', 'lam04_maquina', 'LR-04')
        lista3 = ('lam05_producao', 'lam05_resumo', 'lam05_alarmes', 'lam05_maquina', 'LR-05')

        qual_lista_esta = []

        if self.cod_maquina in lista1:
            qual_lista_esta.append(lista1)

        elif self.cod_maquina in lista2:
            qual_lista_esta.append(lista2)

        elif self.cod_maquina in lista3:
            qual_lista_esta.append(lista3)

        else:
            pass

        return qual_lista_esta


if __name__ == "__main__":
    lista = Maquinas_Tabelas('LX-01').lista_tabelas_sql()[0][1]
    print(lista)