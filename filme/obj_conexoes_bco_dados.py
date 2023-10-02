import mysql.connector

class Conexoes_SQL():
    def __init__(self, database):
        self.database = database

    def obter_conexao(self):
        conexao = ""

        if self.database == "cdtmes":
            conexao = mysql.connector.connect(
                host='10.11.1.10',
                # host='177.47.167.82',
                user='admin',
                password='Admin@Condutec',
                database='cdtmes',
            )

        if self.database == "devpcp":
            conexao = mysql.connector.connect(
                host='192.168.254.83',
                # host='177.47.167.82',
                user='DEVELOPP',
                password='dev@2023',
                database='devpcp',
            )

        return conexao

if __name__ == "__main__":
    con = Conexoes_SQL('cdtmes').obter_conexao()
    print(con)