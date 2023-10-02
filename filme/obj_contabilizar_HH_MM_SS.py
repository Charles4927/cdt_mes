from datetime import datetime


# O objetivo desta classe é contabilizar tempo entre datas e horários informados
class Contabilizar_HH_MM_SS:
    def __init__(self, data_inicio, hora_inicio, data_final, hora_final):
        self.data_inicio = data_inicio
        self.hora_inicio = hora_inicio
        self.data_final = data_final
        self.hora_final = hora_final

    def contabilizar_tempo(self):
        datetime_tempo_inicial = datetime.strptime(self.data_inicio + ' ' + self.hora_inicio, '%d/%m/%Y %H:%M:%S')
        datetime_tempo_final = datetime.strptime(self.data_final + ' ' + self.hora_final, '%d/%m/%Y %H:%M:%S')
        contabilizar_tempo = datetime_tempo_final - datetime_tempo_inicial
        return contabilizar_tempo



############ Usando a classe #################

# parada_aberta_data = "14/06/2023"
# parada_aberta_hora = "10:39:27"
# parada_finalizada_data = "14/06/2023"
# parada_finalizada_hora = "13:42:42"
#
# argumentos = Contabilizar_HH_MM_SS(parada_aberta_data, parada_aberta_hora, parada_finalizada_data, parada_finalizada_hora)
#
# minutos = (argumentos.contabilizar_tempo())
# print("minutos:", minutos)