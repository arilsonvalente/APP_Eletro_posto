import customtkinter as ctk
from tkintermapview import TkinterMapView

# Paleta de cores inspirada no design da EletroBel
COR_FUNDO = "#0B131B"
COR_CARD = "#141F2B"
COR_BORDA = "#1E2D3D"
COR_VERDE = "#00D26A"
COR_VERDE_HOVER = "#00B058"
COR_OCUPADO = "#FFA500"
COR_TEXTO_MUTED = "#8B9DAE"

# Dados extraídos da interface e complementados para Belém e Ananindeua
DADOS_POSTOS = [
    {
        "nome": "Estação EletroBel Doca",
        "cidade": "Belém",
        "endereco": "Av. Visconde de Souza Franco (Doca), 500",
        "potencia": "150 kW (DC Rápida)",
        "conector": "CCS2 / Tipo 2",
        "preco": "R$ 1.95/kWh",
        "status": "Disponível",
        "lat": -1.4485,
        "lon": -48.4890
    },
    {
        "nome": "Estação BRT Augusto Montenegro",
        "cidade": "Belém",
        "endereco": "Av. Augusto Montenegro, Km 8 - Parque Verde",
        "potencia": "90 kW (DC Rápida)",
        "conector": "CCS2 / Tipo 2",
        "preco": "R$ 1.85/kWh",
        "status": "Disponível",
        "lat": -1.3620,
        "lon": -48.4490
    },
    {
        "nome": "Estação Shopping Bosque Grão-Pará",
        "cidade": "Belém",
        "endereco": "Av. Centenário, 1052 - Mangueirão",
        "potencia": "60 kW (DC Rápida)",
        "conector": "CCS2",
        "preco": "R$ 2.10/kWh",
        "status": "Disponível",
        "lat": -1.3789,
        "lon": -48.4480
    },
    {
        "nome": "Estação Aeroporto Internacional",
        "cidade": "Belém",
        "endereco": "Val-de-Cans - Estacionamento VIP",
        "potencia": "100 kW (DC Rápida)",
        "conector": "CCS2",
        "preco": "R$ 2.30/kWh",
        "status": "Ocupado",
        "lat": -1.3850,
        "lon": -48.4760
    },
    {
        "nome": "Estação Shopping Metrópole",
        "cidade": "Ananindeua",
        "endereco": "Rod. BR-316, Km 4 - Coqueiro",
        "potencia": "60 kW (DC Rápida)",
        "conector": "CCS2 / Tipo 2",
        "preco": "R$ 1.90/kWh",
        "status": "Disponível",
        "lat": -1.3655,
        "lon": -48.3748
    },
    {
        "nome": "Estação Posto Grão Ananindeua",
        "cidade": "Ananindeua",
        "endereco": "Rod. BR-316, Km 8 - Centro",
        "potencia": "90 kW (DC Rápida)",
        "conector": "CCS2",
        "preco": "R$ 1.95/kWh",
        "status": "Disponível",
        "lat": -1.3850,
        "lon": -48.4020
    }
]


class EletroBelApp(ctk.CTkFrame):
    def __init__(self, master, abrir_menu_callback):
        # Limpa os componentes anteriores da janela principal
        for widget in master.winfo_children():
            widget.destroy()

        super().__init__(master, fg_color=COR_FUNDO)
        self.pack(fill="both", expand=True)

        self.abrir_menu_callback = abrir_menu_callback
        self.marcadores_no_mapa = []

        # Configuração de grade para painel lateral e mapa
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.construir_painel_lateral()
        self.construir_mapa()
        self.atualizar_lista_e_marcadores()

    def voltar(self):
        self.destroy()
        self.abrir_menu_callback()

    def construir_painel_lateral(self):
        self.painel_lateral = ctk.CTkFrame(
            self,
            width=420,
            corner_radius=0,
            fg_color=COR_FUNDO
        )
        self.painel_lateral.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        self.painel_lateral.grid_propagate(False)

        # Botão de retorno ao menu principal
        btn_voltar = ctk.CTkButton(
            self.painel_lateral,
            text="← Voltar ao Menu",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            text_color=COR_VERDE,
            hover_color=COR_CARD,
            anchor="w",
            height=28,
            command=self.voltar
        )
        btn_voltar.pack(anchor="w", pady=(0, 10))

        # Cabeçalho da aplicação
        frame_logo = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        frame_logo.pack(fill="x", pady=(0, 12))

        lbl_logo = ctk.CTkLabel(
            frame_logo,
            text="⚡ EletroBel",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COR_VERDE
        )
        lbl_logo.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            frame_logo,
            text="Encontre eletropostos rápidos e conecte-se",
            font=ctk.CTkFont(size=12),
            text_color=COR_TEXTO_MUTED
        )
        lbl_sub.pack(anchor="w")

        # Filtro de região
        frame_filtro = ctk.CTkFrame(
            self.painel_lateral,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=8
        )
        frame_filtro.pack(fill="x", pady=(0, 14), ipady=4)

        lbl_regiao = ctk.CTkLabel(frame_filtro, text="📍 Região:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_regiao.pack(side="left", padx=(10, 6))

        self.combo_cidade = ctk.CTkComboBox(
            frame_filtro,
            values=["Todas as Cidades", "Belém", "Ananindeua"],
            command=lambda _: self.atualizar_lista_e_marcadores(),
            fg_color="#0D1620",
            button_color=COR_VERDE,
            button_hover_color=COR_VERDE_HOVER,
            border_color=COR_BORDA,
            dropdown_fg_color=COR_CARD,
            width=260
        )
        self.combo_cidade.pack(side="left", padx=(0, 8), fill="x", expand=True)

        # Contador
        self.lbl_contador = ctk.CTkLabel(
            self.painel_lateral,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        )
        self.lbl_contador.pack(anchor="w", pady=(0, 8))

        # Lista rolável de postos
        self.scroll_cards = ctk.CTkScrollableFrame(
            self.painel_lateral,
            fg_color="transparent",
            corner_radius=8
        )
        self.scroll_cards.pack(fill="both", expand=True)

    def construir_mapa(self):
        frame_mapa = ctk.CTkFrame(
            self,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=12
        )
        frame_mapa.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        self.map_widget = TkinterMapView(frame_mapa, corner_radius=12)
        self.map_widget.pack(fill="both", expand=True, padx=2, pady=2)
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        self.centralizar_visao()

    def centralizar_visao(self):
        self.map_widget.set_position(-1.4050, -48.4350)
        self.map_widget.set_zoom(12)

    def focar_no_posto(self, posto):
        self.map_widget.set_position(posto["lat"], posto["lon"])
        self.map_widget.set_zoom(15)

    def atualizar_lista_e_marcadores(self):
        for widget in self.scroll_cards.winfo_children():
            widget.destroy()

        for marcador in self.marcadores_no_mapa:
            marcador.delete()
        self.marcadores_no_mapa.clear()

        filtro = self.combo_cidade.get()
        postos_filtrados = [
            p for p in DADOS_POSTOS
            if filtro == "Todas as Cidades" or p["cidade"] == filtro
        ]

        self.lbl_contador.configure(
            text=f"⚡ Eletropostos ({len(postos_filtrados)} encontrados)"
        )

        for posto in postos_filtrados:
            marcador = self.map_widget.set_marker(
                posto["lat"],
                posto["lon"],
                text=f"{posto['nome']} ({posto['status']})",
                command=lambda m, p=posto: self.focar_no_posto(p)
            )
            self.marcadores_no_mapa.append(marcador)

            card = ctk.CTkFrame(
                self.scroll_cards,
                fg_color=COR_CARD,
                border_width=1,
                border_color=COR_BORDA,
                corner_radius=10
            )
            card.pack(fill="x", pady=6, padx=2)

            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=12, pady=(10, 4))

            ctk.CTkLabel(
                topo,
                text=posto["nome"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white"
            ).pack(side="left")

            cor_status = COR_VERDE if posto["status"] == "Disponível" else COR_OCUPADO
            ctk.CTkLabel(
                topo,
                text=f"● {posto['status']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=cor_status
            ).pack(side="right")

            ctk.CTkLabel(
                card,
                text=f"📍 {posto['endereco']}",
                font=ctk.CTkFont(size=11),
                text_color=COR_TEXTO_MUTED
            ).pack(anchor="w", padx=12, pady=(0, 6))

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=12, pady=(0, 8))

            ctk.CTkLabel(
                info_frame,
                text=f"⚡ {posto['potencia']}  |  🔌 {posto['conector']}",
                font=ctk.CTkFont(size=11),
                text_color=COR_VERDE
            ).pack(side="left")

            ctk.CTkLabel(
                info_frame,
                text=posto["preco"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            ).pack(side="right")

            btn_acao = ctk.CTkButton(
                card,
                text="Localizar no Mapa",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                border_width=1,
                border_color=COR_VERDE,
                text_color=COR_VERDE,
                hover_color="#0F2B22",
                height=30,
                command=lambda p=posto: self.focar_no_posto(p)
            )
            btn_acao.pack(fill="x", padx=12, pady=(0, 10))