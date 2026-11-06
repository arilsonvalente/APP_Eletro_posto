import webbrowser
import urllib.parse
import customtkinter as ctk
from tkintermapview import TkinterMapView
import database

# Paleta de cores EletroBel (inspirada no portal Carregados.com.br)
COR_FUNDO = "#0B131B"
COR_PAINEL = "#0E1721"
COR_CARD = "#141F2B"
COR_CARD_HOVER = "#1A2938"
COR_BORDA = "#1E2D3D"
COR_VERDE = "#00E676"
COR_VERDE_HOVER = "#00C853"
COR_AZUL = "#38BDF8"
COR_OCUPADO = "#FFA500"
COR_MANUTENCAO = "#FF5252"
COR_TEXTO_MUTED = "#8B9DAE"
COR_BADGE_BG = "#192838"

# Metadados geográficos e operacionais (baseados em Carregados.com.br - Belém/Ananindeua - PA)
METADADOS_ESTACOES_PA = {
    "Estação EletroBel Doca": {
        "cidade": "Belém",
        "bairro": "Reduto / Umarizal",
        "operadora": "EletroBel / Boulevard",
        "horario": "24 horas",
        "acesso": "Público • Estacionamento",
        "lat": -1.4453,
        "lon": -48.4892,
    },
    "Estação Shopping Bosque Grão-Pará": {
        "cidade": "Belém",
        "bairro": "Val-de-Cans",
        "operadora": "EletroBel / Tupinambá",
        "horario": "10h às 22h",
        "acesso": "Shopping • Subsolo G1",
        "lat": -1.3916,
        "lon": -48.4485,
    },
    "Estação Metrópole Ananindeua": {
        "cidade": "Ananindeua",
        "bairro": "Coqueiro",
        "operadora": "EletroBel / WeCharge",
        "horario": "10h às 22h",
        "acesso": "Shopping • Estacionamento VIP",
        "lat": -1.3655,
        "lon": -48.3748,
    },
    "Estação Cidade Nova": {
        "cidade": "Ananindeua",
        "bairro": "Cidade Nova",
        "operadora": "EletroBel",
        "horario": "06h às 23h",
        "acesso": "Público • Conveniência",
        "lat": -1.3512,
        "lon": -48.4035,
    },
    "Estação Aeroporto Internacional": {
        "cidade": "Belém",
        "bairro": "Val-de-Cans",
        "operadora": "EletroBel / Infraero",
        "horario": "24 horas",
        "acesso": "Aeroporto • Estacionamento VIP",
        "lat": -1.3847,
        "lon": -48.4764,
    },
    "Estação BRT Augusto Montenegro": {
        "cidade": "Belém",
        "bairro": "Parque Verde",
        "operadora": "EletroBel / Parque Shopping",
        "horario": "24 horas",
        "acesso": "Corredor BRT • Carga Rápida",
        "lat": -1.3620,
        "lon": -48.4490,
    },
}

# Estações complementares de referência em Belém - PA (Carregados.com.br)
ESTACOES_COMPLEMENTARES_BELEM = [
    {
        "id": 101,
        "nome": "Eletroposto Pátio Belém",
        "cidade": "Belém",
        "bairro": "Batista Campos",
        "endereco": "Tv. Padre Eutíquio, 1078 - Batista Campos, Belém, PA",
        "potencia_kw": 22.0,
        "tipo_conector": "Tipo 2",
        "preco_kwh": 1.65,
        "status": "Disponível",
        "operadora": "EletroBel / Volvo Recharge",
        "horario": "10h às 22h",
        "acesso": "Shopping • Garagem G2",
        "lat": -1.4583,
        "lon": -48.4952,
    },
    {
        "id": 102,
        "nome": "Eletroposto Estação das Docas",
        "cidade": "Belém",
        "bairro": "Campina",
        "endereco": "Av. Boulevard Castilhos França, s/n - Campina, Belém, PA",
        "potencia_kw": 60.0,
        "tipo_conector": "CCS2 / Tipo 2",
        "preco_kwh": 2.05,
        "status": "Disponível",
        "operadora": "EletroBel / Equatorial PA",
        "horario": "09h às 00h",
        "acesso": "Turístico • Estacionamento Externo",
        "lat": -1.4488,
        "lon": -48.5004,
    },
]


def carregar_postos_mysql():
    """
    Carrega as estações diretamente do banco de dados MySQL (`database.listar_estacoes()`)
    e mescla com as coordenadas e metadados de Belém/Ananindeua - PA.
    """
    postos = []
    nomes_cadastrados = set()

    try:
        registros_mysql = database.listar_estacoes()
    except Exception:
        registros_mysql = []

    for idx, reg in enumerate(registros_mysql):
        nome = reg.get("nome", "Estação EletroBel")
        nomes_cadastrados.add(nome)
        endereco = reg.get("endereco", "Belém, PA")
        pot_kw = float(reg.get("potencia_kw") or 50.0)
        conector = reg.get("tipo_conector", "CCS2 / Tipo 2")
        preco_kwh = float(reg.get("preco_kwh") or 1.95)
        status = reg.get("status", "Disponível")

        meta = METADADOS_ESTACOES_PA.get(nome, {})
        cidade = meta.get("cidade") or ("Ananindeua" if "ananindeua" in endereco.lower() else "Belém")
        bairro = meta.get("bairro", "Centro")
        operadora = meta.get("operadora", "Rede EletroBel")
        horario = meta.get("horario", "24 horas")
        acesso = meta.get("acesso", "Público")
        lat = meta.get("lat", -1.4300 + (idx * 0.011))
        lon = meta.get("lon", -48.4600 + (idx * 0.011))

        tipo_carga = "DC Ultra Rápida" if pot_kw >= 100 else ("DC Rápida" if pot_kw >= 50 else "AC Semirrápida")
        postos.append({
            "id": reg.get("id", idx + 1),
            "nome": nome,
            "cidade": cidade,
            "bairro": bairro,
            "endereco": endereco,
            "potencia_kw": pot_kw,
            "potencia": f"{int(pot_kw) if pot_kw.is_integer() else pot_kw} kW ({tipo_carga})",
            "conector": conector,
            "preco_kwh": preco_kwh,
            "preco": f"R$ {preco_kwh:.2f}/kWh",
            "status": status,
            "operadora": operadora,
            "horario": horario,
            "acesso": acesso,
            "lat": lat,
            "lon": lon,
        })

    for extra in ESTACOES_COMPLEMENTARES_BELEM:
        if extra["nome"] not in nomes_cadastrados:
            pot_kw = float(extra["potencia_kw"])
            tipo_carga = "DC Rápida" if pot_kw >= 50 else "AC Semirrápida"
            postos.append({
                **extra,
                "potencia": f"{int(pot_kw)} kW ({tipo_carga})",
                "conector": extra["tipo_conector"],
                "preco": f"R$ {extra['preco_kwh']:.2f}/kWh",
            })

    return postos


class EletroBelApp(ctk.CTkFrame):
    def __init__(self, master, abrir_menu_callback):
        for widget in master.winfo_children():
            widget.destroy()

        super().__init__(master, fg_color=COR_FUNDO)
        self.pack(fill="both", expand=True)

        self.abrir_menu_callback = abrir_menu_callback
        self.marcadores_no_mapa = []
        self.dados_postos = carregar_postos_mysql()
        self.posto_selecionado = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.construir_painel_lateral()
        self.construir_mapa()
        self.atualizar_lista_e_marcadores()

    def voltar(self):
        self.destroy()
        self.abrir_menu_callback()

    def recarregar_do_banco(self):
        """Recarrega as estações atualizadas diretamente do MySQL."""
        self.dados_postos = carregar_postos_mysql()
        self.atualizar_lista_e_marcadores()

    def abrir_rota_google_maps(self, posto):
        destino = urllib.parse.quote(f"{posto['nome']}, {posto['endereco']}")
        url = f"https://www.google.com/maps/dir/?api=1&destination={posto['lat']},{posto['lon']}&query={destino}"
        webbrowser.open(url)

    def construir_painel_lateral(self):
        self.painel_lateral = ctk.CTkFrame(
            self,
            width=450,
            corner_radius=0,
            fg_color=COR_PAINEL,
        )
        self.painel_lateral.grid(row=0, column=0, sticky="nsew", padx=(14, 6), pady=14)
        self.painel_lateral.grid_propagate(False)

        # Topo: Botão voltar + Atualizar MySQL
        top_bar = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        top_bar.pack(fill="x", padx=12, pady=(8, 6))

        ctk.CTkButton(
            top_bar,
            text="← Voltar ao Menu",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            text_color=COR_VERDE,
            hover_color=COR_CARD,
            anchor="w",
            height=28,
            width=130,
            command=self.voltar,
        ).pack(side="left")

        ctk.CTkButton(
            top_bar,
            text="🔄 Sincronizar MySQL",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COR_BADGE_BG,
            text_color=COR_AZUL,
            hover_color=COR_CARD_HOVER,
            height=28,
            width=140,
            command=self.recarregar_do_banco,
        ).pack(side="right")

        # Cabeçalho inspirado em Carregados.com.br (Belém - Pará)
        frame_logo = ctk.CTkFrame(self.painel_lateral, fg_color="transparent")
        frame_logo.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            frame_logo,
            text="⚡ Estações de Carregamento • Belém & PA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame_logo,
            text="Conectado ao banco MySQL • Baseado em Carregados.com.br",
            font=ctk.CTkFont(size=11),
            text_color=COR_VERDE,
        ).pack(anchor="w")

        # Barra de busca por nome, bairro ou conector
        self.entry_busca = ctk.CTkEntry(
            self.painel_lateral,
            placeholder_text="🔍 Buscar por estação, bairro, endereço ou conector...",
            fg_color=COR_CARD,
            border_color=COR_BORDA,
            text_color="white",
            height=34,
        )
        self.entry_busca.pack(fill="x", padx=14, pady=(4, 8))
        self.entry_busca.bind("<KeyRelease>", lambda _: self.atualizar_lista_e_marcadores())

        # Filtros combinados: Cidade + Tipo de Conector + Apenas DC Rápida
        frame_filtros = ctk.CTkFrame(
            self.painel_lateral,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=8,
        )
        frame_filtros.pack(fill="x", padx=14, pady=(0, 10))

        linha1 = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        linha1.pack(fill="x", padx=8, pady=(8, 4))

        self.combo_cidade = ctk.CTkComboBox(
            linha1,
            values=["Todas as Cidades (PA)", "Belém", "Ananindeua"],
            command=lambda _: self.atualizar_lista_e_marcadores(),
            fg_color="#0D1620",
            button_color=COR_VERDE,
            button_hover_color=COR_VERDE_HOVER,
            border_color=COR_BORDA,
            dropdown_fg_color=COR_CARD,
            width=195,
            height=30,
        )
        self.combo_cidade.pack(side="left", padx=(0, 6), fill="x", expand=True)

        self.combo_conector = ctk.CTkComboBox(
            linha1,
            values=["Todos Conectores", "CCS2", "Tipo 2", "CHAdeMO"],
            command=lambda _: self.atualizar_lista_e_marcadores(),
            fg_color="#0D1620",
            button_color=COR_VERDE,
            button_hover_color=COR_VERDE_HOVER,
            border_color=COR_BORDA,
            dropdown_fg_color=COR_CARD,
            width=180,
            height=30,
        )
        self.combo_conector.pack(side="left", fill="x", expand=True)

        linha2 = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        linha2.pack(fill="x", padx=10, pady=(4, 8))

        self.var_dc_rapida = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            linha2,
            text="⚡ Carga Rápida (≥50kW)",
            variable=self.var_dc_rapida,
            command=self.atualizar_lista_e_marcadores,
            font=ctk.CTkFont(size=11),
            fg_color=COR_VERDE,
            hover_color=COR_VERDE_HOVER,
            checkbox_width=18,
            checkbox_height=18,
        ).pack(side="left")

        self.var_apenas_disponiveis = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            linha2,
            text="🟢 Apenas Disponíveis",
            variable=self.var_apenas_disponiveis,
            command=self.atualizar_lista_e_marcadores,
            font=ctk.CTkFont(size=11),
            fg_color=COR_VERDE,
            hover_color=COR_VERDE_HOVER,
            checkbox_width=18,
            checkbox_height=18,
        ).pack(side="right")

        # Resumo estatístico (KPIs estilo Carregados.com.br)
        self.lbl_contador = ctk.CTkLabel(
            self.painel_lateral,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
        )
        self.lbl_contador.pack(anchor="w", padx=14, pady=(0, 6))

        # Lista rolável de cards de estações
        self.scroll_cards = ctk.CTkScrollableFrame(
            self.painel_lateral,
            fg_color="transparent",
            corner_radius=8,
        )
        self.scroll_cards.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def construir_mapa(self):
        frame_direita = ctk.CTkFrame(
            self,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=12,
        )
        frame_direita.grid(row=0, column=1, sticky="nsew", padx=(6, 14), pady=14)
        frame_direita.grid_rowconfigure(1, weight=1)
        frame_direita.grid_columnconfigure(0, weight=1)

        # Barra superior do mapa (modo de visualização + centralizar)
        barra_mapa = ctk.CTkFrame(frame_direita, fg_color=COR_PAINEL, corner_radius=8, height=42)
        barra_mapa.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        ctk.CTkLabel(
            barra_mapa,
            text="🗺️ Mapa Interativo — Região Metropolitana de Belém (PA)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
        ).pack(side="left", padx=12, pady=6)

        ctk.CTkButton(
            barra_mapa,
            text="🎯 Visão Geral PA",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COR_BADGE_BG,
            hover_color=COR_CARD_HOVER,
            text_color=COR_VERDE,
            width=120,
            height=28,
            command=self.centralizar_visao,
        ).pack(side="right", padx=8, pady=6)

        self.combo_estilo_mapa = ctk.CTkComboBox(
            barra_mapa,
            values=["Google Mapa Padrão", "Google Satélite", "OpenStreetMap"],
            command=self.alterar_estilo_mapa,
            width=165,
            height=28,
            fg_color=COR_CARD,
            button_color=COR_VERDE,
            border_color=COR_BORDA,
        )
        self.combo_estilo_mapa.pack(side="right", padx=4, pady=6)

        self.map_widget = TkinterMapView(frame_direita, corner_radius=10)
        self.map_widget.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.map_widget.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=pt-BR&x={x}&y={y}&z={z}&s=Ga",
            max_zoom=22,
        )
        self.centralizar_visao()

    def alterar_estilo_mapa(self, estilo: str):
        if estilo == "Google Satélite":
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
        self.map_widget.set_position(-1.4100, -48.4450)
        self.map_widget.set_zoom(12)

    def focar_no_posto(self, posto):
        self.posto_selecionado = posto
        self.map_widget.set_position(posto["lat"], posto["lon"])
        self.map_widget.set_zoom(16)

    def atualizar_lista_e_marcadores(self):
        for widget in self.scroll_cards.winfo_children():
            widget.destroy()

        for marcador in self.marcadores_no_mapa:
            marcador.delete()
        self.marcadores_no_mapa.clear()

        termo = self.entry_busca.get().strip().lower()
        filtro_cidade = self.combo_cidade.get()
        filtro_conector = self.combo_conector.get()
        apenas_dc = self.var_dc_rapida.get()
        apenas_disp = self.var_apenas_disponiveis.get()

        postos_filtrados = []
        for p in self.dados_postos:
            if filtro_cidade not in ("Todas as Cidades (PA)", "Todas as Cidades") and p["cidade"] != filtro_cidade:
                continue
            if filtro_conector != "Todos Conectores" and filtro_conector.lower() not in p["conector"].lower():
                continue
            if apenas_dc and p["potencia_kw"] < 50.0:
                continue
            if apenas_disp and p["status"] != "Disponível":
                continue
            if termo:
                alvo = f"{p['nome']} {p['endereco']} {p['bairro']} {p['conector']} {p['operadora']}".lower()
                if termo not in alvo:
                    continue
            postos_filtrados.append(p)

        qtd_disp = sum(1 for p in postos_filtrados if p["status"] == "Disponível")
        self.lbl_contador.configure(
            text=f"⚡ {len(postos_filtrados)} eletropostos encontrados  |  🟢 {qtd_disp} disponíveis"
        )

        for posto in postos_filtrados:
            cor_pin = "#00C853" if posto["status"] == "Disponível" else "#FFA000"
            marcador = self.map_widget.set_marker(
                posto["lat"],
                posto["lon"],
                text=f"{posto['nome']} ({int(posto['potencia_kw'])}kW)",
                marker_color_outside=cor_pin,
                marker_color_circle="#0B131B",
                text_color="#FFFFFF",
                command=lambda m, p=posto: self.focar_no_posto(p),
            )
            self.marcadores_no_mapa.append(marcador)

            card = ctk.CTkFrame(
                self.scroll_cards,
                fg_color=COR_CARD,
                border_width=1,
                border_color=COR_BORDA,
                corner_radius=10,
            )
            card.pack(fill="x", pady=5, padx=2)

            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=12, pady=(10, 2))

            ctk.CTkLabel(
                topo,
                text=posto["nome"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white",
            ).pack(side="left")

            cor_status = (
                COR_VERDE
                if posto["status"] == "Disponível"
                else (COR_OCUPADO if posto["status"] == "Ocupado" else COR_MANUTENCAO)
            )
            ctk.CTkLabel(
                topo,
                text=f"● {posto['status']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=cor_status,
            ).pack(side="right")

            # Bairro + Operadora + Horário
            ctk.CTkLabel(
                card,
                text=f"🏙️ {posto['bairro']} ({posto['cidade']}/PA)  •  🕒 {posto['horario']}  •  🏢 {posto['operadora']}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COR_AZUL,
            ).pack(anchor="w", padx=12, pady=(0, 3))

            ctk.CTkLabel(
                card,
                text=f"📍 {posto['endereco']}",
                font=ctk.CTkFont(size=11),
                text_color=COR_TEXTO_MUTED,
            ).pack(anchor="w", padx=12, pady=(0, 6))

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=12, pady=(0, 8))

            ctk.CTkLabel(
                info_frame,
                text=f"⚡ {posto['potencia']}  |  🔌 {posto['conector']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COR_VERDE,
            ).pack(side="left")

            ctk.CTkLabel(
                info_frame,
                text=posto["preco"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white",
            ).pack(side="right")

            botoes_frame = ctk.CTkFrame(card, fg_color="transparent")
            botoes_frame.pack(fill="x", padx=12, pady=(0, 10))

            ctk.CTkButton(
                botoes_frame,
                text="🎯 Ver no Mapa",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="transparent",
                border_width=1,
                border_color=COR_VERDE,
                text_color=COR_VERDE,
                hover_color="#0F2B22",
                height=28,
                command=lambda p=posto: self.focar_no_posto(p),
            ).pack(side="left", fill="x", expand=True, padx=(0, 4))

            ctk.CTkButton(
                botoes_frame,
                text="🧭 Como Chegar (Maps)",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=COR_BADGE_BG,
                text_color="white",
                hover_color=COR_CARD_HOVER,
                height=28,
                command=lambda p=posto: self.abrir_rota_google_maps(p),
            ).pack(side="right", fill="x", expand=True, padx=(4, 0))


if __name__ == "__main__":
    janela = ctk.CTk()
    janela.title("EletroBel - Mapa de Eletropostos (Belém & Pará)")
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
