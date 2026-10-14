import customtkinter as ctk
from tkinter import messagebox


def cadastrar(janela, voltar_login):

    for widget in janela.winfo_children():
        widget.destroy()

    frame = ctk.CTkFrame(janela)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    titulo = ctk.CTkLabel(
        frame,
        text="Cadastro de Usuário",
        font=("Arial", 28, "bold")
    )
    titulo.pack(pady=20)

    nome = ctk.CTkEntry(
        frame,
        placeholder_text="Nome Completo",
        width=300
    )
    nome.pack(pady=10)

    email = ctk.CTkEntry(
        frame,
        placeholder_text="E-mail",
        width=300
    )
    email.pack(pady=10)

    usuario = ctk.CTkEntry(
        frame,
        placeholder_text="Usuário",
        width=300
    )
    usuario.pack(pady=10)

    senha = ctk.CTkEntry(
        frame,
        placeholder_text="Senha",
        show="*",
        width=300
    )
    senha.pack(pady=10)

    def salvar():

        messagebox.showinfo(
            "Sucesso",
            f"Usuário {usuario.get()} cadastrado!"
        )

    btn_salvar = ctk.CTkButton(
        frame,
        text="Salvar",
        command=salvar
    )
    btn_salvar.pack(pady=10)

    btn_voltar = ctk.CTkButton(
        frame,
        text="Voltar",
        fg_color="gray",
        command=voltar_login
    )
    btn_voltar.pack(pady=10)