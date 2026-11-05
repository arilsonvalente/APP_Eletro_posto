import webbrowser
import urllib.parse
import customtkinter as ctk
from tkinter import messagebox
from tkintermapview import TkinterMapView
import database

# Paleta de cores inspirada no design da EletroBel e no portal Carregados.com.br
COR_FUNDO = "#0A0E14"
COR_PAINEL = "#0F1620"
COR_CARD = "#141F2B"
COR_CARD_SELECIONADO = "#192B3C"
COR_BORDA = "#1E2D3D"
COR_VERDE = "#00E676"
COR_VERDE_HOVER = "#00C853"
COR_AZUL_DC = "#40C4FF"
COR_ROXO_AC = "#B388FF"
COR_OCUPADO = "#FFA726"
COR_MANUTENCAO = "#FF5252"
COR_TEXTO_MAIN = "#FFFFFF"
COR_TEXTO_MUTED = "#8B9DAE"

# Base de eletropostos reais de Belém e Ananindeua inspirada no mapeamento Carregados.com.br
CATALOGO_CARREGADOS_PA = [
    {
        "nome": "Boulevard Shopping Belém",
        "rede": "Karg / EletroBel",
        "cidade": "Belém",
        "bairro": "Reduto",
        "endereco": "Av. Visc. de Souza Franco, 776 - Reduto, Belém - PA",
        "potencia_kw": 60.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2 / Tipo 2",
        "preco_kwh": 2.10,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "10h às 22h",
        "lat": -1.4453,
        "lon": -48.4892,
    },
    {
        "nome": "Estação EletroBel Doca",
        "rede": "EletroBel Ultra",
        "cidade": "Belém",
        "bairro": "Reduto (Doca)",
        "endereco": "Av. Visconde de Souza Franco (Doca), 500 - Belém, PA",
        "potencia_kw": 150.0,
        "tipo_carga": "DC Ultrarrápida",
        "conector": "CCS2 / Tipo 2",
        "preco_kwh": 1.95,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "24 horas",
        "lat": -1.4485,
        "lon": -48.4890,
    },
    {
        "nome": "Posto Preço Baixo (Castanheira)",
        "rede": "PlugBRA",
        "cidade": "Belém",
        "bairro": "Castanheira",
        "endereco": "Rod. Augusto Montenegro, 290 - Castanheira, Belém - PA",
        "potencia_kw": 60.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2 / Tipo 2",
        "preco_kwh": 1.99,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "24 horas",
        "lat": -1.3995,
        "lon": -48.4315,
    },
    {
        "nome": "PlugBRA Senador Lemos",
        "rede": "PlugBRA",
        "cidade": "Belém",
        "bairro": "Sacramenta",
        "endereco": "Av. Sen. Lemos, 2842 - Sacramenta, Belém - PA",
        "potencia_kw": 60.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2",
        "preco_kwh": 1.95,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "24 horas",
        "lat": -1.4152,
        "lon": -48.4745,
    },
    {
        "nome": "PlugBRA Econômico Marambaia",
        "rede": "PlugBRA",
        "cidade": "Belém",
        "bairro": "Marambaia",
        "endereco": "Av. Pedro Álvares Cabral, 70 - Marambaia, Belém - PA",
        "potencia_kw": 60.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2 / Tipo 2",
        "preco_kwh": 1.79,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "24 horas",
        "lat": -1.4048,
        "lon": -48.4382,
    },
    {
        "nome": "Estação Shopping Bosque Grão-Pará",
        "rede": "EletroBel / Volvo",
        "cidade": "Belém",
        "bairro": "Val-de-Cans",
        "endereco": "Av. Centenário, 1052 - Val-de-Cans, Belém - PA",
        "potencia_kw": 60.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2",
        "preco_kwh": 2.10,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "10h às 22h",
        "lat": -1.3789,
        "lon": -48.4480,
    },
    {
        "nome": "Parque Shopping Belém",
        "rede": "Tupinambá / Karg",
        "cidade": "Belém",
        "bairro": "Parque Verde",
        "endereco": "Rod. Augusto Montenegro, 4300 - Parque Verde, Belém - PA",
        "potencia_kw": 60.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2 / Tipo 2",
        "preco_kwh": 2.05,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "10h às 22h",
        "lat": -1.3688,
        "lon": -48.4485,
    },
    {
        "nome": "Estação BRT Augusto Montenegro",
        "rede": "EletroBel",
        "cidade": "Belém",
        "bairro": "Parque Verde",
        "endereco": "Av. Augusto Montenegro, Km 8 - Parque Verde, Belém - PA",
        "potencia_kw": 90.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2 / Tipo 2",
        "preco_kwh": 1.85,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "24 horas",
        "lat": -1.3620,
        "lon": -48.4490,
    },
    {
        "nome": "Estação Aeroporto Internacional",
        "rede": "EletroBel VIP",
        "cidade": "Belém",
        "bairro": "Val-de-Cans",
        "endereco": "Val-de-Cans - Estacionamento VIP, Belém - PA",
        "potencia_kw": 100.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2",
        "preco_kwh": 2.30,
        "acesso": "Público",
        "status": "Ocupado",
        "horario": "24 horas",
        "lat": -1.3850,
        "lon": -48.4760,
    },
    {
        "nome": "BYD Concessionária Belém",
        "rede": "BYD Recharge",
        "cidade": "Belém",
        "bairro": "Umarizal",
        "endereco": "Av. Pedro Álvares Cabral, 303 A - Umarizal, Belém - PA",
        "potencia_kw": 60.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2 / Tipo 2",
        "preco_kwh": 1.90,
        "acesso": "Restrito / Clientes",
        "status": "Disponível",
        "horario": "08h às 18h",
        "lat": -1.4348,
        "lon": -48.4810,
    },
    {
        "nome": "Sebrae Pará (Umarizal)",
        "rede": "Sebrae Eco",
        "cidade": "Belém",
        "bairro": "Umarizal",
        "endereco": "Tv. Dom Romualdo de Seixas, 294 - Umarizal, Belém - PA",
        "potencia_kw": 22.0,
        "tipo_carga": "AC Semirrápida",
        "conector": "Tipo 2",
        "preco_kwh": 1.50,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "08h às 18h",
        "lat": -1.4440,
        "lon": -48.4835,
    },
    {
        "nome": "Supermercado Líder Doca",
        "rede": "Líder / PlugBRA",
        "cidade": "Belém",
        "bairro": "Reduto",
        "endereco": "Av. Visc. de Souza Franco, 1088 - Reduto, Belém - PA",
        "potencia_kw": 22.0,
        "tipo_carga": "AC Semirrápida",
        "conector": "Tipo 2",
        "preco_kwh": 1.65,
        "acesso": "Clientes",
        "status": "Manutenção",
        "horario": "07h às 23h",
        "lat": -1.4422,
        "lon": -48.4865,
    },
    {
        "nome": "Complexo Porto Futuro / Docas",
        "rede": "EletroBel Urbano",
        "cidade": "Belém",
        "bairro": "Campina",
        "endereco": "Blvd. Castilhos França / Av. Visc. de Souza Franco - Belém, PA",
        "potencia_kw": 22.0,
        "tipo_carga": "AC Semirrápida",
        "conector": "Tipo 2",
        "preco_kwh": 1.60,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "09h às 23h",
        "lat": -1.4488,
        "lon": -48.4998,
    },
    {
        "nome": "Estação Metrópole Ananindeua",
        "rede": "EletroBel / Karg",
        "cidade": "Ananindeua",
        "bairro": "Coqueiro",
        "endereco": "Rodovia BR-316, Km 4 - Coqueiro, Ananindeua - PA",
        "potencia_kw": 120.0,
        "tipo_carga": "DC Ultrarrápida",
        "conector": "CCS2 / CHAdeMO",
        "preco_kwh": 1.90,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "10h às 22h",
        "lat": -1.3655,
        "lon": -48.3748,
    },
    {
        "nome": "Estação Cidade Nova",
        "rede": "EletroBel",
        "cidade": "Ananindeua",
        "bairro": "Cidade Nova",
        "endereco": "Av. Arterial 18, 400 - Cidade Nova, Ananindeua - PA",
        "potencia_kw": 22.0,
        "tipo_carga": "AC Semirrápida",
        "conector": "Tipo 2",
        "preco_kwh": 1.45,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "24 horas",
        "lat": -1.3510,
        "lon": -48.4040,
    },
    {
        "nome": "Estação Posto Grão Ananindeua",
        "rede": "PlugBRA / EletroBel",
        "cidade": "Ananindeua",
        "bairro": "Centro (BR-316)",
        "endereco": "Rod. BR-316, Km 8 - Centro, Ananindeua - PA",
        "potencia_kw": 90.0,
        "tipo_carga": "DC Rápida",
        "conector": "CCS2",
        "preco_kwh": 1.95,
        "acesso": "Público",
        "status": "Disponível",
        "horario": "24 horas",
        "lat": -1.3690,
        "lon": -48.3490,
    },
]


class EletroBelApp(ctk.CTkFrame):
    """
    Mapa interativo de Eletropostos de Belém e Ananindeua,
    inspirado na plataforma Carregados.com.br e integrado ao banco MySQL.
    """

    def __init__(self, master, abrir_menu_callback):
        for widget in master.winfo_children():
            widget.destroy()

        super().__init__(master, fg_color=COR_FUNDO)
        self.pack(fill="both", expand=True)

        self.abrir_menu_callback = abrir_menu_callback
        self.marcadores_no_mapa = []
        self.posto_selecionado = None
        self.todos_postos = self._carregar_postos_integrados()

        # Layout principal: Painel Lateral (esquerda) + Área do Mapa e Detalhes (direita)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.construir_painel_lateral()
        self.construir_area_mapa()
        self.atualizar_lista_e_marcadores()

    def _carregar_postos_integrados(self):
        """
        Mescla os eletropostos cadastrados no banco MySQL com os metadados geográficos
        e o catálogo completo de Belém e Ananindeua (base Carregados.com.br).
        """
        postos = [dict(p) for p in CATALOGO_CARREGADOS_PA]
        nomes_existentes = {p["nome"].lower(): p for p in postos}

        try:
            estacoes_bd = database.listar_estacoes()
            for idx, est in enumerate(estacoes_bd):
                nome_bd = (est.get("nome") or "").strip()
                chave = nome_bd.lower()
                potencia = float(est.get("potencia_kw") or 50.0)
                preco = float(est.get("preco_kwh") or 1.95)
                conector = est.get("tipo_conector") or "CCS2 / Tipo 2"
                status = est.get("status") or "Disponível"
                endereco = est.get("endereco") or "Belém, PA"

                if chave in nomes_existentes:
                    # Atualiza dados dinâmicos vindos do banco MySQL
                    alvo = nomes_existentes[chave]
                    alvo["id"] = est.get("id")
                    alvo["potencia_kw"] = potencia
                    alvo["preco_kwh"] = preco
                    alvo["conector"] = conector
                    alvo["status"] = status
                    alvo["endereco"] = endereco
                    alvo["tipo_carga"] = (
                        "DC Ultrarrápida" if potencia >= 120 else ("DC Rápida" if potencia >= 50 else "AC Semirrápida")
                    )
                else:
                    cidade = "Ananindeua" if "ananindeua" in endereco.lower() else "Belém"
                    lat_base = -1.3655 if cidade == "Ananindeua" else -1.4300
                    lon_base = -48.3748 if cidade == "Ananindeua" else -48.4700
                    novo_posto = {
                        "id": est.get("id"),
                        "nome": nome_bd,
                        "rede": "EletroBel MySQL",
                        "cidade": cidade,
                        "bairro": cidade,
                        "endereco": endereco,
                        "potencia_kw": potencia,
                        "tipo_carga": "DC Rápida" if potencia >= 50 else "AC Semirrápida",
                        "conector": conector,
                        "preco_kwh": preco,
                        "acesso": "Público",
                        "status": status,
                        "horario": "24 horas",
                        "lat": lat_base + (idx * 0.004),
                        "lon": lon_base + (idx * 0.004),
                    }
                    postos.append(novo_posto)
        except Exception as e:
            print(f"[AVISO] Mapa carregado com catalogo padrao ({e})")

        return postos

    def voltar(self):
        self.destroy()
        self.abrir_menu_callback()

    # =====================================================================
    # PAINEL LATERAL: BUSCA, FILTROS E LISTA DE ESTAÇÕES
    # =====================================================================

    def construir_painel_lateral(self):
        self.painel_lateral = ctk.CTkFrame(
            self,
            width=440,
            corner_radius=0,
            fg_color=COR_PAINEL,
            border_width=1,
            border_color=COR_BORDA,
        )
        self.painel_lateral.grid(row=0, column=0, sticky="nsew")
        self.painel_lateral.grid_propagate(False)

        topo_box = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        topo_box.pack(fill="x", padx=16, pady=(14, 6))

        btn_voltar = ctk.CTkButton(
            topo_box,
            text="← Menu Inicial",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#162230",
            text_color=COR_VERDE,
            hover_color="#1E3044",
            corner_radius=8,
            width=110,
            height=28,
            command=self.voltar,
        )
        btn_voltar.pack(side="left")

        btn_portal = ctk.CTkButton(
            topo_box,
            text="🌐 Carregados.com.br",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="transparent",
            border_width=1,
            border_color=COR_BORDA,
            text_color=COR_TEXTO_MUTED,
            hover_color="#162230",
            corner_radius=8,
            width=145,
            height=28,
            command=lambda: webbrowser.open(
                "https://carregados.com.br/estacoes?cidade=bel%C3%A9m&estado=par%C3%A1+%28pa%29"
            ),
        )
        btn_portal.pack(side="right")

        # Título e Subtítulo
        header_frame = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(2, 8))

        ctk.CTkLabel(
            header_frame,
            text="⚡ Mapa de Eletropostos PA",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COR_VERDE,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Mapeamento Belém & Ananindeua • Padrão CCS2 e Tipo 2",
            font=ctk.CTkFont(size=11),
            text_color=COR_TEXTO_MUTED,
        ).pack(anchor="w")

        # Card de Filtros (Inspirado no Carregados.com.br)
        filtro_card = ctk.CTkFrame(
            self.painel_lateral,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=12,
        )
        filtro_card.pack(fill="x", padx=16, pady=(0, 10))

        # 1. Busca por texto (nome, bairro, endereço, rede)
        self.busca_var = ctk.StringVar()
        self.entry_busca = ctk.CTkEntry(
            filtro_card,
             textvariable=self.busca_var,
            placeholder_text="🔍 Buscar por nome, bairro (ex: Umarizal, Doca) ou rede...",
            fg_color="#0B121A",
            border_color=COR_BORDA,
            text_color=COR_TEXTO_MAIN,
            height=34,
            corner_radius=8,
        )
        self.entry_busca.pack(fill="x", padx=10, pady=(10, 8))
        self.entry_busca.bind("<KeyRelease>", lambda _: self.atualizar_lista_e_marcadores())

        # 2. Linha dupla: Cidade + Conector
        linha_filtros_1 = ctk.CTkFrame(filtro_card, fg_color="transparent")
        linha_filtros_1.pack(fill="x", padx=10, pady=(0, 8))
        linha_filtros_1.grid_columnconfigure((0, 1), weight=1)

        self.combo_cidade = ctk.CTkComboBox(
            linha_filtros_1,
            values=["Todas as Cidades", "Belém", "Ananindeua"],
            command=lambda _: self.atualizar_lista_e_marcadores(),
            fg_color="#0B121A",
            button_color=COR_VERDE,
            button_hover_color=COR_VERDE_HOVER,
            border_color=COR_BORDA,
            dropdown_fg_color=COR_CARD,
            height=30,
            font=ctk.CTkFont(size=12),
        )
        self.combo_cidade.set("Todas as Cidades")
        self.combo_cidade.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.combo_conector = ctk.CTkComboBox(
            linha_filtros_1,
            values=["Todos Conectores", "CCS2 (Rápido)", "Tipo 2 (AC)", "CHAdeMO"],
            command=lambda _: self.atualizar_lista_e_marcadores(),
            fg_color="#0B121A",
            button_color="#233549",
            button_hover_color=COR_VERDE_HOVER,
            border_color=COR_BORDA,
            dropdown_fg_color=COR_CARD,
            height=30,
            font=ctk.CTkFont(size=12),
        )
        self.combo_conector.set("Todos Conectores")
        self.combo_conector.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # 3. Filtro rápido por tipo de carga (Segmented Button estilo Carregados.com.br)
        self.seg_tipo_carga = ctk.CTkSegmentedButton(
            filtro_card,
            values=["Todos", "⚡ Rápida (DC)", "🔌 Lenta/Semi (AC)", "✅ Disponíveis"],
            command=lambda _: self.atualizar_lista_e_marcadores(),
            fg_color="#0B121A",
            selected_color=COR_VERDE,
            selected_hover_color=COR_VERDE_HOVER,
            unselected_color="#111B26",
            unselected_hover_color="#1A2838",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
        )
        self.seg_tipo_carga.set("Todos")
        self.seg_tipo_carga.pack(fill="x", padx=10, pady=(0, 10))

        # Barra de contador + botão limpar filtros
        status_bar = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        status_bar.pack(fill="x", padx=16, pady=(0, 4))

        self.lbl_contador = ctk.CTkLabel(
            status_bar,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COR_TEXTO_MAIN,
        )
        self.lbl_contador.pack(side="left")

        btn_limpar = ctk.CTkButton(
            status_bar,
            text="Limpar filtros",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color="#182432",
            text_color=COR_VERDE,
            width=80,
            height=22,
            command=self.limpar_filtros,
        )
        btn_limpar.pack(side="right")

        # Lista rolável de cards de estações
        self.scroll_cards = ctk.CTkScrollableFrame(
            self.painel_lateral,
            fg_color="transparent",
            scrollbar_button_color="#1F2D3D",
            scrollbar_button_hover_color=COR_VERDE,
        )
        self.scroll_cards.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # =====================================================================
    # ÁREA DIREITA: BARRA DE MÉTRICAS, MAPA E DETALHES DO POSTO
    # =====================================================================

    def construir_area_mapa(self):
        self.area_direita = ctk.CTkFrame(self, fg_color=COR_FUNDO)
        self.area_direita.grid(row=0, column=1, sticky="nsew", padx=14, pady=14)
        self.area_direita.grid_columnconfigure(0, weight=1)
        self.area_direita.grid_rowconfigure(1, weight=1)

        # 1. Barra Superior de Estatísticas da Região (Panorama Carregados.com.br)
        top_stats = ctk.CTkFrame(
            self.area_direita,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=12,
        )
        top_stats.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_stats.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.lbl_stat_total = self._criar_mini_kpi(top_stats, 0, "Estações Mapeadas", "0", COR_VERDE)
        self.lbl_stat_dc = self._criar_mini_kpi(top_stats, 1, "Carga Rápida (DC)", "0", COR_AZUL_DC)
        self.lbl_stat_ac = self._criar_mini_kpi(top_stats, 2, "Carga AC (Tipo 2)", "0", COR_ROXO_AC)
        self.lbl_stat_preco = self._criar_mini_kpi(top_stats, 3, "Tarifa Média", "R$ 1.95/kWh", "#FFD700")

        # Controle de camada do mapa e visão geral
        ctrl_mapa = ctk.CTkFrame(top_stats, fg_color="transparent")
        ctrl_mapa.grid(row=0, column=4, padx=10, pady=8, sticky="e")

        self.combo_estilo_mapa = ctk.CTkOptionMenu(
            ctrl_mapa,
            values=["Mapa Padrão (OSM)", "Google Maps Rua", "Satélite Híbrido"],
            command=self.alterar_estilo_mapa,
            fg_color="#0D1620",
            button_color="#1C2C3E",
            button_hover_color=COR_VERDE_HOVER,
            dropdown_fg_color=COR_CARD,
            width=145,
            height=28,
            font=ctk.CTkFont(size=11),
        )
        self.combo_estilo_mapa.set("Mapa Padrão (OSM)")
        self.combo_estilo_mapa.pack(pady=(0, 4))

        ctk.CTkButton(
            ctrl_mapa,
            text="🎯 Visão Geral PA",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#182A22",
            hover_color="#213D30",
            border_width=1,
            border_color=COR_VERDE,
            text_color=COR_VERDE,
            width=145,
            height=26,
            command=self.centralizar_visao,
        ).pack()

        # 2. Container do Mapa Interativo
        frame_mapa = ctk.CTkFrame(
            self.area_direita,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=12,
        )
        frame_mapa.grid(row=1, column=0, sticky="nsew")

        self.map_widget = TkinterMapView(frame_mapa, corner_radius=12)
        self.map_widget.pack(fill="both", expand=True, padx=2, pady=2)
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        self.centralizar_visao()

        # 3. Card Inferior de Detalhes da Estação Selecionada
        self.painel_detalhe = ctk.CTkFrame(
            self.area_direita,
            fg_color=COR_CARD,
            border_width=1.5,
            border_color=COR_VERDE,
            corner_radius=12,
            height=115,
        )
        self.painel_detalhe.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.renderizar_detalhe_posto(self.todos_postos[0] if self.todos_postos else None)

    def _criar_mini_kpi(self, parent, col, titulo, valor, cor):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=col, padx=8, pady=8, sticky="w")
        ctk.CTkLabel(box, text=titulo, font=ctk.CTkFont(size=11), text_color=COR_TEXTO_MUTED).pack(anchor="w")
        lbl_val = ctk.CTkLabel(
            box,
            text=valor,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=cor,
        )
        lbl_val.pack(anchor="w")
        return lbl_val

    def alterar_estilo_mapa(self, escolha):
        if escolha == "Google Maps Rua":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=pt-BR&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif escolha == "Satélite Híbrido":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=y&hl=pt-BR&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        else:
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")

    def centralizar_visao(self):
        self.map_widget.set_position(-1.4050, -48.4450)
        self.map_widget.set_zoom(12)

    def limpar_filtros(self):
        self.busca_var.set("")
        self.combo_cidade.set("Todas as Cidades")
        self.combo_conector.set("Todos Conectores")
        self.seg_tipo_carga.set("Todos")
        self.atualizar_lista_e_marcadores()
        self.centralizar_visao()

    def focar_no_posto(self, posto):
        self.posto_selecionado = posto
        self.map_widget.set_position(posto["lat"], posto["lon"])
        self.map_widget.set_zoom(16)
        self.renderizar_detalhe_posto(posto)

    def abrir_rota_google_maps(self, posto):
        destino = urllib.parse.quote(f"{posto['nome']}, {posto['endereco']}")
        url = f"https://www.google.com/maps/dir/?api=1&destination={ posto['lat'] },{ posto['lon'] }& destination_place_id={destino}"
        webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={posto['lat']},{posto['lon']}")

    def simular_recarga_no_posto(self, posto):
        if posto.get("status") == "Manutenção":
            messagebox.showwarning(
                "Estação em Manutenção",
                f"A estação '{posto['nome']}' encontra-se temporariamente em manutenção preventiva.\n"
                "Por favor, selecione outro eletroposto disponível no mapa.",
            )
            return

        potencia = float(posto.get("potencia_kw", 60.0))
        preco = float(posto.get("preco_kwh", 1.95))
        energia_padrao = 30.0  # Simulação de recarga de 30 kWh (~20% a 80%)
        tempo_min = (energia_padrao / potencia) * 60.0
        custo_total = energia_padrao * preco

        messagebox.showinfo(
            "Estimativa de Recarga - EletroBel",
            f"⚡ {posto['nome']} ({posto.get('rede', 'EletroBel')})\n"
            f"📍 {posto['endereco']}\n\n"
            f"• Potência nominal: {potencia:.0f} kW ({posto.get('tipo_carga', 'DC')})\n"
            f"• Conectores: {posto.get('conector', 'CCS2')}\n"
            f"• Tarifa: R$ {preco:.2f}/kWh ({posto.get('acesso', 'Público')})\n"
            f"• Horário: {posto.get('horario', '24 horas')}\n\n"
            f"🔋 Simulação para +30 kWh de carga:\n"
            f"• Tempo estimado: ~{tempo_min:.0f} minutos\n"
            f"• Valor estimado: R$ {custo_total:.2f}",
        )

    def renderizar_detalhe_posto(self, posto):
        for widget in self.painel_detalhe.winfo_children():
            widget.destroy()

        if not posto:
            ctk.CTkLabel(
                self.painel_detalhe,
                text="Selecione um eletroposto na lista ou no mapa para visualizar detalhes e traçar rota.",
                font=ctk.CTkFont(size=13),
                text_color=COR_TEXTO_MUTED,
            ).pack(expand=True, pady=25)
            return

        container = ctk.CTkFrame(self.painel_detalhe, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=16, pady=10)

        # Coluna esquerda: informações completas
        esq = ctk.CTkFrame(container, fg_color="transparent")
        esq.pack(side="left", fill="both", expand=True)

        linha_titulo = ctk.CTkFrame(esq, fg_color="transparent")
        linha_titulo.pack(fill="x")

        ctk.CTkLabel(
            linha_titulo,
            text=f"⚡ {posto['nome']}",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COR_TEXTO_MAIN,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            linha_titulo,
            text=f"Rede: {posto.get('rede', 'EletroBel')}  •  Bairro: {posto.get('bairro', posto['cidade'])}  •  🕒 {posto.get('horario', '24h')}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_AZUL_DC,
        ).pack(side="left")

        ctk.CTkLabel(
            esq,
            text=f"📍 {posto['endereco']}",
            font=ctk.CTkFont(size=12),
            text_color=COR_TEXTO_MUTED,
        ).pack(anchor="w", pady=(2, 4))

        especs_texto = (
            f"Potência: {posto['potencia_kw']:.0f} kW ({posto['tipo_carga']})   |   "
            f"Conectores: {posto['conector']}   |   "
            f"Tarifa: R$ {posto['preco_kwh']:.2f}/kWh   |   "
            f"Acesso: {posto.get('acesso', 'Público')}"
        )
        ctk.CTkLabel(
            esq,
            text=especs_texto,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COR_VERDE,
        ).pack(anchor="w")

        # Coluna direita: botões de ação (Rota no Google Maps e Estimativa de Recarga)
        dir_acoes = ctk.CTkFrame(container, fg_color="transparent")
        dir_acoes.pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            dir_acoes,
            text="🗺️ Traçar Rota (Maps)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COR_VERDE,
            hover_color=COR_VERDE_HOVER,
            text_color="#000000",
            width=165,
            height=32,
            corner_radius=8,
            command=lambda p=posto: self.abrir_rota_google_maps(p),
        ).pack(pady=(0, 6))

        ctk.CTkButton(
            dir_acoes,
            text="⚡ Simular Recarga",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#182A22",
            hover_color="#213D30",
            border_width=1,
            border_color=COR_VERDE,
            text_color=COR_VERDE,
            width=165,
            height=30,
            corner_radius=8,
            command=lambda p=posto: self.simular_recarga_no_posto(p),
        ).pack()

    # =====================================================================
    # ATUALIZAÇÃO DOS FILTROS, CARDS E MARCADORES NO MAPA
    # =====================================================================

    def _cor_por_status(self, status: str) -> str:
        if status == "Disponível":
            return COR_VERDE
        if status == "Manutenção":
            return COR_MANUTENCAO
        return COR_OCUPADO

    def atualizar_lista_e_marcadores(self):
        for widget in self.scroll_cards.winfo_children():
            widget.destroy()

        for marcador in self.marcadores_no_mapa:
            marcador.delete()
        self.marcadores_no_mapa.clear()

        termo = self.busca_var.get().strip().lower()
        filtro_cidade = self.combo_cidade.get()
        filtro_conector = self.combo_conector.get()
        filtro_carga = self.seg_tipo_carga.get()

        postos_filtrados = []
        for p in self.todos_postos:
            # 1. Filtro de Cidade
            if filtro_cidade != "Todas as Cidades" and p["cidade"] != filtro_cidade:
                continue

            # 2. Filtro de Conector
            conector_upper = p["conector"].upper()
            if filtro_conector == "CCS2 (Rápido)" and "CCS2" not in conector_upper:
                continue
            elif filtro_conector == "Tipo 2 (AC)" and "TIPO 2" not in conector_upper:
                continue
            elif filtro_conector == "CHAdeMO" and "CHADEMO" not in conector_upper:
                continue

            # 3. Filtro de Tipo de Carga / Disponibilidade
            if filtro_carga == "⚡ Rápida (DC)" and p["potencia_kw"] < 50.0:
                continue
            elif filtro_carga == "🔌 Lenta/Semi (AC)" and p["potencia_kw"] >= 50.0:
                continue
            elif filtro_carga == "✅ Disponíveis" and p["status"] != "Disponível":
                continue

            # 4. Filtro por texto livre (nome, bairro, endereço, rede)
            if termo:
                alvo_busca = f"{p['nome']} {p.get('bairro', '')} {p['endereco']} {p.get('rede', '')}".lower()
                if termo not in alvo_busca:
                    continue

            postos_filtrados.append(p)

        # Atualiza KPIs do topo
        total = len(postos_filtrados)
        qtd_dc = sum(1 for p in postos_filtrados if p["potencia_kw"] >= 50.0)
        qtd_ac = sum(1 for p in postos_filtrados if p["potencia_kw"] < 50.0)
        preco_medio = (
            sum(p["preco_kwh"] for p in postos_filtrados) / total if total > 0 else 0.0
        )

        self.lbl_stat_total.configure(text=f"{total} postos")
        self.lbl_stat_dc.configure(text=f"{qtd_dc} rápidos (DC)")
        self.lbl_stat_ac.configure(text=f"{qtd_ac} pontos (AC)")
        self.lbl_stat_preco.configure(text=f"R$ {preco_medio:.2f}/kWh")
        self.lbl_contador.configure(text=f"⚡ {total} eletroposto(s) encontrado(s)")

        if not postos_filtrados:
            vazio = ctk.CTkFrame(self.scroll_cards, fg_color=COR_CARD, corner_radius=10)
            vazio.pack(fill="x", pady=15, padx=6, ipady=20)
            ctk.CTkLabel(
                vazio,
                text="Nenhum eletroposto encontrado para os filtros aplicados.",
                font=ctk.CTkFont(size=12),
                text_color=COR_TEXTO_MUTED,
            ).pack()
            return

        for posto in postos_filtrados:
            cor_status = self._cor_por_status(posto["status"])
            cor_pino_Fora = "#008040" if posto["status"] == "Disponível" else ("#B71C1C" if posto["status"] == "Manutenção" else "#E65100")

            marcador = self.map_widget.set_marker(
                posto["lat"],
                posto["lon"],
                text=f"{posto['nome']} ({posto['potencia_kw']:.0f}kW)",
                marker_color_circle=cor_status,
                marker_color_outside=cor_pino_Fora,
                command=lambda m, p=posto: self.focar_no_posto(p),
            )
            self.marcadores_no_mapa.append(marcador)

            # Card lateral do eletroposto
            card = ctk.CTkFrame(
                self.scroll_cards,
                fg_color=COR_CARD,
                border_width=1,
                border_color=COR_BORDA,
                corner_radius=12,
            )
            card.pack(fill="x", pady=5, padx=2)

            # Linha 1: Nome e Status
            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=12, pady=(10, 2))

            ctk.CTkLabel(
                topo,
                text=posto["nome"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COR_TEXTO_MAIN,
            ).pack(side="left")

            ctk.CTkLabel(
                topo,
                text=f"● {posto['status']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=cor_status,
            ).pack(side="right")

            # Linha 2: Rede, Bairro e Acesso
            sub_topo = ctk.CTkFrame(card, fg_color="transparent")
            sub_topo.pack(fill="x", padx=12, pady=(0, 4))

            ctk.CTkLabel(
                sub_topo,
                text=f"🏷️ {posto.get('rede', 'EletroBel')}  •  {posto.get('bairro', posto['cidade'])} ({posto.get('acesso', 'Público')})",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COR_AZUL_DC if posto["potencia_kw"] >= 50 else COR_ROXO_AC,
            ).pack(side="left")

            # Linha 3: Endereço
            ctk.CTkLabel(
                card,
                text=f"📍 {posto['endereco']}",
                font=ctk.CTkFont(size=11),
                text_color=COR_TEXTO_MUTED,
                wraplength=360,
                justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 6))

            # Linha 4: Especificações técnicas e preço
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=12, pady=(0, 8))

            ctk.CTkLabel(
                info_frame,
                text=f"⚡ {posto['potencia_kw']:.0f} kW ({posto['tipo_carga']})  |  🔌 {posto['conector']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COR_VERDE,
            ).pack(side="left")

            ctk.CTkLabel(
                info_frame,
                text=f"R$ {posto['preco_kwh']:.2f}/kWh",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COR_TEXTO_MAIN,
            ).pack(side="right")

            # Linha 5: Botões de ação rápida
            botoes_frame = ctk.CTkFrame(card, fg_color="transparent")
            botoes_frame.pack(fill="x", padx=12, pady=(0, 10))
            botoes_frame.grid_columnconfigure((0, 1), weight=1)

            ctk.CTkButton(
                botoes_frame,
                text="📍 Focar no Mapa",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#182A22",
                border_width=1,
                border_color=COR_VERDE,
                text_color=COR_VERDE,
                hover_color="#213D30",
                height=28,
                command=lambda p=posto: self.focar_no_posto(p),
            ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

            ctk.CTkButton(
                botoes_frame,
                text="🗺️ Abrir Rota",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#162230",
                border_width=1,
                border_color=COR_BORDA,
                text_color=COR_TEXTO_MAIN,
                hover_color="#22354A",
                height=28,
                command=lambda p=posto: self.abrir_rota_google_maps(p),
            ).grid(row=0, column=1, padx=(4, 0), sticky="ew")


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("EletroBel - Mapa de Eletropostos (Belém e Ananindeua)")
    app.geometry("1200x760")
    EletroBelApp(app, lambda: print("Retornar ao menu"))
    app.mainloop()
