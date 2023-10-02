from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from django import forms
from datetime import timezone
import time


class FormHomepage(forms.Form):
    email = forms.EmailField(label=False)




from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field


class Formulario_da_form_prod(forms.Form):

    # opcoes_setor = [
    #     ('', ''),
    #     ('laminacao', 'Laminação'),
    #     ('forjaria', 'Forjaria'),
    #     ('dobra', 'Dobra'),
    #     ('luxor', 'Luxor'),
    # ]

    opcoes_maquina = [
        ('', ''),
        ('LX-01', 'LX-01'),
        ('LR-04', 'LR-04'),
        ('LR-05', 'LR-05'),
        # ('DC-04', 'DC-04'),
        # ('DS-03', 'DS-03'),
        # ('DW-0', 'DW-02'),
        # ('DW-03', 'DW-03'),
    ]

    # frm_setor_selecionado = forms.ChoiceField(choices=opcoes_setor, widget=forms.Select, label="Setor")
    frm_maquina_selecionada = forms.ChoiceField(choices=opcoes_maquina, widget=forms.Select, label="Máquina")

    # frm_data_inicio = forms.CharField(max_length=15)
    frm_data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=(time.strftime("%Y-%m-%d")), label="Data Início")
    frm_hora_inicio = forms.CharField(max_length=5, label="Hora Início")
    # frm_data_fim = forms.CharField(max_length=15)
    frm_data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=(time.strftime("%Y-%m-%d")), label="Data Fim")
    frm_hora_fim = forms.CharField(max_length=5, label="Hora Fim")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div('frm_maquina_selecionada', css_class='col-md-4'),
            Div('frm_data_inicio', 'frm_hora_inicio', css_class='col-md-4'),
            Div('frm_data_fim', 'frm_hora_fim', css_class='col-md-4'),
            css_class='row'
        )







class Formulario_especificar_paradas(forms.Form):

    Motivo = forms.CharField(max_length=15)
    Causa_e_Solucao = forms.CharField(max_length=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div('Motivo', css_class='col-md-6'),
            Div('Causa_e_Solucao', css_class='col-md-6'),
            css_class='row'
        )





class CriarContaForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2')