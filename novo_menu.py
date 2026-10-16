import customtkinter as ctk

# Configuração global de aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class EletroBelApp(ctk.CTk):
    def _init_(self):
        super()._init_()

        # Janela principal
        self.title("EletroBel - Conectando o Futuro Elétrico")
        self.geometry("1100x700")
        self.minsize(980, 640)
        self.configure(fg_color="#0A0E14")  # Fundo escuro premium

        # Paleta de Cores baseada na identidade visual da marca
        self.COLOR_BG = "#0A0E14"
        self.COLOR_CARD_BG = "#131922"
        self.COLOR_CARD_BORDER = "#1F2B37"
        self.COLOR_ACCENT = "#00E676"        # Verde neon elétrico
        self.COLOR_ACCENT_HOVER = "#00C853"
        self.COLOR_TEXT_MAIN = "#FFFFFF"
        self.COLOR_TEXT_MUTED = "#8A99AD"

        self._criar_layout()

    def _criar_layout(self):
        # Container com rolagem para adaptação a diferentes tamanhos de tela
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=40, pady=25)

        self._criar_navbar()
        self._criar_hero_section()
        self._criar_barra_busca()
        self._criar_cards_funcionalidades()

    def _criar_navbar(self):
        nav_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 35))

        # Logo / Marca
        logo_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
        logo_container.pack(side="left")

        logo_icon = ctk.CTkLabel(
            logo_container,
            text="⚡",
            font=ctk.CTkFont(size=26),
            text_color=self.COLOR_ACCENT
        )
        logo_icon.pack(side="left", padx=(0, 6))

        logo_label = ctk.CTkLabel(
            logo_container,
            text="EletroBel",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.COLOR_TEXT_MAIN
        )
        logo_label.pack(side="left")

        # Links de navegação (sem FAQ nem Sobre Nós)
        actions_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        actions_frame.pack(side="right")

        nav_links = ["Início", "Mapa de Eletropostos", "Carros Elétricos"]
        for i, link in enumerate(nav_links):
            link_color = self.COLOR_ACCENT if i == 0 else self.COLOR_TEXT_MUTED
            btn = ctk.CTkButton(
                actions_frame,
                text=link,
                fg_color="transparent",
                hover_color="#182330",
                text_color=link_color,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold" if i == 0 else "normal"),
                width=100,
                height=32
            )
            btn.pack(side="left", padx=5)

        # Botão Cadastre-se
        btn_cadastro = ctk.CTkButton(
            actions_frame,
            text="Cadastre-se",
            fg_color="transparent",
            border_color=self.COLOR_ACCENT,
            border_width=1.5,
            hover_color="#113322",
            text_color=self.COLOR_ACCENT,
            corner_radius=20,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=115,
            height=34
        )
        btn_cadastro.pack(side="left", padx=(15, 8))

        # Botão Entrar
        btn_entrar = ctk.CTkButton(
            actions_frame,
            text="Entrar",
            fg_color="transparent",
            hover_color="#182330",
            text_color=self.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            width=70,
            height=34
        )
        btn_entrar.pack(side="left")

    def _criar_hero_section(self):
        hero_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        hero_frame.pack(fill="x", pady=(15, 20))

        # Título principal
        title_box = ctk.CTkFrame(hero_frame, fg_color="transparent")
        title_box.pack(anchor="w")

        lbl_part1 = ctk.CTkLabel(
            title_box,
            text="Encontre e ",
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            text_color=self.COLOR_TEXT_MAIN
        )
        lbl_part1.pack(side="left")

        lbl_part2 = ctk.CTkLabel(
            title_box,
            text="Conecte",
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            text_color=self.COLOR_ACCENT
        )
        lbl_part2.pack(side="left")

        # Subtítulo
        subtitle_lbl = ctk.CTkLabel(
            hero_frame,
            text="Encontre eletropostos rápidos e acompanhe tudo sobre\ncarros elétricos em uma única plataforma integrada.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=self.COLOR_TEXT_MUTED,
            justify="left"
        )
        subtitle_lbl.pack(anchor="w", pady=(8, 0))

    def _criar_barra_busca(self):
        # Card da barra de busca
        search_card = ctk.CTkFrame(
            self.scroll_container,
            fg_color=self.COLOR_CARD_BG,
            border_color=self.COLOR_CARD_BORDER,
            border_width=1.5,
            corner_radius=30,
            height=65
        )
        search_card.pack(fill="x", pady=(15, 40), ipady=5)
        search_card.pack_propagate(False)

        inner_box = ctk.CTkFrame(search_card, fg_color="transparent")
        inner_box.pack(fill="both", expand=True, padx=15, pady=8)

        # Ícone de localização
        loc_icon = ctk.CTkLabel(inner_box, text="📍", font=ctk.CTkFont(size=16))
        loc_icon.pack(side="left", padx=(5, 5))

        # Filtro restrito a Belém e Ananindeua
        self.cidade_var = ctk.StringVar(value="Belém, PA")
        cidade_menu = ctk.CTkOptionMenu(
            inner_box,
            values=["Belém, PA", "Ananindeua, PA", "Região Metropolitana (Belém / Ananindeua)"],
            variable=self.cidade_var,
            fg_color="#18222F",
            button_color="#1F2D3D",
            button_hover_color=self.COLOR_ACCENT,
            dropdown_fg_color="#18222F",
            dropdown_hover_color="#243447",
            dropdown_text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=15,
            width=260,
            height=38
        )
        cidade_menu.pack(side="left", padx=(0, 15))

        # Checkbox Carga Rápida
        self.fast_charge_var = ctk.BooleanVar(value=True)
        chk_fast = ctk.CTkCheckBox(
            inner_box,
            text="Carga Rápida (DC)",
            variable=self.fast_charge_var,
            checkmark_color="#000000",
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_TEXT_MAIN,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        chk_fast.pack(side="left", padx=10)

        # Botão Buscar Eletropostos
        btn_buscar = ctk.CTkButton(
            inner_box,
            text="Buscar Eletropostos",
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=20,
            height=40,
            width=190,
            command=self._acao_buscar
        )
        btn_buscar.pack(side="right", padx=(10, 5))

    def _criar_cards_funcionalidades(self):
        cards_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        cards_container.pack(fill="x", pady=(0, 20))

        # 3 colunas proporcionais
        cards_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        cards_info = [
            {
                "col": 0,
                "icone": "⚡",
                "titulo": "Encontrar Eletropostos",
                "desc": "Mapeamento em tempo real de pontos de recarga disponíveis em Belém e Ananindeua.",
                "destaque": True
            },
            {
                "col": 1,
                "icone": "🗺️",
                "titulo": "Calculadora de Viagem",
                "desc": "Planeje suas paradas e estime com precisão o tempo de carga ideal para o seu trajeto.",
                "destaque": False
            },
            {
                "col": 2,
                "icone": "🚗",
                "titulo": "Mundo Elétrico",
                "desc": "Notícias, especificações, novidades e tendências sobre o universo de veículos elétricos.",
                "destaque": False
            }
        ]

        for item in cards_info:
            border_c = self.COLOR_ACCENT if item["destaque"] else self.COLOR_CARD_BORDER
            card = ctk.CTkFrame(
                cards_container,
                fg_color=self.COLOR_CARD_BG,
                border_color=border_c,
                border_width=1.5,
                corner_radius=18
            )
            card.grid(row=0, column=item["col"], padx=10, pady=5, sticky="nsew")

            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=20, pady=22)

            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", anchor="w")

            lbl_ico = ctk.CTkLabel(header, text=item["icone"], font=ctk.CTkFont(size=20))
            lbl_ico.pack(side="left", padx=(0, 10))

            lbl_tit = ctk.CTkLabel(
                header,
                text=item["titulo"],
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=self.COLOR_TEXT_MAIN
            )
            lbl_tit.pack(side="left")

            lbl_desc = ctk.CTkLabel(
                content,
                text=item["desc"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=self.COLOR_TEXT_MUTED,
                justify="left",
                wraplength=250
            )
            lbl_desc.pack(anchor="w", pady=(14, 0))

    def _acao_buscar(self):
        cidade = self.cidade_var.get()
        rapida = "Sim" if self.fast_charge_var.get() else "Não"
        print(f"[EletroBel] Buscando eletropostos na região: {cidade} | Carga Rápida: {rapida}")

if _name_ == "_main_":
    app = EletroBelApp()
    app.mainloop()