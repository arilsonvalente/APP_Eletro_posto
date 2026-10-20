import customtkinter as ctk
from tkinter import messagebox
import database

# Configuração global de aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Paleta de Cores baseada na identidade visual da marca
COLOR_BG = "#0A0E14"
COLOR_CARD_BG = "#131922"
COLOR_CARD_BORDER = "#1F2B37"
COLOR_ACCENT = "#00E676"        # Verde neon elétrico
COLOR_ACCENT_HOVER = "#00C853"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_MUTED = "#8A99AD"


def Menu(janela, abrir_login=None, abrir_cadastro=None, abrir_perfil=None, usuario_atual=None, fazer_logout=None, abrir_mapa=None):
    """
    Renderiza a interface inicial do EletroBel integrada com navegação
    para telas de login, cadastro, área do cliente (perfil), mapa e consulta ao banco de dados.
    """
    # Limpa componentes anteriores da janela
    for widget in janela.winfo_children():
        widget.destroy()

    # Janela principal
    janela.title("EletroBel - Conectando o Futuro Elétrico")
    janela.geometry("1100x720")
    janela.minsize(980, 640)
    janela.configure(fg_color=COLOR_BG)

    # Handlers padrão caso executado isoladamente
    def nav_login():
        if abrir_login:
            abrir_login()
        else:
            try:
                from login import LoginApp
                LoginApp(janela, nav_cadastro, lambda: Menu(janela, nav_login, nav_cadastro, nav_perfil, usuario_atual, nav_logout, nav_mapa), lambda u: Menu(janela, nav_login, nav_cadastro, nav_perfil, u, nav_logout, nav_mapa))
            except Exception as e:
                messagebox.showinfo("Navegação", f"Tela de Login solicitada. ({e})")

    def nav_cadastro():
        if abrir_cadastro:
            abrir_cadastro()
        else:
            try:
                from cadastro_usuario import cadastrar
                cadastrar(janela, nav_login)
            except Exception as e:
                messagebox.showinfo("Navegação", f"Tela de Cadastro solicitada. ({e})")

    def nav_perfil():
        if abrir_perfil:
            abrir_perfil()
        else:
            if usuario_atual:
                try:
                    from perfil_usuario import PerfilUsuario
                    PerfilUsuario(janela, usuario_atual, lambda: Menu(janela, nav_login, nav_cadastro, nav_perfil, usuario_atual, nav_logout, nav_mapa), nav_logout)
                except Exception as e:
                    messagebox.showinfo("Navegação", f"Perfil solicitado. ({e})")
            else:
                nav_login()

    def nav_logout():
        if fazer_logout:
            fazer_logout()
        else:
            Menu(janela, nav_login, nav_cadastro, nav_perfil, None, None, nav_mapa)

    def nav_mapa():
        if abrir_mapa:
            abrir_mapa()
        else:
            try:
                from mapa_eletroposto import EletroBelApp as MapaEletroposto
                MapaEletroposto(
                    janela,
                    lambda: Menu(janela, nav_login, nav_cadastro, nav_perfil, usuario_atual, nav_logout, nav_mapa)
                )
            except Exception as e:
                messagebox.showinfo("Navegação", f"Mapa de Eletropostos solicitado. ({e})")

    # Container com rolagem para adaptação a diferentes tamanhos de tela
    scroll_container = ctk.CTkScrollableFrame(
        janela,
        fg_color="transparent",
        scrollbar_button_color="#1F2D3D",
        scrollbar_button_hover_color=COLOR_ACCENT
    )
    scroll_container.pack(fill="both", expand=True, padx=40, pady=25)

    # ==========================================
    # NAVBAR (CABEÇALHO)
    # ==========================================
    nav_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
    nav_frame.pack(fill="x", pady=(0, 25))

    # Logo / Marca
    logo_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
    logo_container.pack(side="left")

    logo_icon = ctk.CTkLabel(
        logo_container,
        text="⚡",
        font=ctk.CTkFont(size=26, weight="bold"),
        text_color=COLOR_ACCENT
    )
    logo_icon.pack(side="left", padx=(0, 6))

    logo_label = ctk.CTkLabel(
        logo_container,
        text="EletroBel",
        font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    )
    logo_label.pack(side="left")

    # Links de navegação e botões de ação
    actions_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
    actions_frame.pack(side="right")

    # Link Início
    btn_inicio = ctk.CTkButton(
        actions_frame,
        text="Início",
        fg_color="transparent",
        hover_color="#182330",
        text_color=COLOR_ACCENT,
        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        width=70,
        height=32,
        command=lambda: scroll_container.yview_moveto(0)
    )
    btn_inicio.pack(side="left", padx=4)

    # Link Mapa de Eletropostos
    btn_mapa = ctk.CTkButton(
        actions_frame,
        text="Mapa de Eletropostos",
        fg_color="transparent",
        hover_color="#182330",
        text_color=COLOR_TEXT_MUTED,
        font=ctk.CTkFont(family="Segoe UI", size=13),
        width=140,
        height=32,
        command=nav_mapa
    )
    btn_mapa.pack(side="left", padx=4)

    # Link Carros Elétricos
    btn_carros = ctk.CTkButton(
        actions_frame,
        text="Carros Elétricos",
        fg_color="transparent",
        hover_color="#182330",
        text_color=COLOR_TEXT_MUTED,
        font=ctk.CTkFont(family="Segoe UI", size=13),
        width=110,
        height=32,
        command=lambda: abrir_modal_mundo_eletrico(janela)
    )
    btn_carros.pack(side="left", padx=4)

    # Link Área do Cliente
    btn_area = ctk.CTkButton(
        actions_frame,
        text="Área do Cliente",
        fg_color="transparent",
        hover_color="#182330",
        text_color=COLOR_TEXT_MUTED,
        font=ctk.CTkFont(family="Segoe UI", size=13),
        width=120,
        height=32,
        command=nav_perfil
    )
    btn_area.pack(side="left", padx=4)

    if usuario_atual:
        primeiro_nome = usuario_atual.get("nome", "Usuário").split()[0]
        btn_perfil = ctk.CTkButton(
            actions_frame,
            text=f"👤 {primeiro_nome}",
            fg_color="#182A22",
            hover_color="#203D2F",
            border_color=COLOR_ACCENT,
            border_width=1.5,
            text_color=COLOR_ACCENT,
            corner_radius=20,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=34,
            command=nav_perfil
        )
        btn_perfil.pack(side="left", padx=(10, 6))

        btn_sair = ctk.CTkButton(
            actions_frame,
            text="Sair",
            fg_color="transparent",
            hover_color="#331A1D",
            text_color="#FF6B6B",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=50,
            height=34,
            command=nav_logout
        )
        btn_sair.pack(side="left")
    else:
        # Botão Cadastre-se
        btn_cadastro = ctk.CTkButton(
            actions_frame,
            text="Cadastre-se",
            fg_color="transparent",
            border_color=COLOR_ACCENT,
            border_width=1.5,
            hover_color="#113322",
            text_color=COLOR_ACCENT,
            corner_radius=20,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=115,
            height=34,
            command=nav_cadastro
        )
        btn_cadastro.pack(side="left", padx=(10, 6))

        # Botão Entrar
        btn_entrar = ctk.CTkButton(
            actions_frame,
            text="Entrar",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=20,
            width=80,
            height=34,
            command=nav_login
        )
        btn_entrar.pack(side="left")


    # ==========================================
    # HERO SECTION
    # ==========================================
    hero_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
    hero_frame.pack(fill="x", pady=(10, 20))

    title_box = ctk.CTkFrame(hero_frame, fg_color="transparent")
    title_box.pack(anchor="w")

    ctk.CTkLabel(
        title_box,
        text="Encontre e ",
        font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    ).pack(side="left")

    ctk.CTkLabel(
        title_box,
        text="Conecte",
        font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
        text_color=COLOR_ACCENT
    ).pack(side="left")

    subtitle_lbl = ctk.CTkLabel(
        hero_frame,
        text="Encontre eletropostos rápidos e acompanhe tudo sobre\ncarros elétricos em uma única plataforma integrada.",
        font=ctk.CTkFont(family="Segoe UI", size=14),
        text_color=COLOR_TEXT_MUTED,
        justify="left"
    )
    subtitle_lbl.pack(anchor="w", pady=(8, 0))

    # ==========================================
    # BARRA DE BUSCA
    # ==========================================
    search_card = ctk.CTkFrame(
        scroll_container,
        fg_color=COLOR_CARD_BG,
        border_color=COLOR_CARD_BORDER,
        border_width=1.5,
        corner_radius=30,
        height=68
    )
    search_card.pack(fill="x", pady=(15, 25), ipady=5)
    search_card.pack_propagate(False)

    inner_box = ctk.CTkFrame(search_card, fg_color="transparent")
    inner_box.pack(fill="both", expand=True, padx=15, pady=8)

    loc_icon = ctk.CTkLabel(inner_box, text="📍", font=ctk.CTkFont(size=18))
    loc_icon.pack(side="left", padx=(5, 5))

    cidade_var = ctk.StringVar(value="Belém, PA")
    cidade_menu = ctk.CTkOptionMenu(
        inner_box,
        values=["Belém, PA", "Ananindeua, PA", "Região Metropolitana (Belém / Ananindeua)"],
        variable=cidade_var,
        fg_color="#18222F",
        button_color="#1F2D3D",
        button_hover_color=COLOR_ACCENT,
        dropdown_fg_color="#18222F",
        dropdown_hover_color="#243447",
        dropdown_text_color="#FFFFFF",
        font=ctk.CTkFont(family="Segoe UI", size=13),
        corner_radius=15,
        width=270,
        height=40
    )
    cidade_menu.pack(side="left", padx=(0, 15))

    fast_charge_var = ctk.BooleanVar(value=True)
    chk_fast = ctk.CTkCheckBox(
        inner_box,
        text="Carga Rápida (DC ≥ 50kW)",
        variable=fast_charge_var,
        checkmark_color="#000000",
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        text_color=COLOR_TEXT_MAIN,
        font=ctk.CTkFont(family="Segoe UI", size=13)
    )
    chk_fast.pack(side="left", padx=10)

    btn_buscar = ctk.CTkButton(
        inner_box,
        text="Buscar Eletropostos",
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        text_color="#000000",
        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        corner_radius=20,
        height=40,
        width=190,
        command=lambda: executar_busca()
    )
    btn_buscar.pack(side="right", padx=(10, 5))

    # ==========================================
    # SEÇÃO DINÂMICA DE RESULTADOS DOS ELETROPOSTOS
    # ==========================================
    results_section = ctk.CTkFrame(scroll_container, fg_color="transparent")
    results_section.pack(fill="x", pady=(0, 30))

    results_header = ctk.CTkFrame(results_section, fg_color="transparent")
    results_header.pack(fill="x", pady=(0, 10))

    lbl_status_busca = ctk.CTkLabel(
        results_header,
        text="⚡ Postos de Recarga Próximos",
        font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    )
    lbl_status_busca.pack(side="left")

    stations_list_frame = ctk.CTkFrame(results_section, fg_color="transparent")
    stations_list_frame.pack(fill="x")

    def executar_busca():
        """Busca estações diretamente no SQLite e atualiza os cards dinamicamente."""
        cidade = cidade_var.get()
        apenas_rapida = fast_charge_var.get()

        for widget in stations_list_frame.winfo_children():
            widget.destroy()

        estacoes = database.buscar_estacoes(cidade=cidade, apenas_rapida=apenas_rapida)
        lbl_status_busca.configure(
            text=f"⚡ Eletropostos em {cidade.split(',')[0]} ({len(estacoes)} encontrados)"
        )

        if not estacoes:
            sem_resultados = ctk.CTkFrame(
                stations_list_frame,
                fg_color=COLOR_CARD_BG,
                border_color=COLOR_CARD_BORDER,
                border_width=1,
                corner_radius=12
            )
            sem_resultados.pack(fill="x", pady=10, ipady=15)
            ctk.CTkLabel(
                sem_resultados,
                text="Nenhum eletroposto encontrado para os filtros selecionados.",
                font=ctk.CTkFont(size=14),
                text_color=COLOR_TEXT_MUTED
            ).pack()
            return

        # Renderiza até 6 cards em grid responsivo (2 colunas)
        stations_list_frame.grid_columnconfigure((0, 1), weight=1, uniform="station")

        for idx, estacao in enumerate(estacoes):
            row = idx // 2
            col = idx % 2

            card_estacao = ctk.CTkFrame(
                stations_list_frame,
                fg_color=COLOR_CARD_BG,
                border_color=COLOR_CARD_BORDER,
                border_width=1.5,
                corner_radius=16
            )
            card_estacao.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            content = ctk.CTkFrame(card_estacao, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=16, pady=16)

            # Cabeçalho do Card
            card_top = ctk.CTkFrame(content, fg_color="transparent")
            card_top.pack(fill="x")

            ctk.CTkLabel(
                card_top,
                text=estacao["nome"],
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=COLOR_TEXT_MAIN
            ).pack(side="left")

            status_color = COLOR_ACCENT if estacao["status"] == "Disponível" else "#FFA726"
            status_badge = ctk.CTkLabel(
                card_top,
                text=f"● {estacao['status']}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=status_color
            )
            status_badge.pack(side="right")

            # Endereço
            ctk.CTkLabel(
                content,
                text=f"📍 {estacao['endereco']}",
                font=ctk.CTkFont(size=12),
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
                wraplength=380
            ).pack(fill="x", pady=(4, 8))

            # Detalhes técnicos
            info_bar = ctk.CTkFrame(content, fg_color="transparent")
            info_bar.pack(fill="x", pady=(2, 10))

            tipo_carga = "DC Rápida" if estacao["potencia_kw"] >= 50 else "AC Normal"
            ctk.CTkLabel(
                info_bar,
                text=f"⚡ {estacao['potencia_kw']:.0f} kW ({tipo_carga})",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLOR_ACCENT
            ).pack(side="left", padx=(0, 15))

            ctk.CTkLabel(
                info_bar,
                text=f"🔌 {estacao['tipo_conector']}",
                font=ctk.CTkFont(size=12),
                text_color=COLOR_TEXT_MUTED
            ).pack(side="left", padx=(0, 15))

            ctk.CTkLabel(
                info_bar,
                text=f"💰 R$ {estacao['preco_kwh']:.2f}/kWh",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLOR_TEXT_MAIN
            ).pack(side="right")

            # Botão de Ação
            btn_acao_estacao = ctk.CTkButton(
                content,
                text="Iniciar Recarga",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#182A22",
                hover_color="#1F3D30",
                text_color=COLOR_ACCENT,
                border_width=1,
                border_color=COLOR_ACCENT,
                corner_radius=10,
                height=32,
                command=lambda e=estacao: acao_iniciar_recarga(e, nav_login)
            )
            btn_acao_estacao.pack(fill="x")

    def acao_iniciar_recarga(estacao, callback_login):
        resp = messagebox.askyesno(
            "EletroBel Recarga",
            f"Deseja iniciar a recarga na '{estacao['nome']}'?\n"
            f"Potência: {estacao['potencia_kw']} kW\n"
            f"Tarifa: R$ {estacao['preco_kwh']:.2f}/kWh\n\n"
            "Deseja acessar sua conta para autorizar e registrar a recarga?"
        )
        if resp:
            callback_login()

    # Preenche a listagem inicial de eletropostos
    executar_busca()

    # ==========================================
    # CARDS DE FUNCIONALIDADES
    # ==========================================
    cards_container = ctk.CTkFrame(scroll_container, fg_color="transparent")
    cards_container.pack(fill="x", pady=(10, 20))
    cards_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

    cards_info = [
        {
            "col": 0,
            "icone": "⚡",
            "titulo": "Encontrar Eletropostos",
            "desc": "Mapeamento em tempo real de pontos de recarga disponíveis em Belém e Ananindeua.",
            "destaque": True,
            "acao": nav_mapa
        },
        {
            "col": 1,
            "icone": "🗺️",
            "titulo": "Calculadora de Viagem",
            "desc": "Planeje suas paradas e estime com precisão o tempo de carga ideal para o seu trajeto.",
            "destaque": False,
            "acao": lambda: abrir_modal_calculadora(janela)
        },
        {
            "col": 2,
            "icone": "🚗",
            "titulo": "Mundo Elétrico",
            "desc": "Notícias, especificações, novidades e tendências sobre o universo de veículos elétricos.",
            "destaque": False,
            "acao": lambda: abrir_modal_mundo_eletrico(janela)
        }
    ]

    for item in cards_info:
        border_c = COLOR_ACCENT if item["destaque"] else COLOR_CARD_BORDER
        card = ctk.CTkFrame(
            cards_container,
            fg_color=COLOR_CARD_BG,
            border_color=border_c,
            border_width=1.5,
            corner_radius=18
        )
        card.grid(row=0, column=item["col"], padx=10, pady=5, sticky="nsew")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=22)

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", anchor="w")

        ctk.CTkLabel(header, text=item["icone"], font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            header,
            text=item["titulo"],
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        ).pack(side="left")

        ctk.CTkLabel(
            content,
            text=item["desc"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
            wraplength=250
        ).pack(anchor="w", pady=(14, 15))

        ctk.CTkButton(
            content,
            text="Acessar",
            fg_color="#18222F",
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_TEXT_MAIN,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10,
            height=32,
            command=item["acao"]
        ).pack(fill="x")


# =====================================================================
# MODAIS INTERATIVOS (CALCULADORA E MUNDO ELÉTRICO)
# =====================================================================

def abrir_modal_calculadora(parent):
    """Abre janela de cálculo de tempo e custo de recarga de veículo elétrico."""
    modal = ctk.CTkToplevel(parent)
    modal.title("⚡ Calculadora de Recarga & Viagem - EletroBel")
    modal.geometry("480x560")
    modal.minsize(440, 520)
    modal.configure(fg_color=COLOR_BG)
    modal.attributes("-topmost", True)

    frame = ctk.CTkFrame(modal, fg_color=COLOR_CARD_BG, corner_radius=16, border_width=1, border_color=COLOR_CARD_BORDER)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        frame,
        text="⚡ Calculadora de Recarga",
        font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
        text_color=COLOR_ACCENT
    ).pack(pady=(15, 4))

    ctk.CTkLabel(
        frame,
        text="Estime o tempo e custo da recarga do seu carro elétrico",
        font=ctk.CTkFont(size=12),
        text_color=COLOR_TEXT_MUTED
    ).pack(pady=(0, 15))

    # Bateria (kWh)
    ctk.CTkLabel(frame, text="Capacidade da Bateria (kWh):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w").pack(fill="x", padx=30, pady=(4, 2))
    ent_bateria = ctk.CTkEntry(frame, width=380, height=38, fg_color="#182229", border_color="#253440", text_color="#FFFFFF")
    ent_bateria.insert(0, "50")
    ent_bateria.pack(padx=30, pady=(0, 8))

    # Carga Atual (%)
    ctk.CTkLabel(frame, text="Carga Atual (%):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w").pack(fill="x", padx=30, pady=(4, 2))
    ent_atual = ctk.CTkEntry(frame, width=380, height=38, fg_color="#182229", border_color="#253440", text_color="#FFFFFF")
    ent_atual.insert(0, "20")
    ent_atual.pack(padx=30, pady=(0, 8))

    # Carga Desejada (%)
    ctk.CTkLabel(frame, text="Carga Desejada (%):", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w").pack(fill="x", padx=30, pady=(4, 2))
    ent_alvo = ctk.CTkEntry(frame, width=380, height=38, fg_color="#182229", border_color="#253440", text_color="#FFFFFF")
    ent_alvo.insert(0, "80")
    ent_alvo.pack(padx=30, pady=(0, 15))

    resultado_lbl = ctk.CTkLabel(
        frame,
        text="Clique em Calcular para ver o resultado",
        font=ctk.CTkFont(size=13),
        text_color=COLOR_TEXT_MUTED,
        justify="center"
    )
    resultado_lbl.pack(pady=10)

    def calcular():
        try:
            bateria = float(ent_bateria.get())
            atual = float(ent_atual.get())
            alvo = float(ent_alvo.get())

            if not (0 <= atual < alvo <= 100):
                messagebox.showerror("Validação", "A carga atual deve ser menor que a desejada (entre 0% e 100%).")
                return

            kwh_necessario = ((alvo - atual) / 100.0) * bateria
            custo_medio = kwh_necessario * 1.95  # Tarifa média em Belém
            tempo_rapido_min = (kwh_necessario / 60.0) * 60.0  # Carregador rápido 60kW
            tempo_ultra_min = (kwh_necessario / 150.0) * 60.0  # Ultra rápido 150kW
            autonomia_km = kwh_necessario * 6.2  # Média de 6.2 km/kWh

            resultado_lbl.configure(
                text=(
                    f"Energia necessária: {kwh_necessario:.1f} kWh\n"
                    f"Custo estimado: R$ {custo_medio:.2f}\n"
                    f"Tempo estimado (60 kW DC): ~{tempo_rapido_min:.0f} min\n"
                    f"Tempo estimado (150 kW Ultra DC): ~{tempo_ultra_min:.0f} min\n"
                    f"Autonomia estimada ganha: +{autonomia_km:.0f} km"
                ),
                text_color=COLOR_ACCENT
            )
        except ValueError:
            messagebox.showerror("Erro", "Por favor, digite valores numéricos válidos.")

    ctk.CTkButton(
        frame,
        text="Calcular Estimativa",
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        text_color="#000000",
        height=40,
        corner_radius=10,
        command=calcular
    ).pack(padx=30, pady=(5, 15), fill="x")


def abrir_modal_mundo_eletrico(parent):
    """Abre modal informativo sobre o universo dos carros elétricos."""
    modal = ctk.CTkToplevel(parent)
    modal.title("🚗 Mundo Elétrico - EletroBel")
    modal.geometry("520x580")
    modal.minsize(480, 520)
    modal.configure(fg_color=COLOR_BG)
    modal.attributes("-topmost", True)

    frame = ctk.CTkFrame(modal, fg_color=COLOR_CARD_BG, corner_radius=16, border_width=1, border_color=COLOR_CARD_BORDER)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        frame,
        text="🚗 Guia de Mobilidade Elétrica",
        font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
        text_color=COLOR_ACCENT
    ).pack(pady=(15, 10))

    dicas = [
        ("🔌 Padrões de Conectores no Brasil", "O conector CCS2 é o padrão dominante de carga rápida DC. Para carregamento residencial (wallbox), utiliza-se o padrão Tipo 2."),
        ("🔋 Regra dos 20% aos 80%", "Para máxima vida útil da bateria de íons de lítio, recomenda-se manter a carga entre 20% e 80% no uso diário."),
        ("💰 Economia Operacional", "O custo por quilômetro rodado em um veículo elétrico é até 70% menor em comparação a carros a combustão em Belém e Ananindeua."),
        ("🌱 Sustentabilidade", "Zero emissão de poluentes locais e integração com energia limpa solar e renovável.")
    ]

    for titulo, desc in dicas:
        item_frame = ctk.CTkFrame(frame, fg_color="#182229", corner_radius=10)
        item_frame.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(item_frame, text=titulo, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w").pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(item_frame, text=desc, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MUTED, justify="left", wraplength=440).pack(fill="x", padx=12, pady=(0, 8))

    ctk.CTkButton(
        frame,
        text="Fechar",
        fg_color="#1F2D3D",
        hover_color="#27394D",
        text_color="#FFFFFF",
        height=36,
        corner_radius=10,
        command=modal.destroy
    ).pack(padx=20, pady=(15, 10), fill="x")


# =====================================================================
# CLASSE DE COMPATIBILIDADE E EXECUÇÃO DIRETA
# =====================================================================

class EletroBelApp(ctk.CTk):
    """Classe CTk compatível para inicialização direta do menu."""
    def __init__(self, abrir_login=None, abrir_cadastro=None, abrir_perfil=None, usuario_atual=None, fazer_logout=None, abrir_mapa=None):
        super().__init__()
        database.inicializar_banco()
        Menu(self, abrir_login, abrir_cadastro, abrir_perfil, usuario_atual, fazer_logout, abrir_mapa)


if __name__ == "__main__":
    app = EletroBelApp()
    app.mainloop()