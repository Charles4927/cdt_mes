import mysql.connector
from datetime import date
from .obj_maquinas_tabelas2 import Maquinas_Tabelas


# O objetivo desta classe é filtrar por data e horario e talvez somar os dados que precisar consultar nas tabelas sql resumo
class Trazer_Dados:
    def __init__(self, setor_selecionado, maquina_selecionada, data_inicio, hora_inicio, data_fim, hora_fim):
        self.setor_selecionado = setor_selecionado
        self.maquina_selecionada = maquina_selecionada
        self.data_inicio = data_inicio
        self.hora_inicio = hora_inicio
        self.data_fim = data_fim
        self.hora_fim = hora_fim

        self.tabela_sql_resumo = Maquinas_Tabelas(self.maquina_selecionada).lista_tabelas_sql()[0][1]

    def lista_valores(self):
        # Gerando uma lista com todas as datas que pertencem ao intervalo requerido
        lista_data_inicio_e_data_fim = [self.data_inicio, self.data_fim]
        self.lista_data_inicio_ate_data_fim = []
        #Agregando a primeira data a nova lista
        self.lista_data_inicio_ate_data_fim.append(lista_data_inicio_e_data_fim[0])
        #Loop para construir a lista com as datas intermediarias
        for i in range(1, len(lista_data_inicio_e_data_fim)):
            primeiro = lista_data_inicio_e_data_fim[i-1].split('/')
            # segundo = lista_data_inicio_e_data_fim[i].split('/')
            data = date(int(primeiro[2]), int(primeiro[1]), int(primeiro[0]))
            while (data.strftime("%d/%m/%Y") != lista_data_inicio_e_data_fim[i]):
                data += date.resolution
                self.lista_data_inicio_ate_data_fim.append(data.strftime("%d/%m/%Y"))
        #Imprimindo a nova lista
        # print("lista_data_inicio_ate_data_fim:", self.lista_data_inicio_ate_data_fim)

        # Abrindo consulta no banco de dados.
        # dados_conexao = ("Driver={SQLite3 ODBC Driver};"
        #                  "Server=localhost;"
        #                  "Database=banco_cdt_mes.sqlite;")

        # dados_conexao = ("Driver={MySQL ODBC 8.1 Unicode Driver};"
        #                  "Server=10.11.1.10;"
        #                  "Database=cdtmes;"
        #                  "UID=admin;"
        #                  "PWD=Admin@Condutec;")
        # self.conexao = pyodbc.connect(dados_conexao)

        self.conexao = mysql.connector.connect(
            host='10.11.1.10',
            user='admin',
            password='Admin@Condutec',
            database='cdtmes',
        )

        self.cursor = self.conexao.cursor()

        colunas_requeridas = "producao, perdas, parada_aberta_data, parada_aberta_hora, parada_finalizada_data, parada_finalizada_hora, parada_motivo, parada_descricao, setup, ordem_de_producao, operador"

        comando_sql0 = (f"SELECT {colunas_requeridas} FROM {self.tabela_sql_resumo} WHERE data = '{self.data_inicio}' AND minuto BETWEEN '{self.hora_inicio}' AND '{self.hora_fim}'")
        comando_sql1 = (f"SELECT {colunas_requeridas} FROM {self.tabela_sql_resumo} WHERE data = '{self.data_inicio}' AND minuto BETWEEN '{self.hora_inicio}' AND '23:59'")
        comando_sql2 = (f"SELECT {colunas_requeridas} FROM {self.tabela_sql_resumo} WHERE data = '{self.data_fim}' AND minuto BETWEEN '00:00' AND '{self.hora_fim}'")
        comando_sql3 = (f"SELECT {colunas_requeridas} FROM {self.tabela_sql_resumo} WHERE data = '{i}' AND minuto BETWEEN '00:00' AND '23:59'")

        self.lista_valores_concatenados = []
        if len(self.lista_data_inicio_ate_data_fim) == 1:
            self.cursor.execute(comando_sql0)
            self.lista_valores_concatenados = self.cursor.fetchall()
            # print("lista_valores_concatenados:", self.lista_valores_concatenados)
        elif len(self.lista_data_inicio_ate_data_fim) == 2:
            self.cursor.execute(comando_sql1)
            lista_valores_somente_data_inicio = self.cursor.fetchall()

            self.cursor.execute(comando_sql2)
            lista_valores_somente_data_fim = self.cursor.fetchall()

            self.lista_valores_concatenados = lista_valores_somente_data_inicio + lista_valores_somente_data_fim
            # print("lista_valores_concatenados:", lista_valores_concatenados)
        elif len(self.lista_data_inicio_ate_data_fim) > 2:

            # Pegando valores intermediarios entre ini e fim:
            datas_intermediarias = self.lista_data_inicio_ate_data_fim[1:-1]
            # print("datas_intermediarias:", datas_intermediarias)

            lista_valores_intermediarios = []
            for i in datas_intermediarias:
                self.cursor.execute(comando_sql3)
                valores_intermediarios = self.cursor.fetchall()
                lista_valores_intermediarios.extend(valores_intermediarios)

            self.cursor.execute(comando_sql1)
            lista_valores_somente_data_inicio = self.cursor.fetchall()

            self.cursor.execute(comando_sql2)
            lista_valores_somente_data_fim = self.cursor.fetchall()

            self.cursor.close()
            self.conexao.close()

            # print("lista_valores_somente_data_inicio:", lista_valores_somente_data_inicio)
            # print("lista_valores_somente_data_fim:", self.lista_valores_somente_data_fim)
            # print("lista_valores_intermediarios:", lista_valores_intermediarios)

            self.lista_valores_concatenados = lista_valores_somente_data_inicio + lista_valores_somente_data_fim + lista_valores_intermediarios
            # print("lista_valores_concatenados:", lista_valores_concatenados)
        else:
            pass
        return self.lista_valores_concatenados

    def producao(self):
        self.lista_producao = [i[0] for i in self.lista_valores_concatenados]
        # print("lista_producao:", self.lista_producao)
        self.soma_producao = 0
        for item in self.lista_producao:
            if item:
                self.soma_producao += int(item)
        # print("self.soma_producao:", self.soma_producao)
        return self.soma_producao

    def perda(self):
        self.lista_perdas = [i[1] for i in self.lista_valores_concatenados]
        # print("lista_perdas:", self.lista_perdas)
        self.soma_perda = 0
        for item in self.lista_perdas:
            if item:
                self.soma_perda += int(item)
        # print("self.soma_perda:", self.soma_perda)
        return self.soma_perda


if __name__ == "__main__":

    setor_selecionado = "None"
    maquina_selecionada = "LX-01"
    data_inicio = "27/09/2023"
    hora_inicio = "06:52"
    data_fim = "27/09/2023"
    hora_fim = "16:30"

    argumentos = Trazer_Dados(setor_selecionado, maquina_selecionada, data_inicio, hora_inicio, data_fim, hora_fim).lista_valores()
    print("argumentos", argumentos)

# pegar_lista = (argumentos.lista_valores())
# print("pegar_lista:", pegar_lista)
#
# pegar_producao = (argumentos.producao())
# print("pegar_producao:", pegar_producao)
#
# pegar_perda = (argumentos.perda())
# print("pegar_perda:", pegar_perda)



# pecas_setup_ini = Trazer_Dados(None, maquina, parada_aberta_data, minuto_seg_zero_do_setup, parada_aberta_data,
#                                minuto_seg_exato_do_setup).producao()
# print("pecas_setup_ini:", pecas_setup_ini)