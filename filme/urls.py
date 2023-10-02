# Definindo a url da homepage:

from django.urls import path, reverse_lazy
# Importando o objeto homepage
from .views import Homepage, Homefilmes, Detalhesfilme, Pesquisafilme, Paginaperfil, Criarconta, Pag_Form_Prod, Pag_Producao, Pag_Teste, dashboard, pagina, SuaView
from django.contrib.auth import views as auth_view

from django.urls import path
from .views import SuaView

app_name = 'filme'

urlpatterns = [
    # Chamando a função da View
    path('', Homepage.as_view(), name='homepage'),
    path('pag_form_prod/', Pag_Form_Prod.as_view(), name='pag_form_prod'),

    path('sua_view/', SuaView.as_view(), name='sua_view'),

    path('dashboard/', dashboard, name='dashboard'),
    path('pagina/', pagina, name='pagina'),
    path('pag_producao/', Pag_Producao.as_view(), name='pag_producao'),
    path('filmes/', Homefilmes.as_view(), name='homefilmes'),
    path('pag_teste/', Pag_Teste.as_view(), name='pag_teste'),
    path('filmes/<int:pk>', Detalhesfilme.as_view(), name='detalhesfilme'),
    path('pesquisa/', Pesquisafilme.as_view(), name='pesquisafilme'),
    path('login/', auth_view.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_view.LogoutView.as_view(template_name="logout.html"), name='logout'),
    path('editarperfil/<int:pk>', Paginaperfil.as_view(), name='editarperfil'),
    path('criarconta/', Criarconta.as_view(), name='criarconta'),
    path('mudarsenha/', auth_view.PasswordChangeView.as_view(template_name='editarperfil.html',
                                                             success_url=reverse_lazy('filme:homefilmes')), name='mudarsenha'),
]
