import json
import os
import customtkinter as ctk
from tkinter import messagebox
from database import (
    autenticar_usuario,
    garantir_usuario_admin,
    redefinir_senha_usuario,
)

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

# Credenciais padrão do Usuário Administrador
ADMIN_USUARIO = "admin"
ADMIN_SENHA = "admin123"
ADMIN_PERFIL_PADRAO = {
    "id": 1,
    "nome": "Administrador EletroBel",
    "email": "admin@eletrobel.com",
    "usuario": ADMIN_USUARIO,
    "tipo": "admin",
}

# Arquivo local para persistência da função "Me lembrar"
LEMBRAR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".lembrar_login.json")


def me_lembrar(salvar: bool = False, usuario_str: str = "", senha_str: str = ""):
    """
    Gerencia a função 'Me lembrar' do login:
    - Se `salvar=True`, persiste as credenciais lembradas em disco.
    - Se `salvar=False` e forem passados argumentos vazios, limpa ou carrega o estado salvo.
    """
    try:
        if salvar:
            dados = {
                "lembrar": True,
                "usuario": usuario_str.strip(),
                "senha": senha_str,
            }
            with open(LEMBRAR_FILE, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            return dados
        else:
            if os.path.exists(LEMBRAR_FILE):
                os.remove(LEMBRAR_FILE)
            return {"lembrar": False, "usuario": "", "senha": ""}
    except Exception:
        return {"lembrar": False, "usuario": "", "senha": ""}


def carregar_me_lembrar():
    """Carrega os dados salvos pela função 'Me lembrar', se existirem."""
    try:
        if os.path.exists(LEMBRAR_FILE):
            with open(LEMBRAR_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if isinstance(dados, dict) and dados.get("lembrar"):
                return {
                    "lembrar": True,
                    "usuario": str(dados.get("usuario", "")),
                    "senha": str(dados.get("senha", "")),
                }
    except Exception:
        pass
    return {"lembrar": False, "usuario": "", "senha": ""}


def esqueci_senha(janela_pai, entry_usuario_login=None):
    """
    Abre o modal 'Esqueci minha senha' permitindo ao usuário redefinir sua senha
    informando seu nome de usuário ou e-mail cadastrado.
    """
    modal = ctk.CTkToplevel(janela_pai)
    modal.title("EletroBel - Recuperação de Senha")
    modal.geometry("420x430")
    modal.resizable(False, False)
    modal.configure(fg_color=COLOR_BG)
    modal.transient(janela_pai)
    modal.grab_set()

    card_rec = ctk.CTkFrame(
        modal,
        fg_color=COLOR_CARD_BG,
        corner_radius=14,
        border_width=1,
        border_color=COLOR_BORDER,
    )
    card_rec.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        card_rec,
        text="🔑 Esqueci Minha Senha",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=COLOR_TEXT_MAIN,
    ).pack(pady=(20, 4))

    ctk.CTkLabel(
        card_rec,
        text="Informe seu usuário ou e-mail para criar uma nova senha",
        font=ctk.CTkFont(size=12),
        text_color=COLOR_TEXT_MUTED,
    ).pack(pady=(0, 16))

    # Campo Usuário ou E-mail
    ctk.CTkLabel(
        card_rec,
        text="Usuário ou E-mail",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLOR_TEXT_MUTED,
        anchor="w",
    ).pack(fill="x", padx=28, pady=(2, 2))

    entry_ident = ctk.CTkEntry(
        card_rec,
        placeholder_text="Ex: admin ou email@dominio.com",
        width=320,
        height=38,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8,
    )
    entry_ident.pack(padx=28, pady=(0, 10))

    if entry_usuario_login and entry_usuario_login.get().strip():
        entry_ident.insert(0, entry_usuario_login.get().strip())

    # Campo Nova Senha
    ctk.CTkLabel(
        card_rec,
        text="Nova Senha",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLOR_TEXT_MUTED,
        anchor="w",
    ).pack(fill="x", padx=28, pady=(2, 2))

    entry_nova_senha = ctk.CTkEntry(
        card_rec,
        placeholder_text="Digite a nova senha (mín. 3 caracteres)",
        show="*",
        width=320,
        height=38,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8,
    )
    entry_nova_senha.pack(padx=28, pady=(0, 10))

    # Campo Confirmar Nova Senha
    ctk.CTkLabel(
        card_rec,
        text="Confirmar Nova Senha",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLOR_TEXT_MUTED,
        anchor="w",
    ).pack(fill="x", padx=28, pady=(2, 2))

    entry_confirmar = ctk.CTkEntry(
        card_rec,
        placeholder_text="Repita a nova senha",
        show="*",
        width=320,
        height=38,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8,
    )
    entry_confirmar.pack(padx=28, pady=(0, 18))

    def confirmar_redefinicao(event=None):
        identificador = entry_ident.get().strip()
        nova_s = entry_nova_senha.get().strip()
        conf_s = entry_confirmar.get().strip()

        if not identificador or not nova_s or not conf_s:
            messagebox.showwarning(
                "Campos Obrigatórios",
                "Preencha todos os campos para redefinir sua senha.",
                parent=modal,
            )
            return

        if nova_s != conf_s:
            messagebox.showerror(
                "Senhas Diferentes",
                "A nova senha e a confirmação não coincidem!",
                parent=modal,
            )
            return

        sucesso, msg = redefinir_senha_usuario(identificador, nova_s)
        if sucesso:
            messagebox.showinfo("Senha Atualizada", msg, parent=modal)
            if entry_usuario_login and not entry_usuario_login.get().strip():
                entry_usuario_login.insert(0, identificador)
            modal.destroy()
        else:
            messagebox.showerror("Não foi possível redefinir", msg, parent=modal)

    entry_confirmar.bind("<Return>", confirmar_redefinicao)

    ctk.CTkButton(
        card_rec,
        text="Redefinir Senha",
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        text_color="#000000",
        corner_radius=8,
        height=38,
        width=320,
        command=confirmar_redefinicao,
    ).pack(padx=28, pady=(0, 8))

    ctk.CTkButton(
        card_rec,
        text="Cancelar",
        font=ctk.CTkFont(size=12),
        fg_color="transparent",
        hover_color="#182229",
        text_color=COLOR_TEXT_MUTED,
        border_width=1,
        border_color=COLOR_BORDER,
        corner_radius=8,
        height=34,
        width=320,
        command=modal.destroy,
    ).pack(padx=28, pady=(0, 14))


def LoginApp(janela, abrir_cadastro, abrir_menu, on_login_sucesso=None):
    """Renderiza a tela de login conectada ao banco de dados."""
    for widget in janela.winfo_children():
        widget.destroy()

    # Garante que o usuário Administrador (admin / admin123) esteja registrado no banco
    garantir_usuario_admin(ADMIN_USUARIO, ADMIN_SENHA)

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
        width=420,
    )
    card.place(relx=0.5, rely=0.5, anchor="center")

    # Header / Logo
    logo_frame = ctk.CTkFrame(card, fg_color="transparent")
    logo_frame.pack(pady=(28, 5))

    ctk.CTkLabel(
        logo_frame,
        text="⚡",
        font=ctk.CTkFont(size=30, weight="bold"),
        text_color=COLOR_ACCENT,
    ).pack(side="left", padx=(0, 8))

    ctk.CTkLabel(
        logo_frame,
        text="EletroBel",
        font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
        text_color=COLOR_TEXT_MAIN,
    ).pack(side="left")

    ctk.CTkLabel(
        card,
        text="Acesse sua Conta",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=COLOR_TEXT_MAIN,
    ).pack(pady=(2, 4))

    ctk.CTkLabel(
        card,
        text="Entre com suas credenciais cadastradas",
        font=ctk.CTkFont(size=12),
        text_color=COLOR_TEXT_MUTED,
    ).pack(pady=(0, 18))

    # Campo Usuário
    ctk.CTkLabel(
        card,
        text="Usuário",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLOR_TEXT_MUTED,
        anchor="w",
    ).pack(fill="x", padx=35, pady=(4, 2))

    usuario = ctk.CTkEntry(
        card,
        placeholder_text="Digite seu usuário (ex: admin)",
        width=340,
        height=40,
        fg_color=COLOR_INPUT_BG,
        border_color=COLOR_INPUT_BORDER,
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8,
    )
    usuario.pack(padx=35, pady=(0, 10))

    # Campo Senha
    ctk.CTkLabel(
        card,
        text="Senha",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLOR_TEXT_MUTED,
        anchor="w",
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
        corner_radius=8,
    )
    senha.pack(padx=35, pady=(0, 8))

    # Barra de opções: "Me lembrar" (esquerda) e "Esqueci senha" (direita)
    opcoes_frame = ctk.CTkFrame(card, fg_color="transparent", width=340)
    opcoes_frame.pack(fill="x", padx=35, pady=(2, 14))

    dados_lembrados = carregar_me_lembrar()
    lembrar_var = ctk.BooleanVar(value=dados_lembrados.get("lembrar", False))

    if dados_lembrados.get("lembrar"):
        if dados_lembrados.get("usuario"):
            usuario.insert(0, dados_lembrados["usuario"])
        if dados_lembrados.get("senha"):
            senha.insert(0, dados_lembrados["senha"])

    def ao_alternar_lembrar():
        if not lembrar_var.get():
            me_lembrar(salvar=False)

    chk_lembrar = ctk.CTkCheckBox(
        opcoes_frame,
        text="Me lembrar",
        variable=lembrar_var,
        command=ao_alternar_lembrar,
        font=ctk.CTkFont(size=12),
        text_color=COLOR_TEXT_MUTED,
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        checkmark_color="#000000",
         border_color=COLOR_INPUT_BORDER,
        checkbox_width=18,
        checkbox_height=18,
    )
    chk_lembrar.pack(side="left")

    btn_esqueci_senha = ctk.CTkButton(
        opcoes_frame,
        text="Esqueci minha senha?",
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color="transparent",
        hover_color="#182229",
        text_color=COLOR_ACCENT,
        width=130,
        height=24,
        anchor="e",
        command=lambda: esqueci_senha(janela, usuario),
    )
    btn_esqueci_senha.pack(side="right")

    def fazer_login(event=None):
        u = usuario.get().strip()
        s = senha.get().strip()

        if not u or not s:
            messagebox.showwarning(
                "Atenção",
                "Por favor, informe seu usuário e sua senha.",
            )
            return

        # Consulta no banco de dados MySQL
        usuario_autenticado = autenticar_usuario(u, s)

        # Validação direta do Administrador padrão ("admin" / "admin123")
        if not usuario_autenticado and u.lower() == ADMIN_USUARIO and s == ADMIN_SENHA:
            garantir_usuario_admin(ADMIN_USUARIO, ADMIN_SENHA)
            usuario_autenticado = autenticar_usuario(u, s) or dict(ADMIN_PERFIL_PADRAO)

        if usuario_autenticado:
            # Aplica a opção "Me lembrar"
            if lembrar_var.get():
                me_lembrar(salvar=True, usuario_str=u, senha_str=s)
            else:
                me_lembrar(salvar=False)

            messagebox.showinfo(
                "Sucesso",
                f"Login realizado com sucesso!\nBem-vindo(a), {usuario_autenticado['nome']}!",
            )
            if on_login_sucesso:
                on_login_sucesso(usuario_autenticado)
            else:
                abrir_menu()
        else:
            messagebox.showerror(
                "Erro de Login",
                "Usuário ou senha incorretos!\nVerifique os dados ou utilize 'Esqueci minha senha?'.",
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
        command=fazer_login,
    )
    btn_login.pack(padx=35, pady=(2, 10))

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
        command=abrir_cadastro,
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
        command=abrir_menu,
    )
    btn_menu.pack(padx=35, pady=(0, 25))


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Teste - Login")
    app.geometry("800x600")
    LoginApp(app, lambda: print("Abrir cadastro"), lambda: print("Abrir menu"))
    app.mainloop()
