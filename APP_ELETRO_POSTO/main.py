import customtkinter as ctk
from menu import Menu
from login import LoginApp
from cadastro_usuario import cadastrar
import database

# Inicializa o banco de dados e cria as tabelas caso ainda não existam
database.inicializar_banco()

# Janela principal
janela = ctk.CTk()
janela.title("EletroBel Postos - Gestão de Mobilidade Elétrica")
janela.geometry("1100x720")
janela.minsize(800, 500)


# Funções de navegação
def abrir_login():
    LoginApp(janela, abrir_cadastro, abrir_menu)

def abrir_cadastro():
    cadastrar(janela, abrir_login)

def abrir_menu():
    Menu(janela, abrir_login, abrir_cadastro)

# Tela inicial
abrir_menu()

# Executar aplicação
janela.mainloop()