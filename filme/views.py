from django.shortcuts import render, redirect, reverse
from .models import Filme, Usuario
from .forms import CriarContaForm, FormHomepage, Formulario_da_form_prod, Formulario_especificar_paradas
from django.views.generic import TemplateView, ListView, DetailView, FormView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
# Para poder importar do SQLite:
from .models import Filme
import time
from datetime import datetime, timedelta
from .obj_usar_resumo import Trazer_Dados
from .obj_maquinas_tabelas2 import Maquinas_Tabelas
from .obj_contabilizar_HH_MM_SS import Contabilizar_HH_MM_SS
from .obj_tempo_anterior_parado import Tempo_Anterior_Parado
from .obj_conexoes_bco_dados import Conexoes_SQL

# import locale
# locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')


class Homepage(FormView):
    template_name = "homepage.html"
    form_class = FormHomepage

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('filme:homefilmes')# Redireciona para a homefilmes
        else:
            return super().get(request, *args, **kwargs)# Redireciona para a homepage

    def get_success_url(self):
        email = self.request.POST.get("email")
        usuarios = Usuario.objects.filter(email=email)
        if usuarios:
            return reverse('filme:login')
        else:
            return reverse('filme:criarconta')


class Homefilmes(LoginRequiredMixin, ListView):
    template_name = "homefilmes.html"
    model = Filme
    # object_list -> lista de itens do modelo


# class Pag_Teste(LoginRequiredMixin, ListView):
#     template_name = "pag_teste.html"
#     model = Filme
#
#     def valores(self):
#         context = {}
#         context['lista'] = str("texto1")
#
#         return render(self.request, 'pag_teste.html', context)


class Pag_Teste(View):
    form_class = Formulario_especificar_paradas

    def get(self, request):
        maquina = request.GET.get('maq')
        data_ini = request.GET.get('dt_in')
        hora_ini = request.GET.get('hr_in')
        data_fim = request.GET.get('dt_fi')
        hora_fim = request.GET.get('hr_fi')

        context = {}
        context['lista'] = [maquina, data_ini, hora_ini, data_fim, hora_fim]

        # Código para conseguir lista de todas as paradas no periodo:
        # Extraindo lista com todos os valores da tabela resumo:
        dados = Trazer_Dados('setor_selecionado', maquina, data_ini, hora_ini, data_fim, hora_fim)
        lista = dados.lista_valores()
        print("lista:", lista)
        # Refazendo a lista com os indices e pegando apenas os dados de paradas necessários:
        lista_paradas = [elemento[2:-5] for elemento in lista if elemento[2] != '' and
                         elemento[2] is not None and
                         elemento[6] == None]
        lista_paradas.reverse()# Invertendo as posições dos itens
        context['lista_paradas'] = lista_paradas
        # print("lista_paradas:", lista_paradas)

        lista_formatada_paradas = []
        for i in lista_paradas:
            lista_formatada_paradas.append(f"Parada e Retorno: {i[0]} {i[1]} a {i[2]} {i[3]}")
        context['lista_formatada_paradas'] = lista_formatada_paradas

        return render(request, 'pag_teste.html', context)








    # def post(self, request):
    #     # Lógica para lidar com requisições POST
    #     context = {}
    #     context['lista'] = str("texto1")
    #     return render(request, 'pag_teste.html', context)















# class Pag_Form_Prod(FormView):
#     template_name = "pag_form_prod.html"
#     model = Formulario_da_form_prod
#     # object_list -> lista de itens do modelo


# class Pag_Form_Prod(FormView):
#     template_name = "pag_form_prod.html"
#     form_class = Formulario_da_form_prod
#
#     def form_valid(self, form):
#         # Lógica para processar o formulário válido aqui
#         return redirect('filme:pag_producao')
#
#         # return super().form_valid(form)
#
#     # def redireciona(self):
#     #     return redirect('filme:homefilmes')




class Pag_Form_Prod(LoginRequiredMixin, FormView):
    template_name = "pag_form_prod.html"
    form_class = Formulario_da_form_prod

    def form_valid(self, form):
        context = {}

        context.update(Mostra_valores_atualizados().dados(form.cleaned_data['frm_maquina_selecionada'], form.cleaned_data['frm_data_inicio'].strftime("%d/%m/%Y"), form.cleaned_data['frm_hora_inicio'], form.cleaned_data['frm_data_fim'].strftime("%d/%m/%Y"), form.cleaned_data['frm_hora_fim']))
        print(context.keys())
        print(context['mostrar_cod_maquina'])

        return render(self.request, 'pag_producao.html', context)















# class Pag_Form_Prod(FormView):
#     template_name = "pag_form_prod.html"
#     form_class = Formulario_da_form_prod
#
#     def form_valid(self, form):
#         # Lógica para processar o formulário válido aqui
#         return redirect('filme:pag_producao')










class Pag_Producao(LoginRequiredMixin, ListView):
    template_name = "pag_producao.html"
    model = Filme


class Detalhesfilme(LoginRequiredMixin, DetailView):
    template_name = "detalhesfilme.html"
    model = Filme
    # object -> 1º item do nosso modelo

    def get(self, request, *args, **kwargs):
        # Contabilizar uma visualização
        filme = self.get_object()
        filme.vizualizacoes += 1
        filme.save()
        usuario = request.user
        usuario.filmes_vistos.add(filme)
        return super().get(request, *args, **kwargs) # Redireciona o usuario para a url final

    def get_context_data(self, **kwargs):
        context = super(Detalhesfilme, self).get_context_data(**kwargs)


        filmes_relacionados = self.model.objects.filter(categoria=self.get_object().categoria)
        context["filmes_relacionados"] = filmes_relacionados
        return context


class Pesquisafilme(LoginRequiredMixin, ListView):
    template_name = "pesquisa.html"
    model = Filme

    def get_queryset(self):
        termo_pesquisa = self.request.GET.get('query')
        if termo_pesquisa:
            object_list = self.model.objects.filter(titulo__icontains=termo_pesquisa)
            return object_list
        else:
            return None


class Paginaperfil(LoginRequiredMixin, UpdateView):
    template_name = "editarperfil.html"
    model = Usuario
    field = ['first_name', 'last_name', 'email']

    def get_success_url(self):
        return reverse('filme:homefilmes')


class Criarconta(FormView):
    template_name = "criarconta.html"
    form_class = CriarContaForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('filme:login')

# # Create your views here.
# # Esta função vai indicar qual é o arquivo html a ser exibido
# def homepage(request):
#     return render(request, "homepage.html")
#
# def homefilmes(request):
#     context = {}
#     lista_filmes = Filme.objects.all()
#     context['lista_filmes'] = lista_filmes
#     return render(request, "homefilmes.html", context)











class Mostra_valores_atualizados:
    def __init__(self):
        pass
    def dados(self, maquina_selecionada, data_inicio, hora_inicio, data_fim, hora_fim):
        self.maquina_selecionada = maquina_selecionada

        self.data_inicio = data_inicio
        self.hora_inicio = hora_inicio
        self.data_fim = data_fim
        self.hora_fim = hora_fim

        tabela_sql_producao = Maquinas_Tabelas(self.maquina_selecionada).lista_tabelas_sql()[0][0]
        tabela_sql_resumo = Maquinas_Tabelas(self.maquina_selecionada).lista_tabelas_sql()[0][1]

        dicionario = {}

        dicionario['mostrar_cod_maquina'] = self.maquina_selecionada
        dicionario['mostrar_data_inicio'] = self.data_inicio
        dicionario['mostrar_hora_inicio'] = self.hora_inicio
        dicionario['mostrar_data_fim'] = self.data_fim
        dicionario['mostrar_hora_fim'] = self.hora_fim

        # mostrar_relogio_tempo_real
        # Este bloco é apenas para criar o relógio, depois apague o que for desnecessário
        valor_anterior = None
        tempo_atual_str = (time.strftime("%Y-%m-%d %H:%M:%S"))  # Aqui está em str
        tempo_atual_date = datetime.strptime(tempo_atual_str, "%Y-%m-%d %H:%M:%S")  # Aqui está em datetime
        # tempo_atras_date0 = datetime.strptime(tempo_atual_str, "%Y-%m-%d %H:%M:%S")
        tempo_atual_portug_str = datetime.strftime(tempo_atual_date, "%d/%m/%Y %H:%M:%S")
        if time.strftime("%Y-%m-%d %H:%M:%S") != valor_anterior:
            dicionario['mostrar_relogio_tempo_real'] = tempo_atual_portug_str[:16]
    
        # mostrar_hora_ultimo_ciclo
        conexao = Conexoes_SQL('cdtmes').obter_conexao()

        cursor = conexao.cursor()
    
        # Pegando todos os valores "Data, Hora" da tabela tabela_sql_producao
        comando_SELECT_tabela_sql_producao = (f"SELECT Data, Hora FROM {tabela_sql_producao}")
        cursor.execute(comando_SELECT_tabela_sql_producao)
        todos_valores_tabela_producao = cursor.fetchall()
    
        # Pegando todos os valores "temporarios" da tabela tabela_sql_resumo
        comando_SELECT_tabela_sql_resumo = (f"SELECT temporarios FROM {tabela_sql_resumo}")
        cursor.execute(comando_SELECT_tabela_sql_resumo)
        todos_valores_tabela_resumo = cursor.fetchall()
        # Decodificando os valores:
        todos_valores_temporarios_tabela_resumo_decodificados = []
        for item in todos_valores_tabela_resumo:
            todos_valores_temporarios_tabela_resumo_decodificados.append(str(item)[2:-4].split('•'))
        print("todos_valores_temporarios_tabela_resumo_decodificados:",
              todos_valores_temporarios_tabela_resumo_decodificados[-5:])
    
        cursor.close()
        conexao.close()
    
        valor_anterior = None
        if todos_valores_tabela_producao[-1:] != valor_anterior:
            dicionario['mostrar_data_ultimo_ciclo'] = str(todos_valores_tabela_producao[-1:])[3:-15]
            dicionario['mostrar_hora_ultimo_ciclo'] = str("Última Produção: ") + str(todos_valores_tabela_producao[-1:])[
                                                                           17:-3]
    
        # Mostrar status de máquina:
        ultimo_ciclo = todos_valores_tabela_producao[-1]
        ultimo_ciclo = datetime.strptime(ultimo_ciclo[0] + ' ' + ultimo_ciclo[1], '%d/%m/%Y %H:%M:%S')

        print("tempo_atual_date:", tempo_atual_date, type(tempo_atual_date))
        print("ultimo_ciclo:", ultimo_ciclo, type(ultimo_ciclo))

        diferenca = tempo_atual_date - ultimo_ciclo
        print("diferenca:", diferenca)

        total_horas = int(diferenca.total_seconds() // 3600)
        total_minutos = int(diferenca.total_seconds() % 3600) // 60
        total_segundos = int(diferenca.total_seconds() % 3600) % 60
        segundos_totais = (total_horas * 60 * 60) + (total_minutos * 60) + total_segundos
        horas_finais = segundos_totais // 3600
        minutos_finais = (segundos_totais % 3600) // 60
        segundos_finais = segundos_totais % 60
        hr_mn_sg_final = ("{:02d}:{:02d}:{:02d}".format(horas_finais, minutos_finais, segundos_finais))
        print(hr_mn_sg_final, type(hr_mn_sg_final))

        segundos_parados = (sum(x * int(t) for x, t in zip([3600, 60, 1], str(hr_mn_sg_final).split(":"))))
        print("segundos_parados:", segundos_parados)

        status_maquina = ""
        cor_status = "blue"
        if segundos_parados > 180:
            status_maquina = "Parada (a mais de 3 minutos)"
            cor_status = "#FF0000"
        else:
            status_maquina = "Produzindo"
            cor_status = "#00FF00"

        dicionario['mostrar_status_maquina'] = str(f"Máquina Atualmente {status_maquina}")
        dicionario['mostrar_cor_status'] = cor_status

        # Extraindo lista com todos os valores da tabela resumo a serem mostrados:
        dados = Trazer_Dados(None, self.maquina_selecionada, self.data_inicio, self.hora_inicio, self.data_fim, self.hora_fim)
        # Chamando todos os dados aqui de uma só vez para reduzir o processamento!
        lista_todos_os_dados_tab_resumo = dados.lista_valores()
        print("lista_todos_os_dados_tab_resumo:", lista_todos_os_dados_tab_resumo)

        # Mostrando a ordem de produção em temporarios:
        ordem_e_operador_pendente_em_temporarios = [elemento[-2:] for elemento in
                                                    todos_valores_temporarios_tabela_resumo_decodificados if
                                                    elemento[0] == 'op_operador']
        print("ordem_e_operador_pendente_em_temporarios:", ordem_e_operador_pendente_em_temporarios)

        if len(ordem_e_operador_pendente_em_temporarios) > 0:
            # Mostrando o Ordem de Produção atual:
            ordem_de_producao = ordem_e_operador_pendente_em_temporarios[0][1]
            # Mostrando o operador atual:
            operador = ordem_e_operador_pendente_em_temporarios[0][0]
        else:
            try:
                # Mostrando o Ordem de Produção atual:
                ordem_de_producao = lista_todos_os_dados_tab_resumo[-1][9]
                # Mostrando o operador atual:
                operador = lista_todos_os_dados_tab_resumo[-1][10]
            except:
                # Mostrando o Ordem de Produção atual:
                ordem_de_producao = "Não Consta"
                # Mostrando o operador atual:
                operador = "Não Consta"

        # Mostrando o Ordem de Produção atual:
        dicionario['mostrar_ordem_de_producao'] = (f"Ordem de Produção: {ordem_de_producao}")
        # Mostrando o operador atual:
        dicionario['mostrar_operador'] = operador

        # return dicionario

        # mostrar_soma_producao_bruta
        lista = [i[0] for i in lista_todos_os_dados_tab_resumo]
        soma_producao_bruta = 0
        for item in lista:
            if item:
                soma_producao_bruta += int(item)
        # valor_anterior = None
        # if soma_producao_bruta != valor_anterior:
        #     soma_producao_bruta = locale.format_string('%d', soma_producao_bruta, grouping=True)
        #     soma_producao_bruta['text'] = soma_producao_bruta


        # Mostrando a perda em temporarios:
        apontamento_perda_pendente_em_temporarios = [elemento[3] for elemento in
                                                     todos_valores_temporarios_tabela_resumo_decodificados if
                                                     elemento[0] == 'apontamento_perda']
        print("apontamento_perda_pendente_em_temporarios:", apontamento_perda_pendente_em_temporarios)

        # mostrar_perda
        #     soma_perda = int(0)
        if len(apontamento_perda_pendente_em_temporarios) > 0:
            lista = [i[1] for i in lista_todos_os_dados_tab_resumo]
            soma_perda = int(
                apontamento_perda_pendente_em_temporarios[0][0])  # Adicionando a perda em "temporarios"
            for item in lista:
                if item:
                    soma_perda += int(item)
            valor_anterior = None
            if soma_perda != valor_anterior:
                # soma_perda = locale.format_string('%d', soma_perda, grouping=True)
                dicionario['mostrar_perda'] = soma_perda
        else:
            lista = [i[1] for i in lista_todos_os_dados_tab_resumo]
            soma_perda = 0
            for item in lista:
                if item:
                    soma_perda += int(item)
            valor_anterior = None
            if soma_perda != valor_anterior:
                # soma_perda = locale.format_string('%d', soma_perda, grouping=True)
                dicionario['mostrar_perda'] = soma_perda

        # mostrar_soma_producao_liquida
        lista = [i[0] for i in lista_todos_os_dados_tab_resumo]
        soma_producao_liquida = 0 - int(soma_perda)
        for item in lista:
            if item:
                soma_producao_liquida += int(item)

        valor_anterior = None
        if soma_producao_liquida != valor_anterior:
            # soma_producao_liquida_locale = locale.format_string('%d', soma_producao_liquida, grouping=True)
            dicionario['mostrar_producao_liquida'] = soma_producao_liquida

            print("perda:", int(soma_perda))
            print("p liquida:", int(soma_producao_liquida))
            print("p bruta:", int(soma_producao_bruta), type(soma_producao_bruta))

        # informar Qualidade:
        try:
            percentual_de_producao = (int(soma_producao_liquida) / int(soma_producao_bruta)) * 100
        except ZeroDivisionError:
            percentual_de_producao = 0

        print("percentual_de_producao:", percentual_de_producao, type(percentual_de_producao))
        # porcentagem_de_qualidade_locale = locale.format_string('%.2f%%', percentual_de_producao)
        dicionario['mostrar_percentual_de_qualidade'] = "{:.2%}".format(percentual_de_producao/100)

        # # informar quantidade total de paradas
        #     lista_ini_parada = [i[3] for i in lista_todos_os_dados_tab_resumo]
        #     mostrar_qtde_total_de_paradas['text'] = len([elemento for elemento in lista_ini_parada if elemento != '' and elemento is not None])

        # informar quantidade de paradas sem Especificar
        listatd_retirando_ini_parada_igual_vazio_e_none = (
        [elemento for elemento in lista_todos_os_dados_tab_resumo if elemento[3] != '' and elemento[3] is not None])
        print(listatd_retirando_ini_parada_igual_vazio_e_none)
        listatd_pegando_parada_motivo_igual_vazio_e_none = (
        [elemento for elemento in listatd_retirando_ini_parada_igual_vazio_e_none if
         elemento[6] == '' or elemento[6] is None])
        print("listatd_pegando_parada_motivo_igual_vazio_e_none:", listatd_pegando_parada_motivo_igual_vazio_e_none)
        # mostrar_qtde_paradas_sem_Especificar ['text'] = len(listatd_pegando_parada_motivo_igual_vazio_e_none)
        if len(listatd_pegando_parada_motivo_igual_vazio_e_none) > 0:
            status = """
    Especificar
    Paradas
            """
        #     # Criando Botão que pisca
        #     self.btn5 = tk.Button(self)
        #     self.btn5.place(x=399, y=535, width=118, height=64)  # y=536 h=64
        #     self.btn5.configure(text=status, command=self.ir_para_janela_classificar_parada)
        #     self.btn5.configure(background="white", font=("Arial Rounded MT Bold", '11', 'bold'), fg="red")
        #     # self.btn5.after(200, self.alterar_cores)
        # else:
        #     pass

        # Mostrar tempo parado:
        # Pegando lista com todas as paradas:
        lista_tempo_todas_paradas_no_periodo = (
        [elemento[2:-2] for elemento in listatd_retirando_ini_parada_igual_vazio_e_none])
        # print("lista_tempo_todas_paradas_no_periodo:", lista_tempo_todas_paradas_no_periodo)

        # condição para analizar se o último valor da lista contem as strings "aberta" e trocar pelo horario atual:
        try:
            ultimoValorDaLista = lista_tempo_todas_paradas_no_periodo[-1]
            if ultimoValorDaLista[2] == 'aberta':
                lista_tempo_todas_paradas_no_periodo[-1] = ultimoValorDaLista[:2] + (
                datetime.now().strftime("%d/%m/%Y"),)
                lista_tempo_todas_paradas_no_periodo[-1] = lista_tempo_todas_paradas_no_periodo[-1][:3] + (
                datetime.now().strftime("%H:%M:%S"),)
        except:
            pass
        print("lista_tempo_todas_paradas_no_periodo:", lista_tempo_todas_paradas_no_periodo)

        # Definindo data e horario deste exato momento:
        tempo_atual_str = (time.strftime("%Y-%m-%d %H:%M:%S"))  # Aqui está em str
        tempo_atual_date = datetime.strptime(tempo_atual_str, "%Y-%m-%d %H:%M:%S")  # Aqui está em datetime
        print("tempo_atual_date:", tempo_atual_date, type(tempo_atual_date))

        somente_data_tempo_atual_date = tempo_atual_date.strftime("%d/%m/%Y")
        somente_hora_tempo_atual_date = tempo_atual_date.strftime("%H:%M:%S")

        # Definindo data e horario final do self:
        # Tiveve que adicionar ":00" na linha de baixo em 19/09/2023
        tempo_fim_do_self_str = self.data_fim + " " + self.hora_fim + ":00"
        tempo_fim_do_self_date = datetime.strptime(tempo_fim_do_self_str, '%d/%m/%Y %H:%M:%S')
        print("tempo_fim_do_self_date:", tempo_fim_do_self_date, type(tempo_fim_do_self_date))

        somente_data_tempo_fim_do_self_date = tempo_fim_do_self_date.strftime("%d/%m/%Y")
        somente_hora_tempo_fim_do_self_date = tempo_fim_do_self_date.strftime("%H:%M:%S")

        # return dicionario

        # # Chamando a janela_toplevel_setup
        # argumento_abrir_top_level_setup = Classe_Janela_Toplevel_Gerenciar_Setup(self, self.maquina_selecionada)
        #
        # def funcao_abrir_janela_toplevel_setup():
        #     argumento_abrir_top_level_setup.criar_janela_toplevel_gerenciar_setup()
        #
        # def criar_botao_setup(status):
        #     # Criando Botão Setup Desativado
        #     self.botao_setup = tk.Button(self)
        #     self.botao_setup.place(x=550, y=535, width=118, height=64)  # y=536 h=64
        #     self.botao_setup.configure(text=status, command=funcao_abrir_janela_toplevel_setup)
        #     self.botao_setup.configure(background="white", font=("Arial Rounded MT Bold", '11', 'bold'), fg="black")
        #     # self.botao_setup.after(200, self.alterar_cores)
    #
    #     # Função para aparecer o botão de setup somente se self_final for maior que data atual:
    #     if tempo_fim_do_self_date > tempo_atual_date:
    #         # Pegando os 2 ultimos status preenchidos na coluna setup:
    #         setup_registrado_minuto_atras = [elemento[8] for elemento in lista_todos_os_dados_tab_resumo[-1:]]
    #         print("setup_registrado_minuto_atras:", setup_registrado_minuto_atras)
    #
    #         texto_ativar_setup = """
    # Ativar
    # Setup
    #         """
    #
    #         texto_desativar_setup = """
    # Desativar
    # Setup
    #         """
    #
    #         if setup_registrado_minuto_atras[0] == '':
    #             status = texto_ativar_setup
    #             criar_botao_setup(status)
    #
    #         elif setup_registrado_minuto_atras == []:
    #             status = texto_ativar_setup
    #             criar_botao_setup(status)
    #
    #         elif setup_registrado_minuto_atras[0] == None:
    #             status = texto_ativar_setup
    #             criar_botao_setup(status)
    #
    #         elif setup_registrado_minuto_atras[0] == "setup_iniciado":
    #             status = texto_desativar_setup
    #             criar_botao_setup(status)
    #
    #         elif setup_registrado_minuto_atras[0] == "setup_ativo":
    #             status = texto_desativar_setup
    #             criar_botao_setup(status)
    #
    #         elif setup_registrado_minuto_atras[0] == "setup_encerrado":
    #             status = texto_ativar_setup
    #             criar_botao_setup(status)
    #
    #         else:
    #             pass

        # data final da "list..." que for <= a data atual mantem, e o que for > substitui por data_self:
        nova_lista_tempo_todas_paradas_no_periodo = []
        for valor in lista_tempo_todas_paradas_no_periodo:
            if datetime.strptime(valor[2], '%d/%m/%Y') <= datetime.strptime(somente_data_tempo_atual_date,
                                                                            '%d/%m/%Y') or datetime.strptime(
                    valor[3], '%H:%M:%S') <= datetime.strptime(somente_hora_tempo_atual_date, '%H:%M:%S'):
                nova_lista_tempo_todas_paradas_no_periodo.append(valor)
            else:
                nova_lista_tempo_todas_paradas_no_periodo.append(
                    (valor[0], valor[1], somente_data_tempo_fim_do_self_date, somente_hora_tempo_fim_do_self_date))
        # print("é a nova_lista_tempo_todas_paradas_no_periodo:", nova_lista_tempo_todas_paradas_no_periodo)

        # data final da "list..." que for <= que data_self mantem, e o que for > substitui por data_self
        nova_lista2_tempo_todas_paradas_no_periodo = []
        for valor in nova_lista_tempo_todas_paradas_no_periodo:
            if datetime.strptime(valor[2], '%d/%m/%Y') <= datetime.strptime(somente_data_tempo_fim_do_self_date,
                                                                            '%d/%m/%Y') and datetime.strptime(
                    valor[3], '%H:%M:%S') <= datetime.strptime(somente_hora_tempo_fim_do_self_date, '%H:%M:%S'):
                nova_lista2_tempo_todas_paradas_no_periodo.append(valor)
            else:
                nova_lista2_tempo_todas_paradas_no_periodo.append(
                    (valor[0], valor[1], somente_data_tempo_fim_do_self_date, somente_hora_tempo_fim_do_self_date))
        print("esta é a nova_lista2:", nova_lista2_tempo_todas_paradas_no_periodo)

        # Definindo o tempo total efetivado do turno (que realmente já passou):
        if tempo_fim_do_self_date > tempo_atual_date:
            argumentos = Contabilizar_HH_MM_SS(self.data_inicio, str(self.hora_inicio)+":00",
                                               tempo_atual_date.strftime("%d/%m/%Y"),
                                               tempo_atual_date.strftime("%H:%M:%S"))
            tempo_total_efetivado = (argumentos.contabilizar_tempo())
        else:
            argumentos = Contabilizar_HH_MM_SS(self.data_inicio, self.hora_inicio + ":00", self.data_fim, self.hora_fim + ":00")
            tempo_total_efetivado = (argumentos.contabilizar_tempo())
        print("tempo_total_efetivado:", tempo_total_efetivado, type(tempo_total_efetivado))
        segundos_efetivos = (sum(x * int(t) for x, t in zip([3600, 60, 1], str(tempo_total_efetivado).split(":"))))
        print("segundos_efetivos:", segundos_efetivos)

        # Adicione aqui o tempo anterior parado
        argumentos = Tempo_Anterior_Parado(self.data_inicio, self.hora_inicio + ":00", self.data_fim, self.hora_fim + ":00",
                                           self.maquina_selecionada)
        temp_parado = argumentos.tempo_parado()
        print("temp_parado:", temp_parado)

        # Mostrando tempo parado:
        horas_minutos_segundos_parados = timedelta()

        if temp_parado == "sem_producao":
            print("identificamos como sem_producao", temp_parado)
            horas_minutos_segundos_parados += tempo_total_efetivado
        else:
            # Descontando o "tempo anterior parado":
            horas_minutos_segundos_parados += temp_parado

        for i in nova_lista2_tempo_todas_paradas_no_periodo:
            argumentos = Contabilizar_HH_MM_SS(i[0], i[1], i[2], i[3])
            parada_de_cada_indice = argumentos.contabilizar_tempo()
            horas_minutos_segundos_parados += parada_de_cada_indice


        # Definindo o tempo produzindo:
        horas_minutos_segundos_produzindo = tempo_total_efetivado - horas_minutos_segundos_parados
        segundos_produzindo = (
            sum(x * int(t) for x, t in zip([3600, 60, 1], str(horas_minutos_segundos_produzindo).split(":"))))

        # Condição para inverter valores se acontecer o erro de constar tempo produzindo e produção 0:

        print("prod_liq: ", soma_producao_liquida, "tempo_parado: ", horas_minutos_segundos_parados, "tempo_produzindo: ", horas_minutos_segundos_produzindo)

        if soma_producao_liquida == 0 and str(horas_minutos_segundos_parados) == "0:00:00" and str(horas_minutos_segundos_produzindo) != "0:00:00":
            dicionario['mostrar_horas_minutos_segundos_parados'] = horas_minutos_segundos_produzindo
            dicionario['mostrar_horas_minutos_segundos_produzindo'] = horas_minutos_segundos_parados
        else:
            dicionario['mostrar_horas_minutos_segundos_parados'] = horas_minutos_segundos_parados
            dicionario['mostrar_horas_minutos_segundos_produzindo'] = horas_minutos_segundos_produzindo

        # Informar Disponibilidade:
        # Hr que produziu / Hr do self informado
        disponibilidade = segundos_produzindo / segundos_efetivos * 100
        print("tempo_disponibilidade:", disponibilidade)
        # tempo_disponibilidade_locale = locale.format_string('%.2f%%', disponibilidade)
        dicionario['mostrar_percentual_de_disponibilidade'] = "{:.2%}".format(disponibilidade/100)

        # Puxando o valor de peca_hora do banco sql:
        conexao = Conexoes_SQL('cdtmes').obter_conexao()

        cursor = conexao.cursor()
        comando_pegar_peca_hora = (f"SELECT temporarios FROM {tabela_sql_resumo} WHERE temporarios LIKE 'peca_hora%'")
        cursor.execute(comando_pegar_peca_hora)
        valores = cursor.fetchall()
        cursor.close()
        conexao.close()
        # Decodificando os valores:
        dados_recodificados = []
        for item in valores:
            dados_recodificados.append(str(item)[2:-4].split('•'))
        print("dados_recodificados:", dados_recodificados)
        peca_hora = dados_recodificados[0][1:]
        peca_hora = float(peca_hora[0])
        print("peca_hora:", peca_hora)
        dicionario['mostrar_peca_hora'] = int(peca_hora)

        # Informar Produtividade:
        # Pegando o "segundos_produzindo" e calcular quantar peças produziria segundo o Pç/Hora:
        # (peca_hora/60) Obtem o peça/minuto
        # (segundos_produzindo/60) Obtem o qtde minutos produzindo
        producao_teorica = (peca_hora / 60) * (segundos_produzindo / 60)
        print("producao_teorica:", producao_teorica, type(producao_teorica))

        produtividade = 0
        try:
            produtividade = soma_producao_bruta / producao_teorica
        except ZeroDivisionError:
            percentual_de_producao = 100

        print("produtividade:", produtividade, type(produtividade))
        # produtividade_locale = locale.format_string("%.2f%%", round(produtividade * 100, 2))
        print("produtividade_locale", produtividade)
        dicionario['mostrar_percentual_de_produtividade'] = "{:.2%}".format(produtividade)

        # Informar OEE:
        oee = (disponibilidade * produtividade * percentual_de_producao) / 10000

        oee_exp = str((disponibilidade * produtividade * percentual_de_producao) / 100)
        oee_exp = oee_exp.replace(",", ".")
        num_float = float(oee_exp)
        num_rounded = round(num_float, 2)
        num_formatted = "{:.2f}".format(num_rounded)
        dicionario['percentual_de_oee'] = num_formatted
        print("num_formatted:", num_formatted, type(num_formatted))

        # oee_locale = locale.format_string("%.2f%%", round(oee * 100, 2))
        # print("oee_locale:", oee_locale)
        dicionario['mostrar_percentual_de_oee'] = "{:.2%}".format(oee)

        # Informar peça/hora ultimas 100:
        # pegando os 100 ultimos pulsos
        ultimos100 = [elemento for elemento in todos_valores_tabela_producao[-100:]]
        print("len e ultimos100", len(ultimos100), ultimos100)
        # Contabilizando o tempo entre o primeiro e ultimo indice dos ultimos 100 ciclos:
        primeiro_e_ultimo_indice = [ultimos100[0], ultimos100[-1]]
        print("primeiro_e_ultimo_indice", primeiro_e_ultimo_indice)
        argumentos = Contabilizar_HH_MM_SS(primeiro_e_ultimo_indice[0][0], primeiro_e_ultimo_indice[0][1],
                                           primeiro_e_ultimo_indice[1][0], primeiro_e_ultimo_indice[1][1])
        minutos100 = (argumentos.contabilizar_tempo())
        print("minutos100:", minutos100)

        # Recalculando para não dar erro quando ultrapassar 24:00:00 hr
        total_horas = int(minutos100.total_seconds() // 3600)
        total_minutos = int(minutos100.total_seconds() % 3600) // 60
        total_segundos = int(minutos100.total_seconds() % 3600) % 60
        segundos_totais = (total_horas * 60 * 60) + (total_minutos * 60) + total_segundos
        horas_finais = segundos_totais // 3600
        minutos_finais = (segundos_totais % 3600) // 60
        segundos_finais = segundos_totais % 60
        hr_mn_sg_final = ("{:02d}:{:02d}:{:02d}".format(horas_finais, minutos_finais, segundos_finais))
        print(hr_mn_sg_final, type(hr_mn_sg_final))

        segundos_totais_100 = (sum(x * int(t) for x, t in zip([3600, 60, 1], str(hr_mn_sg_final).split(":"))))
        print("segundos_totais_100:", segundos_totais_100)

        # Pegando o tempo parado contido nos ultimos 100 ciclos
        # Pegando lista com todos os dados da tabela_resumo que ocorreram dentro do periodo especificado:
        lista_dados_para_pegar_paradas_de_100 = Trazer_Dados("setor_selecionado", self.maquina_selecionada,
                                                             primeiro_e_ultimo_indice[0][0],
                                                             primeiro_e_ultimo_indice[0][1],
                                                             primeiro_e_ultimo_indice[1][0],
                                                             primeiro_e_ultimo_indice[1][1]).lista_valores()
        print("lista_dados_para_pegar_paradas_de_100", lista_dados_para_pegar_paradas_de_100[-5:])

        # Pegando apenas dados de paradas e retirando da "lista_dados_para_pegar_paradas_de_100" os campos de paradas não preenchidos:
        lista_paradas_de_100 = ([elemento[2:-5] for elemento in lista_dados_para_pegar_paradas_de_100 if
                                 elemento[3] != '' and elemento[3] is not None])
        print("lista_paradas_de_100", lista_paradas_de_100[-5:])

        # Tratamento para mudar a finalização de parada da ultima tupla se for 'aberta', mudando assim para que receba a data e horario atuais:

        if len(lista_paradas_de_100) > 0:
            ultimoValorDalista_paradas_de_100 = lista_paradas_de_100[-1]
            print("ultimoValorDalista_paradas_de_100[2]:", ultimoValorDalista_paradas_de_100[2])
            if ultimoValorDalista_paradas_de_100[2] == 'aberta':
                lista_paradas_de_100[-1] = ultimoValorDalista_paradas_de_100[:2] + (primeiro_e_ultimo_indice[1][0],)
                # if ultimoValorDalista_paradas_de_100[3] == 'aberta':
                lista_paradas_de_100[-1] = lista_paradas_de_100[-1][:3] + (primeiro_e_ultimo_indice[1][1],)
            print(lista_paradas_de_100[-5:])

        hor_min_seg_parados_100 = timedelta()
        for i in lista_paradas_de_100:
            argumentos = Contabilizar_HH_MM_SS(i[0], i[1], i[2], i[3])
            parada_de_cada_indice = argumentos.contabilizar_tempo()
            hor_min_seg_parados_100 += parada_de_cada_indice
        print("hor_min_seg_parados_100:", hor_min_seg_parados_100)

        # Recalculando para não dar erro quando ultrapassar 24:00:00 hr
        total_horas = int(hor_min_seg_parados_100.total_seconds() // 3600)
        total_minutos = int(hor_min_seg_parados_100.total_seconds() % 3600) // 60
        total_segundos = int(hor_min_seg_parados_100.total_seconds() % 3600) % 60
        segundos_totais = (total_horas * 60 * 60) + (total_minutos * 60) + total_segundos
        horas_finais = segundos_totais // 3600
        minutos_finais = (segundos_totais % 3600) // 60
        segundos_finais = segundos_totais % 60
        hr_mn_sg_final = ("{:02d}:{:02d}:{:02d}".format(horas_finais, minutos_finais, segundos_finais))
        print(hr_mn_sg_final, type(hr_mn_sg_final))

        segundos_parados_100 = (sum(x * int(t) for x, t in zip([3600, 60, 1], str(hr_mn_sg_final).split(":"))))
        print("segundos_parados_100:", segundos_parados_100)

        # Aqui define o valor final
        # Se trocar o 'ultimos100' por outro valor, tem que atualizar aqui:
        peca_hora_ultimas_100 = (100 / (segundos_totais_100 - segundos_parados_100)) * 3600
        print("peca_hora_ultimas_100:", peca_hora_ultimas_100)
        # peca_hora_ultimas_100_locale = locale.format_string('%d', peca_hora_ultimas_100, grouping=True)
        dicionario['mostrar_peca_hora_ultimas_100'] = round(peca_hora_ultimas_100)

        dicionario['mostrar_percentual_peca_hora'] = (peca_hora_ultimas_100/peca_hora) * 100

        # # Mostrar Cliente e Produto descrição
        # # Sistema do Giovanni:
        # conexao = Conexoes_SQL('devpcp').obter_conexao()
        #
        # cursor = conexao.cursor()
        #
        # comando_pegar_pruduto_descricao = (
        #     f"SELECT nomecliente_op, produto_op FROM tab_ops where num_op = '{ordem_de_producao}'")
        # cursor.execute(comando_pegar_pruduto_descricao)
        # produto_descricao = cursor.fetchall()
        #
        # if len(produto_descricao) > 0:
        #     print("produto_descricao:", produto_descricao)
        #
        #     dicionario['mostrar_cliente'] = str(f"Cliente: {produto_descricao[0][0]}")
        #     dicionario['mostrar_produto'] = str(f"Produto: {produto_descricao[0][1]}")
        #
        # else:
        #     dicionario['mostrar_cliente'] = str("Cliente: Não Consta")
        #     dicionario['mostrar_produto'] = str("Produto: Não Consta")

        # Código provisório:
        dicionario['mostrar_cliente'] = str("Cliente: LUXOR")
        dicionario['mostrar_produto'] = str("Produto: MPBTIR22X160R")


        return dicionario









import pytz
class Dados_Producao:
    def __init__(self):
        pass
    def dados(self, tabela_producao):
        self.tabela_producao = tabela_producao

        context = {}

        conexao = Conexoes_SQL('cdtmes').obter_conexao()

        # Data e horario atuais que se atualizam (penas para usar para sabem o tempo parado de máquina)
        data_hora_atual_str = (datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%Y-%m-%d %H:%M:%S"))  # Aqui está em str
        data_hora_atual_date = datetime.strptime(data_hora_atual_str, "%Y-%m-%d %H:%M:%S")
        nova_data_hora_str = data_hora_atual_date.strftime('%d/%m/%Y %H:%M:%S')
        # print("data_hor_atual_str:", data_hora_atual_str)
        # print("data_hora_atual_date:", data_hora_atual_date)
        data_atual = data_hora_atual_str[8:10] + '/' + data_hora_atual_str[5:7] + '/' + data_hora_atual_str[0:4]
        # print("data_atual:", data_atual)

        cursor = conexao.cursor()
        comando_ciclos_do_dia_atual = (f"SELECT Data, Hora FROM {tabela_producao} where Data = '{data_atual}'")
        # print("comando_ciclos_do_dia_atual:", comando_ciclos_do_dia_atual)
        cursor.execute(comando_ciclos_do_dia_atual)
        valores_ciclos_do_dia_atual = cursor.fetchall()
        conexao.close()
        # print("valores_ciclos_do_dia_atual:", valores_ciclos_do_dia_atual)

        try:
            data_ultimo_ciclo = valores_ciclos_do_dia_atual[-1][0]
            # print("data_ultimo_ciclo:", data_ultimo_ciclo)
            hora_ultimo_ciclo = valores_ciclos_do_dia_atual[-1][1]
            # print("hora_ultimo_ciclo:", hora_ultimo_ciclo)
        except:
            data_ultimo_ciclo = str("Não houve")
            hora_ultimo_ciclo = str("Não houve")

        qtde_ciclos_do_dia_atual = len(valores_ciclos_do_dia_atual)
        # qtde_ciclos_do_dia_atual = ("{:,.3f}".format(float(qtde_ciclos_do_dia_atual0)))
        # print("qtde_ciclos_do_dia_atual:", qtde_ciclos_do_dia_atual)
        # data_ultimo_ciclo_do_dia_atual = valores_ciclos_do_dia_atual[-1][0]
        data_ultimo_ciclo_do_dia_atual = data_atual
        # print("data_ultimo_ciclo_do_dia_atual:", data_ultimo_ciclo_do_dia_atual)

        try:
            hora_primeiro_ciclo_do_dia_atual = valores_ciclos_do_dia_atual[0][1]
        except:
            hora_primeiro_ciclo_do_dia_atual = str("Não houve")
        # print("hora_primeiro_ciclo_do_dia_atual:", hora_primeiro_ciclo_do_dia_atual)

        # Apenas para usar para sabem o tempo parado de máquina:
        try:
            data_hora_ultimo_ciclo_do_dia_atual0 = str(valores_ciclos_do_dia_atual[-1])
            data_hora_ultimo_ciclo_do_dia_atual1 = data_hora_ultimo_ciclo_do_dia_atual0[
                                                   2:-14] + " " + data_hora_ultimo_ciclo_do_dia_atual0[-10:-2]
            data_hora_ultimo_ciclo_do_dia_atual = datetime.strptime(data_hora_ultimo_ciclo_do_dia_atual1,
                                                                    "%d/%m/%Y %H:%M:%S")
            # print("data_hora_ultimo_ciclo_do_dia_atual:", data_hora_ultimo_ciclo_do_dia_atual)

            tempo_entre_datas = abs(data_hora_atual_date - data_hora_ultimo_ciclo_do_dia_atual).seconds
            # print("tempo_entre_datas:", tempo_entre_datas)

            status_de_producao = ()
            if tempo_entre_datas > 180:
                status_de_producao = "Parada"
            else:
                status_de_producao = "Produzindo"
            # print("status_de_producao:", status_de_producao)
        except:
            status_de_producao = "Parada"

        context[f'{self.tabela_producao}_mostrar_data_atual'] = str(f"Primeiro Ciclo: {data_atual}")

        # context[f'{self.tabela_producao}_mostrar_data_ultimo_ciclo_do_dia_atual'] = str(data_ultimo_ciclo_do_dia_atual)

        context[f'{self.tabela_producao}_mostrar_hora_primeiro_ciclo_do_dia_atual'] = str(f"Primeiro Ciclo: {hora_primeiro_ciclo_do_dia_atual}")

        # context[f'{self.tabela_producao}_mostrar_data_ultimo_ciclo'] = str(data_ultimo_ciclo)

        context[f'{self.tabela_producao}_mostrar_hora_ultimo_ciclo'] = str(f"Último Ciclo: {hora_ultimo_ciclo}")

        # qtde_ciclos_do_dia_atual = locale.format_string('%d', qtde_ciclos_do_dia_atual, grouping=True)
        context[f'{self.tabela_producao}_mostrar_qtde_ciclos_do_dia_atual'] = str(f"Peças: {qtde_ciclos_do_dia_atual}")
        context[f'{self.tabela_producao}_mostrar_pecas'] = str(f"{qtde_ciclos_do_dia_atual}")

        context[f'{self.tabela_producao}_mostrar_status_de_producao'] = str(f"Status: {status_de_producao}")

        context['mostrar_data_hora_atual'] = str(f"Atualização: {nova_data_hora_str}")

        # context['pecas'] = [50, 100, 150, 200, 250, 300, 350]

        return context


def dashboard(request):
    lista_tabelas = ["luxor_producao", "lam04_producao", "lam05_producao", "dc04_producao", "ds03_producao", "dw02_producao", "dw03_producao"]
    lista_dados = {}
    for item in lista_tabelas:
        lista_dados.update(Dados_Producao().dados(item))
    # print(lista_dados)
    # context[f'{self.tabela_producao}_mostrar_pecas'] = str(f"Peças: {qtde_ciclos_do_dia_atual}")

    return render(request, "dashboard.html", lista_dados)






# função para do views para
def pagina(request):
    context = {}
    context['valor1'] = "volor1_obtido"
    context['mostrar_hora_ultimo_ciclo'] = datetime.now(pytz.timezone('America/Sao_Paulo'))
    return render(request, "pagina.html", context)


from django.http import JsonResponse
from django.views import View
from datetime import datetime
import pytz

class SuaView(View):
    def get(self, request):
        mostrar_hora_ultimo_ciclo = datetime.now(pytz.timezone('America/Sao_Paulo'))
        return JsonResponse({'mostrar_hora_ultimo_ciclo': mostrar_hora_ultimo_ciclo.strftime('%Y-%m-%d %H:%M:%S %Z%z')})






# função para obter o valor atualizado de mostrar_hora_ultimo_ciclo
from django.http import JsonResponse
def usar_ajax(request):
    mostrar_hora_ultimo_ciclo = "08:01:00"
    return JsonResponse({'mostrar_hora_ultimo_ciclo': mostrar_hora_ultimo_ciclo})
