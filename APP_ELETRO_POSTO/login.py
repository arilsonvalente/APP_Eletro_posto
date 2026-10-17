import customtkinter as ctk
from tkinter import messagebox
from database import autenticar_usuario

# Paleta de cores EletroBel
COLOR_BG = "#0B0F12"
COLOR_CARD_BG = "#13191E"
COLOR_ACCENT = "#00FF66"
COLOR_ACCENT_HOVER = "#00CC52"
COLOR_BORDER = "#1E2A32"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_MUTED = "#8B9DAA"
COLOR_INPUT_BG = "#182229"
COLOR_INPUT_BORDER = "#253440"


def LoginApp(janela, abrir_cadastro, abrir_menu, on_login_sucesso=None):
    """Renderiza a tela de login conectada ao banco de dados."""
    for widget in janela.winfo_children():
        widget.destroy()

    janela.configure(fg_color=COLOR_BG)

    # Frame principal para centralização
    main_frame = ctk.CTkFrame(janela, fg_color=COLOR_BG)
    main_frame.pack(fill="both", expand=True)

    # Card central de login
    card = ctk.CTkFrame(
        main_frame,
        fg_color=COLOR_CARD_BG,
        corner_radius=16,
        border_width=1,
        border_color=COLOR_BORDER,
        width=420
    )
    card.place(relx=0.5, rely=0.5, anchor="center")

    # Header / Logo
    logo_frame = ctk.CTkFrame(card, fg_color="transparent")
    logo_frame.pack(pady=(30, 5))

    ctk.CTkLabel(
        logo_frame,
        text="⚡",
        font=ctk.CTkFont(size=30, weight="bold"),
        text_color=COLOR_ACCENT
    ).pack(side="left", padx=(0, 8))

    ctk.CTkLabel(
        logo_frame,
        text="EletroBel",
        font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    ).pack(side="left")

    ctk.CTkLabel(
        card,
        text="Acesse sua Conta",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    ).pack(pady=(2, 4))

    ctk.CTkLabel(
        card,
        text="Entre com suas credenciais cadastradas",
        font=ctk.CTkFont(size=12),
        text_color=COLOR_TEXT_MUTED
    ).pack(pady=(0, 20))

    # Campo Usuário
    ctk.CTkLabel(
        card,
        text="Usuário",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLOR_TEXT_MUTED,
        anchor="w"
    ).pack(fill="x", padx=35, pady=(4, 2))

    usuario = ctk.CTkEntry(
        card,
        placeholder_text="Digite seu usuário",
        width=340,
        height=40,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8
    )
    usuario.pack(padx=35, pady=(0, 10))

    # Campo Senha
    ctk.CTkLabel(
        card,
        text="Senha",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLOR_TEXT_MUTED,
        anchor="w"
    ).pack(fill="x", padx=35, pady=(4, 2))

    senha = ctk.CTkEntry(
        card,
        placeholder_text="Digite sua senha",
        show="*",
        width=340,
        height=40,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8
    )
    senha.pack(padx=35, pady=(0, 18))

    def fazer_login(event=None):
        u = usuario.get().strip()
        s = senha.get().strip()

        if not u or not s:
            messagebox.showwarning(
                "Atenção",
                "Por favor, informe seu usuário e sua senha."
            )
            return

        # Consulta no banco de dados SQLite
        usuario_autenticado = autenticar_usuario(u, s)

        if usuario_autenticado:
            messagebox.showinfo(
                "Sucesso",
                f"Login realizado com sucesso!\nBem-vindo(a), {usuario_autenticado['nome']}!"
            )
            if on_login_sucesso:
                on_login_sucesso(usuario_autenticado)
            else:
                abrir_menu()
        else:
            messagebox.showerror(
                "Erro de Login",
                "Usuário ou senha incorretos!\nVerifique os dados ou realize um cadastro."
            )

    # Permite pressionar Enter para logar
    usuario.bind("<Return>", fazer_login)
    senha.bind("<Return>", fazer_login)

    # Botão Entrar
    btn_login = ctk.CTkButton(
        card,
        text="Entrar",
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        text_color="#000000",
        corner_radius=8,
        height=42,
        width=340,
        command=fazer_login
    )
    btn_login.pack(padx=35, pady=(4, 10))

    # Botão Cadastrar
    btn_cadastro = ctk.CTkButton(
        card,
        text="Criar nova conta",
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color="transparent",
        hover_color="#182229",
        text_color=COLOR_ACCENT,
        border_width=1,
        border_color=COLOR_ACCENT,
        corner_radius=8,
        height=38,
        width=340,
        command=abrir_cadastro
    )
    btn_cadastro.pack(padx=35, pady=(0, 8))

    # Botão Voltar ao Menu Inicial
    btn_menu = ctk.CTkButton(
        card,
        text="Voltar à Tela Inicial",
        font=ctk.CTkFont(size=12),
        fg_color="transparent",
        hover_color="#182229",
        text_color=COLOR_TEXT_MUTED,
        border_width=1,
        border_color=COLOR_BORDER,
        corner_radius=8,
        height=36,
        width=340,
        command=abrir_menu
    )
    btn_menu.pack(padx=35, pady=(0, 25))


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Teste - Login")
    app.geometry("800x600")
    LoginApp(app, lambda: print("Abrir cadastro"), lambda: print("Abrir menu"))
    app.mainloop()