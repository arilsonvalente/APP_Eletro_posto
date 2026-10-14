import customtkinter as ctk
from login import LoginApp
from cadastro_usuario import cadastrar

# Janela principal
janela = ctk.CTk()
janela.title("Sistema de Gestão")
janela.geometry("720x480")
janela.minsize(650, 450)


# Funções de navegação
def abrir_login():
    LoginApp(janela, abrir_cadastro)


def abrir_cadastro():
    cadastrar(janela, abrir_login)


# Tela inicial
abrir_login()

# Executar aplicação
janela.mainloop()