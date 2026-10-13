import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

# Configuração da aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema de Login")
        self.geometry("500x600")
        self.resizable(False, False)

        # Frame Principal
        self.frame = ctk.CTkFrame(self, corner_radius=20)
        self.frame.pack(pady=30, padx=30, fill="both", expand=True)

        # Logo
        try:
            logo_img = ctk.CTkImage(
                light_image=Image.open("logo.png"),
                dark_image=Image.open("logo.png"),
                size=(150, 150)
            )

            self.logo_label = ctk.CTkLabel(
                self.frame,
                image=logo_img,
                text="C:\\Users\\63360626\\Pictures\\logo.png"
            )
            self.logo_label.pack(pady=(25, 10))

        except Exception:
            self.logo_label = ctk.CTkLabel(
                self.frame,
                text="SUA LOGOMARCA",
                font=("Arial", 26, "bold")
            )
            self.logo_label.pack(pady=(25, 10))

        # Título
        self.titulo = ctk.CTkLabel(
            self.frame,
            text="Bem-vindo",
            font=("Arial", 28, "bold")
        )
        self.titulo.pack(pady=10)

        # Campo usuário
        self.usuario = ctk.CTkEntry(
            self.frame,
            placeholder_text="Usuário",
            width=300,
            height=40
        )
        self.usuario.pack(pady=15)

        # Campo senha
        self.senha = ctk.CTkEntry(
            self.frame,
            placeholder_text="Senha",
            show="*",
            width=300,
            height=40
        )
        self.senha.pack(pady=15)

        # Checkbox
        self.lembrar = ctk.CTkCheckBox(
            self.frame,
            text="Lembrar usuário"
        )
        self.lembrar.pack(pady=10)

        # Botão Login
        self.btn_login = ctk.CTkButton(
            self.frame,
            text="Entrar",
            width=300,
            height=45,
            command=self.fazer_login
        )
        self.btn_login.pack(pady=20)

        # Botão Cadastro
        self.btn_cadastro = ctk.CTkButton(
            self.frame,
            text="Cadastrar",
            width=300,
            height=45,
            fg_color="green",
            hover_color="#006400",
            command=self.cadastrar
        )
        self.btn_cadastro.pack(pady=10)

        # Rodapé
        self.rodape = ctk.CTkLabel(
            self.frame,
            text="© 2026 - Meu Sistema",
            text_color="gray"
        )
        self.rodape.pack(side="bottom", pady=20)

    def fazer_login(self):
        usuario = self.usuario.get()
        senha = self.senha.get()

        # Exemplo simples
        if usuario == "admin" and senha == "123":
            messagebox.showinfo(
                "Sucesso",
                "Login realizado com sucesso!"
            )
        else:
            messagebox.showerror(
                "Erro",
                "Usuário ou senha inválidos!"
            )

    def cadastrar(self):
        messagebox.showinfo(
            "Cadastro",
            "Tela de cadastro em desenvolvimento."
        )


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()