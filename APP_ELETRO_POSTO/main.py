import customtkinter as ctk
from menu import Menu
from login import LoginApp
from cadastro_usuario import cadastrar

# Janela principal
janela = ctk.CTk()
janela.title("Sistema de Gestão")
janela.geometry("1920x1080")
janela.minsize(650, 450)


# Funções de navegação
def abrir_login():
    LoginApp(janela, abrir_cadastro, abrir_menu)

def abrir_cadastro():
    cadastrar(janela, abrir_login)

def abrir_menu():
    Menu(janela, abrir_login)

# Tela inicial
abrir_menu()

# Executar aplicação
janela.mainloop()