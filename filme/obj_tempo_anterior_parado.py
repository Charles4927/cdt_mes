from .obj_maquinas_tabelas2 import Maquinas_Tabelas
from datetime import datetime, timedelta
from .obj_conexoes_bco_dados import Conexoes_SQL
import mysql.connector


# Este objeto vai entregar hora, minutos e segundos em formato datetime ou str(sem_producao) se resultado for True:

class Tempo_Anterior_Parado:
    # 1 - inicia a função com o parâmetro especificado
    def __init__(self, self_data_inicio, self_hora_inicio, self_data_fim, self_hora_fim, self_maquina_selecionada):
        self.self_data_inicio = self_data_inicio
        self.self_hora_inicio = self_hora_inicio
        self.self_data_fim = self_data_fim
        self.self_hora_fim = self_hora_fim
        self.self_maquina_selecionada = self_maquina_selecionada

    def tempo_parado(self):
        # Definindo datatime do inicio do self:
        datetime_self_inicio = self.self_data_inicio + " " + self.self_hora_inicio
        datetime_self_inicio_date = datetime.strptime(datetime_self_inicio, '%d/%m/%Y %H:%M:%S')
        print("datetime_self_inicio_date:", datetime_self_inicio_date, type(datetime_self_inicio_date))

        # Definindo datatime do fim do self:
        datetime_self_fim = self.self_data_fim + " " + self.self_hora_fim
        datetime_self_fim_date = datetime.strptime(datetime_self_fim, '%d/%m/%Y %H:%M:%S')
        print("datetime_self_fim_date:", datetime_self_fim_date, type(datetime_self_fim_date))

        tabela_sql_resumo = Maquinas_Tabelas(self.self_maquina_selecionada).lista_tabelas_sql()[0][1]

        # Pegando a data e hora do último registro de parada na tabela_resumo correspondente a máquina em questão
        # em que os campo de parada finalizada estejam preenchidos (diferentes de "" e None):
        # dados_conexao = ("Driver={SQLite3 ODBC Driver};"
        #                  "Server=localhost;"
        #                  "Database=banco_cdt_mes.sqlite;")

        # dados_conexao = ("Driver={MySQL ODBC 8.1 Unicode Driver};"
        #                "Server=10.11.1.10;"
        #                "Database=cdtmes;"
        #                "UID=admin;"
        #                "PWD=Admin@Condutec;")
        # conexao = pyodbc.connect(dados_conexao)

        conexao = Conexoes_SQL('cdtmes').obter_conexao()

        cursor = conexao.cursor()
        comando = (f"SELECT parada_aberta_data, parada_aberta_hora, parada_finalizada_data, parada_finalizada_hora FROM {tabela_sql_resumo}")
        print("comando:", comando)
        cursor.execute(comando)
        valores = cursor.fetchall()
        cursor.close()
        conexao.close()
        # print("valores:", valores)

        # Colocar uma função, para retirar todas as datas de "valores" que forem maiores de data_self_inicio
        # retirando todos os campos none e vazio da lista
        lista_sem_none_e_vazio = [elemento for elemento in valores if elemento[0] != '' and elemento[0] is not None]
        # print("lista_sem_none_e_vazio:", lista_sem_none_e_vazio)

        lista_filtrada = []
        if not lista_sem_none_e_vazio:
            pass
            # print('Lista vazia!')
        else:
            for i in lista_sem_none_e_vazio:
                d1 = datetime.strptime(i[0] + i[1], '%d/%m/%Y%H:%M:%S')
                if d1 < datetime_self_inicio_date:
                    lista_filtrada.append(i[2:])
        # print("lista_filtrada:", lista_filtrada)

        ultimo_fechamento_de_parada = [elemento for elemento in lista_filtrada if elemento[1] != '' and elemento[1] is not None][-1]
        print("ultimo_fechamento_de_parada:", ultimo_fechamento_de_parada)

        # Gerando valor inicial a lista de resultado "return":
        lista_resultado = []

        # Condicionando "sem producao" se ultimo registro for "aberta":
        if ultimo_fechamento_de_parada[0] == "aberta":
            lista_resultado.append("sem_producao")
        else:
            # Definindo data e horario final do ultimo_fechamento_de_parada:
            datetime_ultimo_fechamento_de_parada = ultimo_fechamento_de_parada[0] + " " + ultimo_fechamento_de_parada[1]
            datetime_ultimo_fechamento_de_parada_date = datetime.strptime(datetime_ultimo_fechamento_de_parada,
                                                                          '%d/%m/%Y %H:%M:%S')
            print("datetime_ultimo_fechamento_de_parada_date:", datetime_ultimo_fechamento_de_parada_date,
                  type(datetime_ultimo_fechamento_de_parada_date))

            # Condicionando "sem_producao" se "datetime_ultimo_fechamento_de_parada_date" for maior que "datetime_self_fim_date":
            if datetime_ultimo_fechamento_de_parada_date > datetime_self_fim_date:
                lista_resultado.append("sem_producao")
            else:
                if datetime_ultimo_fechamento_de_parada_date > datetime_self_inicio_date:
                    lista_resultado.append(datetime_ultimo_fechamento_de_parada_date - datetime_self_inicio_date)
                else:
                    lista_resultado.append(timedelta())
        resultado = lista_resultado[0]
        return resultado


if __name__ == "__main__":

    # Vai receber estes valores por orientação:
    self_data_inicio = "25/07/2023"
    self_hora_inicio = "06:52:00"
    self_data_fim = "25/07/2023"
    self_hora_fim = "08:00:00"
    self_maquina_selecionada = "LX-01"

    argumentos = Tempo_Anterior_Parado(self_data_inicio, self_hora_inicio, self_data_fim, self_hora_fim, self_maquina_selecionada)
    tempo = argumentos.tempo_parado()

    print("tempo:", tempo)







# # Colocar uma função, para retirar todas as datas de "valores" que forem maiores de data_self_inicio
# # Gere um código em python para que retire da "lista" todos as tuplas em que a junção do item 0 e 1 da tupla convertidos em datetime sejam maiores que o valor da variavel "tempo" (self_inicio) em formato datetime:
# lista = [('29/05/2023', '01:30:02', '29/05/2023', '07:02:00'), (None, None, None, None), ('', '', '', ''), ('29/05/2023', '06:52:00', '29/05/2023', '08:00:00')]
#
# tempo_atual_str = str('2023-05-29 06:52:01')  # Este é para teste, apagar depois, o de baixo é o definitivo
# tempo = datetime.strptime(tempo_atual_str, "%Y-%m-%d %H:%M:%S") # Aqui está em datetime
#
# # retirando todos os campos none e vazio da lista
# lista_sem_none = [elemento for elemento in lista if elemento[0] != '' and elemento[0] is not None]
# print("lista_sem_none:", lista_sem_none)
#
# lista_filtrada = []
#
# if not lista_sem_none:
#     print('Lista vazia!')
# else:
#     for i in lista_sem_none:
#         d1 = datetime.strptime(i[0] + i[1], '%d/%m/%Y%H:%M:%S')
#         # d2 = datetime.strptime(i[2] + i[3], '%d/%m/%Y%H:%M:%S')
#
#         if d1 < tempo:
#             lista_filtrada.append(i)
#
# print(lista_filtrada)





# # Vai receber estes valores por orientação:
# self_data_inicio = "19/06/2023"
# self_hora_inicio = "06:52:00"
# self_data_fim = "19/06/2023"
# self_hora_fim = "16:30:00"
# self_maquina_selecionada = "LR-04"

        # print("lista_resultado:", lista_resultado, type(lista_resultado))
# ...
# horas_minutos_segundos_parados = tempo_total_efetivado - horas_minutos_segundos_parados
# segundos_produzindo = (
#     sum(x * int(t) for x, t in zip([3600, 60, 1], str(horas_minutos_segundos_produzindo).split(":"))))
# print("horas_minutos_segundos_produzindo:", horas_minutos_segundos_produzindo)