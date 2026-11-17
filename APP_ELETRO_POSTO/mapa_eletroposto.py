import urllib.parse
import webbrowser
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from tkintermapview import TkinterMapView
import database

# Paleta de cores inspirada fielmente em https://carregados.com.br/estacoes?cidade=belém&estado=pará+(pa)
COR_FUNDO = "#090D14"
COR_PAINEL = "#0F1622"
COR_CARD = "#131C2B"
COR_CARD_HOVER = "#192538"
COR_CARD_SELECIONADO = "#172940"
COR_BORDA = "#223044"
COR_TEXTO = "#F8FAFC"
COR_TEXTO_MUTED = "#94A3B8"

# Cores oficiais da legenda do mapa Carregados.com.br
COR_CARGA_RAPIDA = "#3B82F6"   # bg-blue-500 (Carga rápida)
COR_PUBLICO = "#22C55E"        # bg-green-500 (Público)
COR_RESTRITO = "#FB7185"       # bg-rose-400 (Uso restrito)
COR_MANUTENCAO = "#EF4444"     # bg-red-500 (Manutenção / Ocupado)
COR_PRIMARIA = "#22C55E"
COR_PRIMARIA_HOVER = "#16A34A"

# Estações reais mapeadas em Belém / Pará extraídas do modelo Carregados.com.br
# e integradas às estações do banco de dados MySQL (eletrobel_posto)
CATALOGO_CARREGADOS_PA = [
    {
        "nome": "Boulevard Shopping Belém",
        "aliases": ["Estação EletroBel Doca"],
        "cidade": "Belém",
        "bairro": "Reduto",
        "endereco": "Av. Visc. de Souza Franco, 776 - Reduto, Belém - PA, 66055-005",
        "acesso": "Público",
        "carga_rapida": True,
        "qtd_estacoes": 6,
        "potencia_kw": 34.1,
        "tipo_conector": "CCS2 / Tipo 2",
        "preco_kwh": 1.95,
        "status": "Disponível",
        "operadora": "EletroBel / Boulevard",
        "lat": -1.446455,
        "lon": -48.490301,
    },
    {
        "nome": "UFPA - Cidade Universitária",
        "aliases": [],
        "cidade": "Belém",
        "bairro": "Guamá",
        "endereco": "R. Igarapé Tucunduba, 976 - Guamá, Belém - PA, 66075-123",
        "acesso": "Uso restrito",
        "carga_rapida": False,
        "qtd_estacoes": 1,
        "potencia_kw": 22.0,
        "tipo_conector": "Tipo 2",
        "preco_kwh": 1.40,
        "status": "Restrito",
        "operadora": "UFPA",
        "lat": -1.473639,
        "lon": -48.455471,
    },
    {
        "nome": "Preço Baixo - Augusto Montenegro",
        "aliases": ["Estação BRT Augusto Montenegro"],
        "cidade": "Belém",
        "bairro": "Castanheira / Parque Verde",
        "endereco": "Rod. Augusto Montenegro, 290 - Castanheira, Belém - PA, 66635",
        "acesso": "Público",
        "carga_rapida": True,
        "qtd_estacoes": 2,
        "potencia_kw": 119.7,
        "tipo_conector": "CCS2 / Tipo 2",
        "preco_kwh": 1.85,
        "status": "Disponível",
        "operadora": "PlugBRA / EletroBel",
        "lat": -1.363527,
        "lon": -48.450135,
    },
    {
        "nome": "Líder Doca",
        "aliases": [],
        "cidade": "Belém",
        "bairro": "Reduto",
        "endereco": "Av. Visc. de Souza Franco, 1088 - Reduto, Belém - PA, 66053-000",
        "acesso": "Público",
        "carga_rapida": False,
        "qtd_estacoes": 1,
        "potencia_kw": 22.0,
        "tipo_conector": "Tipo 2",
        "preco_kwh": 1.75,
        "status": "Disponível",
        "operadora": "Rede Líder",
        "lat": -1.447807,
        "lon": -48.488038,
    },
    {
        "nome": "PlugBRA - Senador Lemos",
        "aliases": [],
        "cidade": "Belém",
        "bairro": "Sacramenta",
        "endereco": "Av. Sen. Lemos, 2842 - Sacramenta, Belém - PA, 66120-000",
        "acesso": "Público",
        "carga_rapida": True,
        "qtd_estacoes": 2,
        "potencia_kw": 55.2,
        "tipo_conector": "CCS2",
        "preco_kwh": 1.92,
        "status": "Disponível",
        "operadora": "PlugBRA",
        "lat": -1.419715,
        "lon": -48.480316,
    },
    {
        "nome": "PlugBRA Econômico - Marambaia",
        "aliases": [],
        "cidade": "Belém",
        "bairro": "Marambaia",
        "endereco": "Av. Pedro Álvares Cabral, 70 - Marambaia, Belém - PA, 66050-400",
        "acesso": "Público",
        "carga_rapida": True,
        "qtd_estacoes": 2,
        "potencia_kw": 87.8,
        "tipo_conector": "CCS2 / Tipo 2",
        "preco_kwh": 1.69,
        "status": "Disponível",
        "operadora": "PlugBRA",
        "lat": -1.436236,
        "lon": -48.491990,
    },
    {
        "nome": "Estação das Docas",
        "aliases": ["Docas"],
        "cidade": "Belém",
        "bairro": "Campina",
        "endereco": "Blvd. Castilhos França, 3 - Campina, Belém - PA, 66010",
        "acesso": "Público",
        "carga_rapida": False,
        "qtd_estacoes": 2,
        "potencia_kw": 6.0,
        "tipo_conector": "Tipo 2",
        "preco_kwh": 1.50,
        "status": "Disponível",
        "operadora": "Amazônia Plug",
        "lat": -1.448217,
        "lon": -48.499326,
    },
    {
        "nome": "Shopping Bosque Grão-Pará",
        "aliases": ["Estação Shopping Bosque Grão-Pará"],
        "cidade": "Belém",
        "bairro": "Val-de-Cans",
        "endereco": "Av. Centenário, 1052 (Av. dos Trabalhadores) - Belém - PA",
        "acesso": "Público",
        "carga_rapida": True,
        "qtd_estacoes": 9,
        "potencia_kw": 60.0,
        "tipo_conector": "CCS2",
        "preco_kwh": 2.10,
        "status": "Disponível",
        "operadora": "Tupinambá / EletroBel",
        "lat": -1.389970,
        "lon": -48.464353,
    },
    {
        "nome": "Aeroporto Internacional de Belém",
        "aliases": ["Estação Aeroporto Internacional"],
        "cidade": "Belém",
        "bairro": "Val-de-Cans",
        "endereco": "Av. Júlio César, s/n - Val-de-Cans, Belém - PA",
        "acesso": "Público",
        "carga_rapida": True,
        "qtd_estacoes": 2,
        "potencia_kw": 100.0,
        "tipo_conector": "CCS2",
        "preco_kwh": 2.30,
        "status": "Manutenção",
        "operadora": "EletroBel",
        "lat": -1.384700,
        "lon": -48.476400,
    },
    {
        "nome": "Shopping Metrópole Ananindeua",
        "aliases": ["Estação Metrópole Ananindeua"],
        "cidade": "Ananindeua",
        "bairro": "Coqueiro",
        "endereco": "Rodovia BR-316, Km 4 - Coqueiro, Ananindeua - PA",
        "acesso": "Público",
        "carga_rapida": True,
        "qtd_estacoes": 4,
        "potencia_kw": 120.0,
        "tipo_conector": "CCS2 / CHAdeMO",
        "preco_kwh": 1.90,
        "status": "Disponível",
        "operadora": "EletroBel",
        "lat": -1.365500,
        "lon": -48.374800,
    },
    {
        "nome": "Estação Cidade Nova",
        "aliases": [],
        "cidade": "Ananindeua",
        "bairro": "Cidade Nova",
        "endereco": "Av. Arterial 18, 400 - Cidade Nova, Ananindeua - PA",
        "acesso": "Público",
        "carga_rapida": False,
        "qtd_estacoes": 2,
        "potencia_kw": 22.0,
        "tipo_conector": "Tipo 2",
        "preco_kwh": 1.45,
        "status": "Disponível",
        "operadora": "EletroBel",
        "lat": -1.351200,
        "lon": -48.403500,
    },
]


def criar_icone_pino_localizacao(cor_hex: str, selecionado: bool = False) -> ImageTk.PhotoImage:
    """
    Desenha um ícone de pino de localização limpo (sem texto), com anti-aliasing (4x supersampling),
    seguindo as cores da legenda do Carregados.com.br.
    """
    escala = 4
    largura = (38 if selecionado else 30) * escala
    altura = (48 if selecionado else 38) * escala
    img = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = largura // 2
    raio = int(largura * 0.36)
    cy = raio + (3 * escala)
    ponta_y = altura - (2 * escala)

    # Sombra suave na base do pino
    sombra_rx = int(raio * 0.45)
    sombra_ry = int(2.5 * escala)
    draw.ellipse(
        (cx - sombra_rx, ponta_y - sombra_ry, cx + sombra_rx, ponta_y + sombra_ry),
        fill=(0, 0, 0, 95),
    )

    # Borda externa branca (destaque no mapa)
    espessura_borda = (3 if selecionado else 2) * escala
    raio_ext = raio + espessura_borda
    draw.ellipse(
        (cx - raio_ext, cy - raio_ext, cx + raio_ext, cy + raio_ext),
        fill=(255, 255, 255, 255),
    )
    draw.polygon(
        [
            (cx - int(raio_ext * 0.72), cy + int(raio_ext * 0.50)),
            (cx + int(raio_ext * 0.72), cy + int(raio_ext * 0.50)),
            (cx, ponta_y),
        ],
        fill=(255, 255, 255, 255),
    )

    # Corpo colorido do pino de localização
    draw.ellipse(
        (cx - raio, cy - raio, cx + raio, cy + raio),
        fill=cor_hex,
    )
    draw.polygon(
        [
            (cx - int(raio * 0.70), cy + int(raio * 0.48)),
            (cx + int(raio * 0.70), cy + int(raio * 0.48)),
            (cx, ponta_y - espessura_borda),
        ],
        fill=cor_hex,
    )

    # Círculo interno branco do ícone de localização
    raio_interno = int(raio * 0.42)
    draw.ellipse(
        (cx - raio_interno, cy - raio_interno, cx + raio_interno, cy + raio_interno),
        fill="#FFFFFF",
    )

    img_final = img.resize((largura // escala, altura // escala), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img_final)


def carregar_estacoes_integradas():
    """
    Integra os dados do banco MySQL (`database.listar_estacoes()`) com o catálogo
    de eletropostos de Belém e Pará no padrão Carregados.com.br.
    """
    estacoes = [dict(item) for item in CATALOGO_CARREGADOS_PA]

    try:
        registros_mysql = database.listar_estacoes()
    except Exception:
        registros_mysql = []

    nomes_conhecidos = set()
    for item in estacoes:
        nomes_conhecidos.add(item["nome"].lower())
        for al in item.get("aliases", []):
            nomes_conhecidos.add(al.lower())

    for idx, reg in enumerate(registros_mysql):
        nome_bd = (reg.get("nome") or "").strip()
        if not nome_bd:
            continue

        # Atualiza dados caso corresponda a um item do catálogo
        atualizado = False
        for item in estacoes:
            if nome_bd.lower() == item["nome"].lower() or nome_bd.lower() in [a.lower() for a in item.get("aliases", [])]:
                if reg.get("preco_kwh") is not None:
                    item["preco_kwh"] = float(reg["preco_kwh"])
                if reg.get("tipo_conector"):
                    item["tipo_conector"] = reg["tipo_conector"]
                if reg.get("status"):
                    st = reg["status"]
                    if st in ("Ocupado", "Manutenção"):
                        item["status"] = st
                atualizado = True
                break

        # Se for uma nova estação cadastrada no MySQL, adiciona ao mapa
        if not atualizado and nome_bd.lower() not in nomes_conhecidos:
            pot = float(reg.get("potencia_kw") or 50.0)
            end = reg.get("endereco") or "Belém - PA"
            cidade = "Ananindeua" if "ananindeua" in end.lower() else "Belém"
            estacoes.append({
                "nome": nome_bd,
                "aliases": [],
                "cidade": cidade,
                "bairro": "Centro",
                "endereco": end,
                "acesso": "Público",
                "carga_rapida": pot >= 50.0,
                "qtd_estacoes": 2,
                "potencia_kw": pot,
                "tipo_conector": reg.get("tipo_conector") or "CCS2 / Tipo 2",
                "preco_kwh": float(reg.get("preco_kwh") or 1.95),
                "status": reg.get("status") or "Disponível",
                "operadora": "EletroBel",
                "lat": -1.4350 + (idx * 0.008),
                "lon": -48.4700 + (idx * 0.008),
            })

    return estacoes


class EletroBelApp(ctk.CTkFrame):
    def __init__(self, master, abrir_menu_callback):
        for widget in master.winfo_children():
            widget.destroy()

        super().__init__(master, fg_color=COR_FUNDO)
        self.pack(fill="both", expand=True)

        self.abrir_menu_callback = abrir_menu_callback
        self.marcadores_no_mapa = []
        self.icones_cache = {}
        self.dados_postos = carregar_estacoes_integradas()
        self.posto_selecionado = None
        self.categoria_ativa = "Todos"

        # Layout responsivo: Coluna esquerda (lista estilo Carregados) + Coluna direita (Mapa + Legenda)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.construir_painel_lateral()
        self.construir_area_mapa()
        self.atualizar_lista_e_marcadores()

    def _obter_cor_categoria(self, posto: dict) -> str:
        """Retorna a cor do pino seguindo a legenda do Carregados.com.br."""
        if posto.get("status") in ("Manutenção", "Ocupado"):
            return COR_MANUTENCAO
        if posto.get("acesso") == "Uso restrito" or posto.get("status") == "Restrito":
            return COR_RESTRITO
        if posto.get("carga_rapida") or float(posto.get("potencia_kw", 0)) >= 50.0:
            return COR_CARGA_RAPIDA
        return COR_PUBLICO

    def _obter_icone_pino(self, posto: dict, selecionado: bool = False) -> ImageTk.PhotoImage:
        cor = self._obter_cor_categoria(posto)
        chave = (cor, selecionado)
        if chave not in self.icones_cache:
            self.icones_cache[chave] = criar_icone_pino_localizacao(cor, selecionado=selecionado)
        return self.icones_cache[chave]

    def voltar(self):
        self.destroy()
        self.abrir_menu_callback()

    def abrir_rota_google_maps(self, posto: dict):
        destino = urllib.parse.quote(f"{posto['nome']}, {posto['endereco']}")
        url = f"https://www.google.com/maps/dir/?api=1&destination={posto['lat']},{posto['lon']}&query={destino}"
        webbrowser.open(url)

    def construir_painel_lateral(self):
        self.painel_lateral = ctk.CTkFrame(
            self,
            width=460,
            corner_radius=0,
            fg_color=COR_PAINEL,
        )
        self.painel_lateral.grid(row=0, column=0, sticky="nsew", padx=(14, 6), pady=14)
        self.painel_lateral.grid_propagate(False)

        # Barra de navegação superior (Breadcrumb estilo Carregados.com.br)
        nav_bar = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        nav_bar.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkButton(
            nav_bar,
            text="← Voltar ao Menu",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            text_color=COR_PRIMARIA,
            hover_color=COR_CARD,
            anchor="w",
            height=26,
            width=120,
            command=self.voltar,
        ).pack(side="left")

        ctk.CTkLabel(
            nav_bar,
            text="Brasil  /  Pará  /  Belém",
            font=ctk.CTkFont(size=11),
            text_color=COR_TEXTO_MUTED,
        ).pack(side="right")

        # Cabeçalho Principal ("Eletropostos e estações de recarga Belém PA")
        header = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(2, 8))

        ctk.CTkLabel(
            header,
            text="Eletropostos e estações de recarga",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_PRIMARIA,
        ).pack(anchor="w")

        titulo_frame = ctk.CTkFrame(header, fg_color="transparent")
        titulo_frame.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(
            titulo_frame,
            text="Belém",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COR_TEXTO,
        ).pack(side="left")

        badge_uf = ctk.CTkLabel(
            titulo_frame,
            text=" PA ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COR_CARD,
            text_color=COR_TEXTO_MUTED,
            corner_radius=6,
        )
        badge_uf.pack(side="left", padx=8, pady=2)

        ctk.CTkLabel(
            titulo_frame,
            text="Preço médio: R$ 1,92/kWh",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_CARGA_RAPIDA,
        ).pack(side="right")

        self.lbl_resumo_topo = ctk.CTkLabel(
            header,
            text="39 eletropostos na região, abertos ao público e com carga rápida.",
            font=ctk.CTkFont(size=11),
            text_color=COR_TEXTO_MUTED,
        )
        self.lbl_resumo_topo.pack(anchor="w")

        # Seletores de Estado / Cidade + Busca
        filtro_box = ctk.CTkFrame(
            self.painel_lateral,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=10,
        )
        filtro_box.pack(fill="x", padx=14, pady=(0, 8))

        linha_cidade = ctk.CTkFrame(filtro_box, fg_color="transparent")
        linha_cidade.pack(fill="x", padx=10, pady=(8, 6))

        ctk.CTkLabel(
            linha_cidade,
            text="Cidade:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_TEXTO_MUTED,
        ).pack(side="left", padx=(0, 6))

        self.combo_cidade = ctk.CTkComboBox(
            linha_cidade,
            values=["Belém e Região (PA)", "Belém", "Ananindeua"],
            command=lambda _: self.atualizar_lista_e_marcadores(),
            fg_color=COR_FUNDO,
            button_color=COR_PRIMARIA,
            button_hover_color=COR_PRIMARIA_HOVER,
            border_color=COR_BORDA,
            dropdown_fg_color=COR_CARD,
            height=28,
            width=175,
        )
        self.combo_cidade.pack(side="left", fill="x", expand=True)

        self.entry_busca = ctk.CTkEntry(
            linha_cidade,
            placeholder_text="🔍 Filtrar posto ou bairro...",
            fg_color=COR_FUNDO,
            border_color=COR_BORDA,
            text_color=COR_TEXTO,
            height=28,
            width=175,
        )
        self.entry_busca.pack(side="left", padx=(8, 0), fill="x", expand=True)
        self.entry_busca.bind("<KeyRelease>", lambda _: self.atualizar_lista_e_marcadores())

        # Botões de filtro rápido iguais às categorias do mapa Carregados.com.br
        pills_frame = ctk.CTkFrame(filtro_box, fg_color="transparent")
        pills_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.botoes_categoria = {}
        categorias = [
            ("Todos", "#334155"),
            ("Carga rápida", COR_CARGA_RAPIDA),
            ("Público", COR_PUBLICO),
            ("Restrito", COR_RESTRITO),
            ("Manutenção", COR_MANUTENCAO),
        ]
        for nome_cat, cor_cat in categorias:
            btn = ctk.CTkButton(
                pills_frame,
                text=nome_cat,
                font=ctk.CTkFont(size=10, weight="bold"),
                height=24,
                 width=68,
                corner_radius=12,
                fg_color=cor_cat if nome_cat == "Todos" else "transparent",
                border_width=1,
                border_color=cor_cat,
                text_color="#FFFFFF" if nome_cat == "Todos" else COR_TEXTO_MUTED,
                hover_color=COR_CARD_HOVER,
                command=lambda c=nome_cat: self.selecionar_categoria(c),
            )
            btn.pack(side="left", padx=2, expand=True, fill="x")
            self.botoes_categoria[nome_cat] = (btn, cor_cat)

        # Cabeçalho da lista ("Eletropostos em Belém  •  Mais avaliados primeiro")
        lista_header = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        lista_header.pack(fill="x", padx=14, pady=(2, 4))

        self.lbl_titulo_lista = ctk.CTkLabel(
            lista_header,
            text="Eletropostos em Belém",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COR_TEXTO,
        )
        self.lbl_titulo_lista.pack(side="left")

        self.lbl_contador = ctk.CTkLabel(
            lista_header,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COR_TEXTO_MUTED,
        )
        self.lbl_contador.pack(side="right")

        # Lista rolável de cards de estações
        self.scroll_cards = ctk.CTkScrollableFrame(
            self.painel_lateral,
            fg_color="transparent",
            corner_radius=8,
        )
        self.scroll_cards.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def selecionar_categoria(self, categoria: str):
        self.categoria_ativa = categoria
        for nome_cat, (btn, cor_cat) in self.botoes_categoria.items():
            ativo = nome_cat == categoria
            btn.configure(
                fg_color=cor_cat if ativo else "transparent",
                text_color="#FFFFFF" if ativo else COR_TEXTO_MUTED,
            )
        self.atualizar_lista_e_marcadores()

    def construir_area_mapa(self):
        frame_direita = ctk.CTkFrame(
            self,
            fg_color=COR_PAINEL,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=12,
        )
        frame_direita.grid(row=0, column=1, sticky="nsew", padx=(6, 14), pady=14)
        frame_direita.grid_rowconfigure(1, weight=1)
        frame_direita.grid_columnconfigure(0, weight=1)

        # Topo do mapa ("Veja os eletropostos no mapa — Cada ponto abre os detalhes sem sair da página.")
        barra_mapa = ctk.CTkFrame(frame_direita, fg_color="transparent")
        barra_mapa.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 6))

        textos_mapa = ctk.CTkFrame(barra_mapa, fg_color="transparent")
        textos_mapa.pack(side="left")

        ctk.CTkLabel(
            textos_mapa,
            text="Veja os eletropostos no mapa",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COR_TEXTO,
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos_mapa,
            text="Cada ícone de localização abre os detalhes sem sair da página.",
            font=ctk.CTkFont(size=11),
            text_color=COR_TEXTO_MUTED,
        ).pack(anchor="w")

        controles_mapa = ctk.CTkFrame(barra_mapa, fg_color="transparent")
        controles_mapa.pack(side="right")

        self.combo_estilo_mapa = ctk.CTkComboBox(
            controles_mapa,
            values=["Mapa Padrão", "Satélite", "OpenStreetMap"],
            command=self.alterar_estilo_mapa,
            width=140,
            height=28,
            fg_color=COR_CARD,
            button_color=COR_PRIMARIA,
            border_color=COR_BORDA,
        )
        self.combo_estilo_mapa.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            controles_mapa,
            text="Centralizar Belém",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COR_CARD,
            hover_color=COR_CARD_HOVER,
            text_color=COR_TEXTO,
            border_width=1,
            border_color=COR_BORDA,
            width=125,
            height=28,
            command=self.centralizar_visao,
        ).pack(side="left")

        # Container do widget de mapa
        self.container_mapa = ctk.CTkFrame(frame_direita, fg_color=COR_FUNDO, corner_radius=10)
        self.container_mapa.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 6))

        self.map_widget = TkinterMapView(self.container_mapa, corner_radius=10)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=pt-BR&x={x}&y={y}&z={z}&s=Ga",
            max_zoom=22,
        )

        # Card flutuante de detalhes do ponto selecionado no mapa (abre ao clicar no ícone)
        self.card_detalhe_mapa = ctk.CTkFrame(
            self.container_mapa,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=12,
        )

        # Rodapé de legenda idêntico ao modelo Carregados.com.br:
        # ● Carga rápida   ● Público   ● Restrito   ● Manutenção
        legenda_bar = ctk.CTkFrame(frame_direita, fg_color="transparent")
        legenda_bar.grid(row=2, column=0, sticky="ew", padx=14, pady=(2, 10))

        itens_legenda = [
            ("Carga rápida", COR_CARGA_RAPIDA),
            ("Público", COR_PUBLICO),
            ("Restrito", COR_RESTRITO),
            ("Manutenção", COR_MANUTENCAO),
        ]
        for texto_leg, cor_leg in itens_legenda:
            item_f = ctk.CTkFrame(legenda_bar, fg_color="transparent")
            item_f.pack(side="left", padx=(0, 18))

            ctk.CTkLabel(
                item_f,
                text="●",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=cor_leg,
            ).pack(side="left", padx=(0, 5))

            ctk.CTkLabel(
                item_f,
                text=texto_leg,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COR_TEXTO_MUTED,
            ).pack(side="left")

        self.centralizar_visao()

    def mostrar_detalhe_no_mapa(self, posto: dict):
        """Exibe o card compacto de detalhes quando o usuário clica em um pino no mapa."""
        for w in self.card_detalhe_mapa.winfo_children():
            w.destroy()

        topo = ctk.CTkFrame(self.card_detalhe_mapa, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            topo,
            text=posto["nome"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COR_TEXTO,
        ).pack(side="left")

        ctk.CTkButton(
            topo,
            text="✕",
            width=24,
            height=24,
            fg_color="transparent",
            hover_color=COR_CARD_HOVER,
            text_color=COR_TEXTO_MUTED,
            command=self.fechar_detalhe_mapa,
        ).pack(side="right")

        ctk.CTkLabel(
            self.card_detalhe_mapa,
            text=posto["endereco"],
            font=ctk.CTkFont(size=11),
            text_color=COR_TEXTO_MUTED,
        ).pack(anchor="w", padx=14, pady=(0, 6))

        badges = ctk.CTkFrame(self.card_detalhe_mapa, fg_color="transparent")
        badges.pack(fill="x", padx=14, pady=(0, 10))

        cor_acesso = COR_PUBLICO if posto["acesso"] == "Público" else COR_RESTRITO
        ctk.CTkLabel(
            badges,
            text=f"  {posto['acesso']}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#132A20" if posto["acesso"] == "Público" else "#2D1622",
            text_color=cor_acesso,
            corner_radius=6,
        ).pack(side="left", padx=(0, 6))

        if posto.get("carga_rapida"):
            ctk.CTkLabel(
                badges,
                text="  ⚡ Carga rápida  ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#12243E",
                text_color=COR_CARGA_RAPIDA,
                corner_radius=6,
            ).pack(side="left", padx=(0, 6))

        qtd_est = posto.get("qtd_estacoes", 1)
        plural = "estações" if qtd_est > 1 else "estação"
        ctk.CTkLabel(
            badges,
            text=f"{qtd_est} {plural}  •  {posto['potencia_kw']:g} kW  •  {posto['tipo_conector']}  •  R$ {posto['preco_kwh']:.2f}/kWh",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COR_TEXTO,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            badges,
            text="Como chegar ↗",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COR_PRIMARIA,
            hover_color=COR_PRIMARIA_HOVER,
            text_color="#051B0C",
            height=26,
            width=110,
            corner_radius=8,
            command=lambda p=posto: self.abrir_rota_google_maps(p),
        ).pack(side="right")

        self.card_detalhe_mapa.place(relx=0.02, rely=0.97, relwidth=0.96, anchor="sw")

    def fechar_detalhe_mapa(self):
        self.posto_selecionado = None
        self.card_detalhe_mapa.place_forget()

    def alterar_estilo_mapa(self, estilo: str):
        if estilo == "Satélite":
            self.map_widget.set_tile_server(
                "https://mt0.google.com/vt/lyrs=y&hl=pt-BR&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22,
            )
        elif estilo == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        else:
            self.map_widget.set_tile_server(
                "https://mt0.google.com/vt/lyrs=m&hl=pt-BR&x={x}&y={y}&z={z}&s=Ga",
                max_zoom=22,
            )

    def centralizar_visao(self):
        self.fechar_detalhe_mapa()
        self.map_widget.set_position(-1.4250, -48.4650)
        self.map_widget.set_zoom(12)

    def focar_no_posto(self, posto: dict):
        self.posto_selecionado = posto
        self.map_widget.set_position(posto["lat"], posto["lon"])
        self.map_widget.set_zoom(15)
        self.mostrar_detalhe_no_mapa(posto)

    def atualizar_lista_e_marcadores(self):
        for widget in self.scroll_cards.winfo_children():
            widget.destroy()

        for marcador in self.marcadores_no_mapa:
            marcador.delete()
        self.marcadores_no_mapa.clear()

        termo = self.entry_busca.get().strip().lower()
        filtro_cidade = self.combo_cidade.get()

        postos_filtrados = []
        for p in self.dados_postos:
            if filtro_cidade in ("Belém", "Ananindeua") and p["cidade"] != filtro_cidade:
                continue

            if self.categoria_ativa == "Carga rápida" and not p.get("carga_rapida"):
                continue
            elif self.categoria_ativa == "Público" and p.get("acesso") != "Público":
                continue
            elif self.categoria_ativa == "Restrito" and p.get("acesso") != "Uso restrito":
                continue
            elif self.categoria_ativa == "Manutenção" and p.get("status") not in ("Manutenção", "Ocupado"):
                continue

            if termo:
                alvo = f"{p['nome']} {p['endereco']} {p['bairro']} {p['tipo_conector']} {p['operadora']}".lower()
                if termo not in alvo:
                    continue

            postos_filtrados.append(p)

        self.lbl_contador.configure(text=f"{len(postos_filtrados)} de 39 mapeados")

        for posto in postos_filtrados:
            # IMPORTANTE: text=None remove totalmente os nomes dos postos no mapa,
            # exibindo apenas o ícone limpo de localização (modelo Carregados.com.br)
            icone_pino = self._obter_icone_pino(posto, selecionado=(posto == self.posto_selecionado))
            marcador = self.map_widget.set_marker(
                posto["lat"],
                posto["lon"],
                text=None,
                icon=icone_pino,
                icon_anchor="s",
                command=lambda m, p=posto: self.focar_no_posto(p),
            )
            self.marcadores_no_mapa.append(marcador)

            # Card na lista lateral seguindo exatamente o modelo Carregados.com.br:
            # [Ver no mapa] | Nome do Posto / Endereço / Badges (Público, Carga rápida) / N estações + kW
            card = ctk.CTkFrame(
                self.scroll_cards,
                fg_color=COR_CARD,
                border_width=1,
                border_color=COR_BORDA,
                corner_radius=12,
            )
            card.pack(fill="x", pady=5, padx=2)

            # Linha 1: Nome da estação + botão "Ver no mapa"
            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=12, pady=(10, 2))

            ctk.CTkLabel(
                topo,
                text=posto["nome"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COR_TEXTO,
            ).pack(side="left")

            ctk.CTkButton(
                topo,
                text="Ver no mapa",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#182436",
                hover_color=COR_CARD_HOVER,
                text_color=COR_TEXTO,
                border_width=1,
                border_color=COR_BORDA,
                corner_radius=14,
                height=24,
                width=92,
                command=lambda p=posto: self.focar_no_posto(p),
            ).pack(side="right")

            # Linha 2: Endereço completo
            ctk.CTkLabel(
                card,
                text=posto["endereco"],
                font=ctk.CTkFont(size=11),
                text_color=COR_TEXTO_MUTED,
                 anchor="w",
                justify="left",
            ).pack(fill="x", padx=12, pady=(0, 8))

            # Linha 3: Badges (Público / Uso restrito / Carga rápida) + Métricas (N estações | kW)
            rodape_card = ctk.CTkFrame(card, fg_color="transparent")
            rodape_card.pack(fill="x", padx=12, pady=(0, 10))

            # Badge de acesso (Público / Uso restrito / Manutenção)
            if posto.get("status") in ("Manutenção", "Ocupado"):
                cor_txt_acesso = COR_MANUTENCAO
                cor_bg_acesso = "#2D1418"
                texto_acesso = posto["status"]
            elif posto.get("acesso") == "Uso restrito":
                cor_txt_acesso = COR_RESTRITO
                cor_bg_acesso = "#2D1622"
                texto_acesso = "Uso restrito"
            else:
                cor_txt_acesso = COR_PUBLICO
                cor_bg_acesso = "#11281E"
                texto_acesso = "Público"

            ctk.CTkLabel(
                rodape_card,
                text=f"  {texto_acesso}  ",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=cor_bg_acesso,
                text_color=cor_txt_acesso,
                corner_radius=6,
            ).pack(side="left", padx=(0, 6))

            # Badge "Carga rápida" (quando aplicável)
            if posto.get("carga_rapida"):
                ctk.CTkLabel(
                    rodape_card,
                    text="  ⚡ Carga rápida  ",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    fg_color="#12243E",
                    text_color=COR_CARGA_RAPIDA,
                    corner_radius=6,
                ).pack(side="left", padx=(0, 6))

            # Métricas à direita: "6 estações  •  34.1 kW" (idêntico ao modelo Carregados.com.br)
            qtd_est = posto.get("qtd_estacoes", 1)
            plural = "estações" if qtd_est > 1 else "estação"
            metricas_txt = f"{qtd_est} {plural}   •   {posto['potencia_kw']:g} kW"

            ctk.CTkLabel(
                rodape_card,
                text=metricas_txt,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COR_TEXTO,
            ).pack(side="right")


if __name__ == "__main__":
    janela = ctk.CTk()
    janela.title("Estações de Carregamento e Eletropostos: Belém - Pará (PA)")
    janela.geometry("1180x740")
    janela.minsize(980, 640)

    def voltar_menu():
        try:
            from menu import Menu
            database.inicializar_banco()
            Menu(janela)
        except Exception:
            janela.destroy()

    EletroBelApp(janela, voltar_menu)
    janela.mainloop()
