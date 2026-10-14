import customtkinter as ctk
from tkinter import messagebox

# Configurações globais de tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Cores baseadas na logo EletroBel
COLOR_BG = "#0B0F12"          # Fundo escuro azulado/grafite profundo
COLOR_CARD_BG = "#13191E"     # Fundo dos cards e containers
COLOR_ACCENT = "#00FF66"      # Verde neon / raio elétrico
COLOR_ACCENT_HOVER = "#00CC52"# Verde neon mais escuro para hover
COLOR_BORDER = "#1E2A32"      # Bordas sutis em chumbo
COLOR_TEXT_MAIN = "#FFFFFF"   # Texto primário
COLOR_TEXT_MUTED = "#8B9DAA"  # Texto secundário/cinza


def Menu(janela, abrir_login):

    # Limpa os componentes anteriores
    for widget in janela.winfo_children():
        widget.destroy()

    # Configuração da janela
    janela.title("EletroBel Postos - Mobilidade Elétrica & Energia")
    janela.geometry("1100x720")
    janela.minsize(950, 600)
    janela.configure(fg_color=COLOR_BG)

    # Frame principal
    frame = ctk.CTkFrame(janela, fg_color=COLOR_BG)
    frame.pack(fill="both", expand=True)

    # ==========================================
    # CABEÇALHO
    # ==========================================
    def criar_cabecalho(parent):

        navbar = ctk.CTkFrame(
            parent,
            fg_color=COLOR_CARD_BG,
            height=70,
            corner_radius=0,
            border_width=1,
            border_color=COLOR_BORDER
        )
        navbar.pack(fill="x", side="top")
        navbar.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(
            navbar,
            fg_color="transparent"
        )
        logo_frame.pack(side="left", padx=30)

        ctk.CTkLabel(
            logo_frame,
            text="⚡",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=COLOR_ACCENT
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            logo_frame,
            text="EletroBel Postos",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=24,
                weight="bold"
            ),
            text_color=COLOR_TEXT_MAIN
        ).pack(side="left")

        # Menu de navegação
        menu_frame = ctk.CTkFrame(
            navbar,
            fg_color="transparent"
        )
        menu_frame.pack(side="right", padx=20)

        itens_menu = [
            "Início",
            "Veículos",
            "Estações",
            "Serviços",
            "Sobre"
        ]

        for item in itens_menu:
            ctk.CTkButton(
                menu_frame,
                text=item,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color="#182229",
                text_color=COLOR_TEXT_MUTED,
                width=65,
                corner_radius=8
            ).pack(side="left", padx=2)

        # Botão para abrir o login
        ctk.CTkButton(
            menu_frame,
            text="Entrar",
            command=abrir_login,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#000000",
            corner_radius=8,
            width=80,
            height=36
        ).pack(side="left", padx=(10, 0))

    # ==========================================
    # CONTEÚDO PRINCIPAL
    # ==========================================
    def criar_conteudo_principal(parent):

        scroll_container = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color="#1F2A33",
            scrollbar_button_hover_color=COLOR_ACCENT
        )
        scroll_container.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        # Banner principal
        hero_frame = ctk.CTkFrame(
            scroll_container,
            fg_color=COLOR_CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=COLOR_BORDER
        )
        hero_frame.pack(
            fill="x",
            pady=(0, 30),
            ipady=25
        )

        ctk.CTkLabel(
            hero_frame,
            text="⚡ O FUTURO DA MOBILIDADE É ELÉTRICO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_ACCENT,
            fg_color="#0D2E1F",
            corner_radius=20
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        ctk.CTkLabel(
            hero_frame,
            text="Soluções Inteligentes em\nTecnologia e Eletrificação",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=34,
                weight="bold"
            ),
            text_color=COLOR_TEXT_MAIN,
            justify="left"
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

        ctk.CTkLabel(
            hero_frame,
            text=(
                "Infraestrutura de recarga de alta performance, "
                "conversão e assistência técnica\n"
                "especializada para seu veículo elétrico ou híbrido."
            ),
            font=ctk.CTkFont(size=15),
            text_color=COLOR_TEXT_MUTED,
            justify="left"
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 25)
        )

        botoes_hero = ctk.CTkFrame(
            hero_frame,
            fg_color="transparent"
        )
        botoes_hero.pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        ctk.CTkButton(
            botoes_hero,
            text="Explorar Serviços",
            command=lambda: scroll_container.yview_moveto(1),
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#000000",
            corner_radius=10,
            height=44,
            width=160
        ).pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            botoes_hero,
            text="Acessar minha conta",
            command=abrir_login,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color="#1F2A33",
            text_color=COLOR_TEXT_MAIN,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=10,
            height=44,
            width=180
        ).pack(side="left")

        # Título da seção
        ctk.CTkLabel(
            scroll_container,
            text="Nossos Serviços e Diferenciais",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        ).pack(
            anchor="w",
            pady=(10, 15)
        )

        # Cards de serviços
        cards_frame = ctk.CTkFrame(
            scroll_container,
            fg_color="transparent"
        )
        cards_frame.pack(fill="x", expand=True)

        for coluna in range(3):
            cards_frame.grid_columnconfigure(
                coluna,
                weight=1,
                uniform="servicos"
            )

        servicos = [
            {
                "icone": "🔌",
                "titulo": "Estações de Recarga",
                "descricao": (
                    "Instalação e manutenção de carregadores "
                    "rápidos, residenciais e comerciais."
                )
            },
            {
                "icone": "🛠️",
                "titulo": "Manutenção Técnica",
                "descricao": (
                    "Diagnóstico de baterias, motores e "
                    "módulos elétricos."
                )
            },
            {
                "icone": "🔋",
                "titulo": "Eficiência Energética",
                "descricao": (
                    "Projetos integrados com energia solar "
                    "para uma recarga sustentável."
                )
            }
        ]

        for idx, item in enumerate(servicos):

            card = ctk.CTkFrame(
                cards_frame,
                fg_color=COLOR_CARD_BG,
                corner_radius=14,
                border_width=1,
                border_color=COLOR_BORDER
            )
            card.grid(
                row=0,
                column=idx,
                padx=8,
                pady=5,
                sticky="nsew",
                ipady=15
            )

            ctk.CTkLabel(
                card,
                text=item["icone"],
                font=ctk.CTkFont(size=30)
            ).pack(
                anchor="w",
                padx=20,
                pady=(15, 10)
            )

            ctk.CTkLabel(
                card,
                text=item["titulo"],
                font=ctk.CTkFont(size=17, weight="bold"),
                text_color=COLOR_TEXT_MAIN,
                wraplength=230
            ).pack(
                anchor="w",
                padx=20,
                pady=(0, 6)
            )

            ctk.CTkLabel(
                card,
                text=item["descricao"],
                font=ctk.CTkFont(size=13),
                text_color=COLOR_TEXT_MUTED,
                wraplength=230,
                justify="left"
            ).pack(
                anchor="w",
                padx=20,
                pady=(0, 15)
            )

    # Monta a interface na ordem correta
    criar_cabecalho(frame)
    criar_conteudo_principal(frame)
