import customtkinter as ctk

from login import mostrar_login
from menu import mostrar_menu

janela = ctk.CTk()
janela.title("Sistema de Gestão")
janela.geometry("720x480")
janela.minsize(650, 450)

# funcao de navegacao entre telas

def abrir_login():
    mostrar_login(janela, abrir_menu)