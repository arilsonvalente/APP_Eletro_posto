import customtkinter as ctk
from tkinter import messagebox
import database

# Paleta de cores EletroBel
COLOR_BG = "#0A0E14"
COLOR_CARD_BG = "#131922"
COLOR_CARD_BORDER = "#1F2B37"
COLOR_ACCENT = "#00E676"        # Verde neon elétrico
COLOR_ACCENT_HOVER = "#00C853"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_MUTED = "#8A99AD"
COLOR_INPUT_BG = "#182229"
COLOR_INPUT_BORDER = "#253440"


def PerfilUsuario(janela, usuario, abrir_menu, fazer_logout=None):
    """
    Renderiza a 'Pasta do Usuário' (Área do Cliente), apresentando todos os
    dados cadastrais, resumo de consumo, veículos cadastrados e histórico de recargas.
    """
    for widget in janela.winfo_children():
        widget.destroy()

    janela.title(f"EletroBel - Área do Cliente | {usuario.get('nome', 'Usuário')}")
    janela.geometry("1100x720")
    janela.minsize(980, 640)
    janela.configure(fg_color=COLOR_BG)

    # Função de logout padrão caso não seja fornecida
    def logout():
        if fazer_logout:
            fazer_logout()
        else:
            abrir_menu()

    # Container de rolagem principal
    scroll = ctk.CTkScrollableFrame(
        janela,
        fg_color="transparent",
        scrollbar_button_color="#1F2D3D",
        scrollbar_button_hover_color=COLOR_ACCENT
    )
    scroll.pack(fill="both", expand=True, padx=40, pady=25)

    # ==========================================
    # BARRA SUPERIOR / CABEÇALHO DA CONTA
    # ==========================================
    top_bar = ctk.CTkFrame(scroll, fg_color="transparent")
    top_bar.pack(fill="x", pady=(0, 20))

    # Logo e identificação
    brand_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
    brand_frame.pack(side="left")

    ctk.CTkLabel(
        brand_frame,
        text="⚡",
        font=ctk.CTkFont(size=26, weight="bold"),
        text_color=COLOR_ACCENT
    ).pack(side="left", padx=(0, 6))

    ctk.CTkLabel(
        brand_frame,
        text="EletroBel",
        font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    ).pack(side="left")

    ctk.CTkLabel(
        brand_frame,
        text=" | Área do Cliente",
        font=ctk.CTkFont(family="Segoe UI", size=16),
        text_color=COLOR_TEXT_MUTED
    ).pack(side="left")

    # Botões de navegação no topo
    actions_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
    actions_frame.pack(side="right")

    ctk.CTkButton(
        actions_frame,
        text="🏠 Início / Postos",
        font=ctk.CTkFont(family="Segoe UI", size=13),
        fg_color="#18222F",
        hover_color="#223244",
        text_color=COLOR_TEXT_MAIN,
        corner_radius=8,
        height=34,
        command=abrir_menu
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        actions_frame,
        text="🚪 Sair da Conta",
        font=ctk.CTkFont(family="Segoe UI", size=13),
        fg_color="transparent",
        hover_color="#331A1D",
        text_color="#FF6B6B",
        border_width=1,
        border_color="#552222",
        corner_radius=8,
        height=34,
        command=logout
    ).pack(side="left", padx=5)

    # Atualiza informações do usuário do banco
    usuario_id = usuario.get("id")
    dados_atualizados = database.obter_usuario_por_id(usuario_id) if usuario_id else usuario
    if not dados_atualizados:
        dados_atualizados = usuario

    resumo = database.obter_resumo_usuario(usuario_id) if usuario_id else {
        "total_recargas": 0, "total_kwh": 0.0, "total_valor": 0.0, "total_veiculos": 0
    }

    # ==========================================
    # CARD DE BOAS-VINDAS / PERFIL PRINCIPAL
    # ==========================================
    hero_card = ctk.CTkFrame(
        scroll,
        fg_color=COLOR_CARD_BG,
        border_color=COLOR_CARD_BORDER,
        border_width=1.5,
        corner_radius=16
    )
    hero_card.pack(fill="x", pady=(0, 20), ipady=12)

    hero_content = ctk.CTkFrame(hero_card, fg_color="transparent")
    hero_content.pack(fill="x", padx=25, pady=10)

    # Avatar com ícone
    avatar_box = ctk.CTkFrame(
        hero_content,
        fg_color="#182A22",
        border_color=COLOR_ACCENT,
        border_width=1.5,
        width=60,
        height=60,
        corner_radius=30
    )
    avatar_box.pack(side="left", padx=(0, 20))
    avatar_box.pack_propagate(False)

    ctk.CTkLabel(
        avatar_box,
        text="👤",
        font=ctk.CTkFont(size=26)
    ).place(relx=0.5, rely=0.5, anchor="center")

    info_box = ctk.CTkFrame(hero_content, fg_color="transparent")
    info_box.pack(side="left", fill="both")

    nome_cliente = dados_atualizados.get("nome", "Cliente EletroBel")
    tipo_conta = dados_atualizados.get("tipo", "cliente").capitalize()
    membro_desde = str(dados_atualizados.get("criado_em", "Recente"))[:10]

    title_frame = ctk.CTkFrame(info_box, fg_color="transparent")
    title_frame.pack(anchor="w")

    ctk.CTkLabel(
        title_frame,
        text=nome_cliente,
        font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    ).pack(side="left", padx=(0, 10))

    badge_tipo = ctk.CTkLabel(
        title_frame,
        text=f"● {tipo_conta}",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=COLOR_ACCENT,
        fg_color="#0F2E20",
        corner_radius=12,
        padx=10,
        pady=2
    )
    badge_tipo.pack(side="left")

    ctk.CTkLabel(
        info_box,
        text=f"E-mail: {dados_atualizados.get('email', '-')}  |  Usuário: @{dados_atualizados.get('usuario', '-')}  |  Membro desde: {membro_desde}",
        font=ctk.CTkFont(family="Segoe UI", size=13),
        text_color=COLOR_TEXT_MUTED
    ).pack(anchor="w", pady=(4, 0))

    # ==========================================
    # CARDS DE MÉTRICAS / ESTATÍSTICAS
    # ==========================================
    metrics_frame = ctk.CTkFrame(scroll, fg_color="transparent")
    metrics_frame.pack(fill="x", pady=(0, 25))
    metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="metric")

    cards_metricas = [
        ("⚡", f"{resumo.get('total_recargas', 0)}", "Sessões de Recarga", COLOR_ACCENT),
        ("🔋", f"{resumo.get('total_kwh', 0.0):.1f} kWh", "Energia Consumida", "#40C4FF"),
        ("💳", f"R$ {resumo.get('total_valor', 0.0):.2f}", "Total Investido", "#FFD700"),
        ("🚗", f"{resumo.get('total_veiculos', 0)}", "Veículos Cadastrados", "#B388FF")
    ]

    for col, (icone, valor, rotulo, cor) in enumerate(cards_metricas):
        card_m = ctk.CTkFrame(
            metrics_frame,
            fg_color=COLOR_CARD_BG,
            border_color=COLOR_CARD_BORDER,
            border_width=1.5,
            corner_radius=14
        )
        card_m.grid(row=0, column=col, padx=6, pady=5, sticky="nsew", ipady=8)

        ctk.CTkLabel(card_m, text=icone, font=ctk.CTkFont(size=24)).pack(pady=(12, 2))
        ctk.CTkLabel(card_m, text=valor, font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color=cor).pack()
        ctk.CTkLabel(card_m, text=rotulo, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MUTED).pack(pady=(0, 10))

    # ==========================================
    # SEÇÃO: MEUS VEÍCULOS ELÉTRICOS
    # ==========================================
    veiculos_header = ctk.CTkFrame(scroll, fg_color="transparent")
    veiculos_header.pack(fill="x", pady=(10, 8))

    ctk.CTkLabel(
        veiculos_header,
        text="🚗 Meus Veículos Elétricos",
        font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    ).pack(side="left")

    def recarregar_tela():
        PerfilUsuario(janela, dados_atualizados, abrir_menu, fazer_logout)

    btn_novo_veiculo = ctk.CTkButton(
        veiculos_header,
        text="+ Cadastrar Veículo",
        font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        text_color="#000000",
        corner_radius=8,
        height=32,
        command=lambda: abrir_modal_novo_veiculo(janela, usuario_id, recarregar_tela)
    )
    btn_novo_veiculo.pack(side="right")

    veiculos_container = ctk.CTkFrame(scroll, fg_color="transparent")
    veiculos_container.pack(fill="x", pady=(0, 25))

    lista_veiculos = database.listar_veiculos(usuario_id) if usuario_id else []

    if not lista_veiculos:
        vazio_frame = ctk.CTkFrame(
            veiculos_container,
            fg_color=COLOR_CARD_BG,
            border_color=COLOR_CARD_BORDER,
            border_width=1,
            corner_radius=12
        )
        vazio_frame.pack(fill="x", ipady=20)

        ctk.CTkLabel(
            vazio_frame,
            text="Você ainda não possui nenhum veículo elétrico cadastrado.",
            font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_MUTED
        ).pack(pady=(8, 4))

        ctk.CTkLabel(
            vazio_frame,
            text="Cadastre seu carro elétrico para obter estimativas de tempo e registrar recargas facilmente.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 10))
    else:
        veiculos_container.grid_columnconfigure((0, 1), weight=1, uniform="veic")
        for idx, veic in enumerate(lista_veiculos):
            r = idx // 2
            c = idx % 2
            card_v = ctk.CTkFrame(
                veiculos_container,
                fg_color=COLOR_CARD_BG,
                border_color=COLOR_CARD_BORDER,
                border_width=1.5,
                corner_radius=14
            )
            card_v.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")

            box_v = ctk.CTkFrame(card_v, fg_color="transparent")
            box_v.pack(fill="both", expand=True, padx=16, pady=14)

            header_v = ctk.CTkFrame(box_v, fg_color="transparent")
            header_v.pack(fill="x")

            ctk.CTkLabel(
                header_v,
                text=f"{veic['marca']} {veic['modelo']}",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=COLOR_TEXT_MAIN
            ).pack(side="left")

            ctk.CTkLabel(
                header_v,
                text=f"Placa: {veic['placa']}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLOR_ACCENT,
                fg_color="#12251B",
                corner_radius=6,
                padx=8,
                pady=2
            ).pack(side="right")

            detalhes_text = (
                f"Ano: {veic.get('ano', '-')}  |  "
                f"Conector: {veic.get('tipo_conector', '-')}  |  "
                f"Bateria: {veic.get('capacidade_bateria_kwh', 0.0):.1f} kWh"
            )
            ctk.CTkLabel(
                box_v,
                text=detalhes_text,
                font=ctk.CTkFont(size=12),
                text_color=COLOR_TEXT_MUTED,
                anchor="w"
            ).pack(fill="x", pady=(6, 0))

    # ==========================================
    # SEÇÃO: HISTÓRICO DE RECARGAS
    # ==========================================
    recargas_header = ctk.CTkFrame(scroll, fg_color="transparent")
    recargas_header.pack(fill="x", pady=(10, 8))

    ctk.CTkLabel(
        recargas_header,
        text="⚡ Histórico de Recargas",
        font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
        text_color=COLOR_TEXT_MAIN
    ).pack(side="left")

    recargas_container = ctk.CTkFrame(scroll, fg_color="transparent")
    recargas_container.pack(fill="x", pady=(0, 20))

    lista_recargas = database.listar_recargas(usuario_id) if usuario_id else []

    if not lista_recargas:
        vazio_r = ctk.CTkFrame(
            recargas_container,
            fg_color=COLOR_CARD_BG,
            border_color=COLOR_CARD_BORDER,
            border_width=1,
            corner_radius=12
        )
        vazio_r.pack(fill="x", ipady=20)

        ctk.CTkLabel(
            vazio_r,
            text="Nenhuma sessão de recarga registrada até o momento.",
            font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_MUTED
        ).pack(pady=(8, 4))

        ctk.CTkButton(
            vazio_r,
            text="⚡ Explorar Eletropostos em Belém e Região",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#182A22",
            hover_color="#223D32",
            text_color=COLOR_ACCENT,
            border_width=1,
            border_color=COLOR_ACCENT,
            corner_radius=8,
            height=34,
            command=abrir_menu
        ).pack(pady=(6, 8))
    else:
        for rec in lista_recargas:
            card_r = ctk.CTkFrame(
                recargas_container,
                fg_color=COLOR_CARD_BG,
                border_color=COLOR_CARD_BORDER,
                border_width=1,
                corner_radius=12
            )
            card_r.pack(fill="x", pady=4)

            box_r = ctk.CTkFrame(card_r, fg_color="transparent")
            box_r.pack(fill="x", padx=16, pady=12)

            # Esquerda: Estação e veículo
            esq = ctk.CTkFrame(box_r, fg_color="transparent")
            esq.pack(side="left", anchor="w")

            ctk.CTkLabel(
                esq,
                text=rec.get("estacao_nome", "Estação EletroBel"),
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=COLOR_TEXT_MAIN
            ).pack(anchor="w")

            data_str = str(rec.get("data_inicio", "-"))[:16]
            veic_nome = rec.get("veiculo_modelo") or "Veículo Elétrico"
            ctk.CTkLabel(
                esq,
                text=f"{veic_nome}  •  Data: {data_str}",
                font=ctk.CTkFont(size=12),
                text_color=COLOR_TEXT_MUTED
            ).pack(anchor="w")

            # Direita: Energia, Valor e Status
            dir_frame = ctk.CTkFrame(box_r, fg_color="transparent")
            dir_frame.pack(side="right", anchor="e")

            ctk.CTkLabel(
                dir_frame,
                text=f"{rec.get('energia_kwh', 0.0):.1f} kWh  |  R$ {rec.get('valor_total', 0.0):.2f}",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=COLOR_ACCENT
            ).pack(anchor="e")

            ctk.CTkLabel(
                dir_frame,
                text=f"● {rec.get('status', 'Concluída')}",
                font=ctk.CTkFont(size=12),
                text_color="#40C4FF"
            ).pack(anchor="e")


# =====================================================================
# MODAL: CADASTRO DE NOVO VEÍCULO ELÉTRICO
# =====================================================================

def abrir_modal_novo_veiculo(parent, usuario_id, callback_sucesso):
    """Abre modal para o cliente cadastrar um novo veículo elétrico."""
    if not usuario_id:
        messagebox.showerror("Erro", "É necessário estar autenticado para cadastrar veículos.")
        return

    modal = ctk.CTkToplevel(parent)
    modal.title("Cadastrar Novo Veículo Elétrico")
    modal.geometry("460x580")
    modal.minsize(420, 520)
    modal.configure(fg_color=COLOR_BG)
    modal.attributes("-topmost", True)

    frame = ctk.CTkFrame(modal, fg_color=COLOR_CARD_BG, corner_radius=16, border_width=1, border_color=COLOR_CARD_BORDER)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        frame,
        text="🚗 Novo Veículo Elétrico",
        font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        text_color=COLOR_ACCENT
    ).pack(pady=(15, 4))

    ctk.CTkLabel(
        frame,
        text="Preencha os dados do seu automóvel elétrico ou híbrido",
        font=ctk.CTkFont(size=12),
        text_color=COLOR_TEXT_MUTED
    ).pack(pady=(0, 15))

    def criar_campo(rotulo, placeholder):
        ctk.CTkLabel(frame, text=rotulo, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w").pack(fill="x", padx=30, pady=(4, 2))
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, width=380, height=38, fg_color=COLOR_INPUT_BG, border_color=COLOR_INPUT_BORDER, text_color=COLOR_TEXT_MAIN)
        entry.pack(padx=30, pady=(0, 6))
        return entry

    ent_marca = criar_campo("Marca", "Ex: BYD, GWM, Tesla, Volvo, Nissan")
    ent_modelo = criar_campo("Modelo", "Ex: Dolphin, Haval H6, Model 3")
    ent_placa = criar_campo("Placa", "Ex: BRA2E19")
    ent_ano = criar_campo("Ano de Fabricação", "Ex: 2024")

    # Conector
    ctk.CTkLabel(frame, text="Tipo de Conector", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w").pack(fill="x", padx=30, pady=(4, 2))
    conector_var = ctk.StringVar(value="CCS2 (Carga Rápida DC)")
    ctk.CTkOptionMenu(
        frame,
        values=["CCS2 (Carga Rápida DC)", "Tipo 2 (AC Normal/Wallbox)", "CHAdeMO", "GB/T"],
        variable=conector_var,
        width=380,
        height=38,
        fg_color=COLOR_INPUT_BG,
        button_color="#1F2D3D",
        button_hover_color=COLOR_ACCENT,
        dropdown_fg_color="#18222F"
    ).pack(padx=30, pady=(0, 6))

    # Bateria
    ent_bateria = criar_campo("Capacidade da Bateria (kWh)", "Ex: 44.9 ou 60.0")

    def salvar_veiculo():
        m = ent_marca.get().strip()
        mod = ent_modelo.get().strip()
        p = ent_placa.get().strip()
        ano_str = ent_ano.get().strip()
        conec = conector_var.get().split()[0]
        bat_str = ent_bateria.get().strip()

        if not m or not mod or not p or not ano_str or not bat_str:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos do veículo.")
            return

        try:
            ano = int(ano_str)
            bat = float(bat_str)
        except ValueError:
            messagebox.showerror("Erro", "Ano e capacidade da bateria devem ser números válidos.")
            return

        sucesso, msg = database.cadastrar_veiculo(
            usuario_id=usuario_id,
            marca=m,
            modelo=mod,
            placa=p,
            ano=ano,
            tipo_conector=conec,
            capacidade_bateria_kwh=bat
        )

        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            modal.destroy()
            callback_sucesso()
        else:
            messagebox.showerror("Erro", msg)

    ctk.CTkButton(
        frame,
        text="Salvar Veículo",
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        text_color="#000000",
        height=40,
        corner_radius=10,
        command=salvar_veiculo
    ).pack(padx=30, pady=(15, 10), fill="x")


# =====================================================================
# TESTE ISOLADO
# =====================================================================

if __name__ == "__main__":
    database.inicializar_banco()
    app = ctk.CTk()
    admin = database.autenticar_usuario("admin", "123")
    PerfilUsuario(app, admin or {"id": 1, "nome": "Cliente Teste", "email": "teste@eletrobel.com", "usuario": "teste", "tipo": "cliente"}, lambda: print("Voltar ao Menu"))
    app.mainloop()
