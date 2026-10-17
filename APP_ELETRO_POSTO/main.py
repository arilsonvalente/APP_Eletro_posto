import customtkinter as ctk
from menu import Menu
from login import LoginApp
from cadastro_usuario import cadastrar
from perfil_usuario import PerfilUsuario
import database

# Inicializa o banco de dados e cria as tabelas caso ainda não existam
database.inicializar_banco()

# Janela principal
janela = ctk.CTk()
janela.title("EletroBel Postos - Gestão de Mobilidade Elétrica")
janela.geometry("1100x720")
janela.minsize(800, 500)

# Estado global da sessão do usuário
usuario_atual = None


# Funções de navegação
def definir_usuario(usuario):
    global usuario_atual
    usuario_atual = usuario


def on_login_sucesso(usuario):
    definir_usuario(usuario)
    abrir_perfil()


def abrir_login():
    LoginApp(janela, abrir_cadastro, abrir_menu, on_login_sucesso)


def abrir_cadastro():
    cadastrar(janela, abrir_login)


def abrir_perfil():
    if usuario_atual:
        PerfilUsuario(janela, usuario_atual, abrir_menu, fazer_logout)
    else:
        abrir_login()


def fazer_logout():
    definir_usuario(None)
    abrir_menu()


def abrir_menu():
    Menu(janela, abrir_login, abrir_cadastro, abrir_perfil, usuario_atual, fazer_logout)


# Tela inicial
abrir_menu()

# Executar aplicação
janela.mainloop()
