import customtkinter as ctk
from tkinter import messagebox


def LoginApp(janela, abrir_cadastro):

    for widget in janela.winfo_children():
        widget.destroy()

    frame = ctk.CTkFrame(janela)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    titulo = ctk.CTkLabel(
        frame,
        text="Bem-vindo",
        font=("Arial", 28, "bold")
    )
    titulo.pack(pady=20)

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

    def fazer_login():

        if usuario.get() == "admin" and senha.get() == "123":

            messagebox.showinfo(
                "Sucesso",
                "Login realizado com sucesso!"
            )

        else:

            messagebox.showerror(
                "Erro",
                "Usuário ou senha inválidos!"
            )

    btn_login = ctk.CTkButton(
        frame,
        text="Entrar",
        command=fazer_login
    )
    btn_login.pack(pady=10)

    btn_cadastro = ctk.CTkButton(
        frame,
        text="Cadastrar",
        fg_color="green",
        command=abrir_cadastro
    )
    btn_cadastro.pack(pady=10)