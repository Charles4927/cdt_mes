# Este código abaixo está funcionando perfeitamente, preciso adaptá-lo em um projeto django.
# Já consegui recriar a variável "lista" no views.py e passar para o context. Preciso saber agora como faço para criar
# um template em HTML que faça os elementos da "lista" e os botões para cada um destes elementos aparecerem na janela.
# crie um exemplo de código HTML deste template.


from tkinter import *

class Janela_Classificar_Parada(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.state("zoomed")

        lista = [('texto 1'),
                 ('texto 2'),
                 ('texto 3'),
                 ]
        lista = [elemento for elemento in lista]
        print("lista2:", lista)

        self.variaveis_lista2 = []
        for item in lista:
            label = Label(text=item)
            label.place(x=100, y=(50 + 30 * lista.index(item)))

            btn = Button(self, text="Apontar")
            btn.place(x=475, y=(50 + 30 * lista.index(item)))

Janela_Classificar_Parada().mainloop()

