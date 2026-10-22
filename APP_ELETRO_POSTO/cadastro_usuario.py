import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from database import cadastrar_usuario

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

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LOGO_ELETROBEL_POSTO_NOVO.jpg")


def cadastrar(janela, voltar_login):
    """Renderiza a tela de cadastro de usuário conectada ao banco de dados."""
    for widget in janela.winfo_children():
        widget.destroy()

    janela.configure(fg_color=COLOR_BG)

    # Container principal centralizado
    main_frame = ctk.CTkFrame(janela, fg_color=COLOR_BG)
    main_frame.pack(fill="both", expand=True)

    # Card central do cadastro
    card = ctk.CTkFrame(
        main_frame,
        fg_color=COLOR_CARD_BG,
        corner_radius=16,
        border_width=1,
        border_color=COLOR_BORDER,
        width=440
    )
    card.place(relx=0.5, rely=0.5, anchor="center")

    # Header / Logomarca Centralizada
    logo_frame = ctk.CTkFrame(card, fg_color="transparent")
    logo_frame.pack(fill="x", pady=(18, 6))

    if os.path.exists(LOGO_PATH):
        try:
            img_pil = Image.open(LOGO_PATH)
            logo_img = ctk.CTkImage(
                light_image=img_pil,
                dark_image=img_pil,
                size=(210, 118)
            )
            lbl_logo = ctk.CTkLabel(logo_frame, image=logo_img, text="")
            lbl_logo.image = logo_img  # Mantém referência para evitar garbage collection
            lbl_logo.pack(anchor="center")
        except Exception:
            ctk.CTkLabel(
                logo_frame,
                text="⚡ EletroBel",
                font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                text_color=COLOR_ACCENT
            ).pack(anchor="center")
    else:
        ctk.CTkLabel(
            logo_frame,
            text="⚡ EletroBel",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLOR_ACCENT
        ).pack(anchor="center")

    ctk.CTkLabel(
        card,
        text="Criar Nova Conta",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    ).pack(anchor="center", pady=(0, 2))

    ctk.CTkLabel(
        card,
        text="Preencha os dados abaixo para se cadastrar",
        font=ctk.CTkFont(size=12),
        text_color=COLOR_TEXT_MUTED
    ).pack(anchor="center", pady=(0, 12))

    # Campos de Entrada
    def criar_label_campo(parent, texto):
        label = ctk.CTkLabel(
            parent,
            text=texto,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        label.pack(fill="x", padx=35, pady=(2, 2))
        return label

    criar_label_campo(card, "Nome Completo")
    nome = ctk.CTkEntry(
        card,
        placeholder_text="Ex: Maria Silva",
        width=360,
        height=38,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8
    )
    nome.pack(padx=35, pady=(0, 6))

    criar_label_campo(card, "E-mail")
    email = ctk.CTkEntry(
        card,
        placeholder_text="Ex: maria@email.com",
        width=360,
        height=38,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8
    )
    email.pack(padx=35, pady=(0, 6))

    criar_label_campo(card, "Telefone (opcional)")
    telefone = ctk.CTkEntry(
        card,
        placeholder_text="Ex: (11) 99999-9999",
        width=360,
        height=38,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8
    )
    telefone.pack(padx=35, pady=(0, 6))

    criar_label_campo(card, "Nome de Usuário (Login)")
    usuario = ctk.CTkEntry(
        card,
        placeholder_text="Ex: mariasilva",
        width=360,
        height=38,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8
    )
    usuario.pack(padx=35, pady=(0, 6))

    criar_label_campo(card, "Senha (mínimo 3 caracteres)")
    senha = ctk.CTkEntry(
        card,
        placeholder_text="Digite sua senha",
        show="*",
        width=360,
        height=38,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8
    )
    senha.pack(padx=35, pady=(0, 14))

    # Ação de salvar no banco de dados
    def salvar(event=None):
        n = nome.get().strip()
        e = email.get().strip()
        f = telefone.get().strip()
        u = usuario.get().strip()
        s = senha.get().strip()

        if not n or not e or not u or not s:
            messagebox.showwarning(
                "Campos Obrigatórios",
                "Por favor, preencha todos os campos para realizar o cadastro."
            )
            return

        # Chama a função de inserção do banco de dados
        sucesso, mensagem = cadastrar_usuario(
            nome=n,
            email=e,
            usuario=u,
            telefone=f,
            senha=s,
            tipo="cliente"
        )

        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            voltar_login()
        else:
            messagebox.showerror("Erro no Cadastro", mensagem)

    # Atalho com tecla Enter nos campos
    nome.bind("<Return>", salvar)
    email.bind("<Return>", salvar)
    telefone.bind("<Return>", salvar)
    usuario.bind("<Return>", salvar)
    senha.bind("<Return>", salvar)

    # Botão Salvar / Cadastrar
    btn_salvar = ctk.CTkButton(
        card,
        text="Salvar Cadastro",
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        text_color="#000000",
        corner_radius=8,
        height=40,
        width=360,
        command=salvar
    )
    btn_salvar.pack(padx=35, pady=(2, 8))

    # Botão Voltar para o Login
    btn_voltar = ctk.CTkButton(
        card,
        text="Já possui uma conta? Voltar ao Login",
        font=ctk.CTkFont(size=12),
        fg_color="transparent",
        hover_color="#182229",
        text_color=COLOR_TEXT_MUTED,
        border_width=1,
        border_color=COLOR_BORDER,
        corner_radius=8,
        height=36,
        width=360,
        command=voltar_login
    )
    btn_voltar.pack(padx=35, pady=(0, 20))


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Teste - Cadastro de Usuário")
    app.geometry("800x680")
    cadastrar(app, lambda: print("Voltar ao login pressionado"))
    app.mainloop()
