from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.

campos = list(UserAdmin.fieldsets)
campos.append(
    ("Histórico", {'fields': ('filmes_vistos',)})
)
UserAdmin.fieldsets = tuple(campos)

# Trazendo o acesso da tabela Filme para a area adm
from .models import Filme, Episodio, Usuario
admin.site.register(Filme)
admin.site.register(Episodio)
admin.site.register(Usuario, UserAdmin)

# [
#     ("Informações Pessoais", {'fields': ('Primeiro nome', 'Último nome',)})
# ]