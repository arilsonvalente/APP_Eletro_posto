
from pathlib import Path
import customtkinter as ctk
import tkinter.messagebox as messagebox
from PIL import Image

# ==========================================
# CONFIGURAÇÕES
# ==========================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "logo_eletrobel.jpeg"


class EletroBelLogin(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("EletroBel | Mobilidade Elétrica & Energia")
        self.geometry("1200x760")
        self.minsize(950, 650)
        self.configure(fg_color="#061326")

        # Configuração das colunas
        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # Painel esquerdo
        self.left_panel = ctk.CTkFrame(
            self,
            fg_color="#071A32",
            corner_radius=0
        )
        self.left_panel.grid(
            row=0, column=0, sticky="nsew"
        )

        # Painel direito
        self.right_panel = ctk.CTkFrame(
            self,
            fg_color="#0A1729",
            corner_radius=0
        )
        self.right_panel.grid(
            row=0, column=1, sticky="nsew"
        )

        self._build_brand_panel()
        self._build_login_panel()

    # ==========================================
    # PAINEL DA MARCA
    # ==========================================

    def _build_brand_panel(self):

        janela = ctk.CTkFrame(
            self.left_panel,
            fg_color="transparent"
        )
        janela.pack(
            expand=True,
            fill="both",
            padx=40,
            pady=30
        )

        # Logomarca
        if LOGO_PATH.exists():
            try:
                logo_img = Image.open(LOGO_PATH).convert("RGBA")

                self.logo = ctk.CTkImage(
                    light_image=logo_img,
                    dark_image=logo_img,
                    size=(300, 220)
                )

                ctk.CTkLabel(
                    janela,
                    image=self.logo,
                    text=""
                ).pack(pady=(10, 15))

            except Exception as erro:
                print(f"Erro ao carregar a logo: {erro}")
                self._mostrar_nome(janela)

        else:
            print(f"Logomarca não encontrada: {LOGO_PATH}")
            self._mostrar_nome(janela)

        # Título
        ctk.CTkLabel(
            janela,
            text="ENERGIA QUE MOVE O FUTURO",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color="#F5F8FF"
        ).pack(pady=(5, 10))

        ctk.CTkLabel(
            janela,
            text="Mobilidade elétrica • Tecnologia • Sustentabilidade",
            font=ctk.CTkFont(size=13),
            text_color="#9DB4D1",
            wraplength=420
        ).pack(pady=(0, 22))

        # Cartão de carregamento
        charger = ctk.CTkFrame(
            janela,
            fg_color="#0D2746",
            border_color="#167BFF",
            border_width=1,
            corner_radius=18,
            height=105
        )
        charger.pack(fill="x", padx=8, pady=10)
        charger.pack_propagate(False)

        ctk.CTkLabel(
            charger,
            text="⚡",
            font=ctk.CTkFont(size=42),
            text_color="#27F05B",
            width=75
        ).pack(side="left", padx=(12, 5))

        info = ctk.CTkFrame(
            charger,
            fg_color="transparent"
        )
        info.pack(
            side="left",
            expand=True,
            fill="both",
            pady=18
        )

        ctk.CTkLabel(
            info,
            text="POSTOS DE CARREGAMENTO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            info,
            text="Conecte-se a uma nova experiência de energia.",
            font=ctk.CTkFont(size=12),
            text_color="#9DB4D1",
            anchor="w",
            wraplength=260
        ).pack(fill="x", pady=(5, 0))

        ctk.CTkLabel(
            janela,
            text="Soluções inteligentes para um caminho mais limpo.",
            font=ctk.CTkFont(size=12),
            text_color="#6F8BAE",
            wraplength=420
        ).pack(side="bottom", pady=(20, 0))

    def _mostrar_nome(self, janela):

        ctk.CTkLabel(
            janela,
            text="EletroBel",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="#28F05A"
        ).pack(pady=(45, 30))

    # ==========================================
    # PAINEL DE LOGIN
    # ==========================================

    def _build_login_panel(self):

        card = ctk.CTkFrame(
            self.right_panel,
            fg_color="#101F34",
            border_color="#164C83",
            border_width=1,
            corner_radius=24
        )
        card.pack(
            expand=True,
            padx=35,
            pady=35,
            fill="both"
        )

        # Cabeçalho
        ctk.CTkLabel(
            card,
            text="Bem-vindo",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#F5F8FF"
        ).pack(pady=(35, 7))

        ctk.CTkLabel(
            card,
            text="Acesse sua conta para continuar",
            font=ctk.CTkFont(size=14),
            text_color="#9DB4D1"
        ).pack(pady=(0, 28))

        # Campo usuário
        self.user = ctk.CTkEntry(
            card,
            height=48,
            corner_radius=12,
            placeholder_text="Usuário",
            border_color="#237BD0",
            fg_color="#0B192B",
            text_color="#FFFFFF",
            placeholder_text_color="#8EA4BF",
            font=ctk.CTkFont(size=14)
        )
        self.user.pack(fill="x", padx=28, pady=8)

        # Campo senha
        self.password = ctk.CTkEntry(
            card,
            height=48,
            corner_radius=12,
            placeholder_text="Senha",
            show="*",
            border_color="#237BD0",
            fg_color="#0B192B",
            text_color="#FFFFFF",
            placeholder_text_color="#8EA4BF",
            font=ctk.CTkFont(size=14)
        )
        self.password.pack(fill="x", padx=28, pady=8)

        # Mostrar / ocultar senha
        self.show_password = ctk.CTkCheckBox(
            card,
            text="Mostrar senha",
            font=ctk.CTkFont(size=12),
            text_color="#9DB4D1",
            fg_color="#167BFF",
            hover_color="#0860C5",
            command=self._toggle_password
        )
        self.show_password.pack(
            anchor="w",
            padx=30,
            pady=(5, 15)
        )

        # Botão entrar
        ctk.CTkButton(
            card,
            text="➜   Entrar",
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#087BFA",
            hover_color="#075BC4",
            command=self._login
        ).pack(fill="x", padx=28, pady=8)

        # Botão cadastrar
        ctk.CTkButton(
            card,
            text="＋   Cadastrar",
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#00A83B",
            hover_color="#00872F",
            command=self._cadastrar
        ).pack(fill="x", padx=28, pady=8)

        # Botão tela inicial
        ctk.CTkButton(
            card,
            text="⌂   Tela Inicial",
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=15),
            fg_color="#344B68",
            hover_color="#496482",
            command=self._tela_inicial
        ).pack(fill="x", padx=28, pady=(8, 20))

        # Rodapé
        ctk.CTkLabel(
            card,
            text="EletroBel • Mobilidade Elétrica & Energia",
            font=ctk.CTkFont(size=11),
            text_color="#6F8BAE"
        ).pack(side="bottom", pady=(5, 15))

        # Permite pressionar Enter para tentar entrar
        self.bind("<Return>", lambda event: self._login())

    # ==========================================
    # FUNÇÕES DOS BOTÕES
    # ==========================================

    def _toggle_password(self):

        if self.show_password.get():
            self.password.configure(show="")
        else:
            self.password.configure(show="*")

    def _login(self):

        usuario = self.user.get().strip()
        senha = self.password.get()

        if not usuario or not senha:
            messagebox.showwarning(
                "Atenção",
                "Preencha o usuário e a senha."
            )
            return

        # Ainda não conectado ao banco de dados
        messagebox.showinfo(
            "Login",
            "Campos preenchidos corretamente.\n\n"
            "Conecte a autenticação ao MySQL "
            "para validar o acesso."
        )

    def _cadastrar(self):

        messagebox.showinfo(
            "Cadastro",
            "A tela de cadastro de usuários "
            "será integrada nesta função."
        )

    def _tela_inicial(self):

        messagebox.showinfo(
            "EletroBel",
            "Você está na tela inicial de acesso."
        )


# ==========================================
# INICIAR A APLICAÇÃO
# ==========================================

if __name__ == "__main__":
    app = EletroBelLogin()
    app.mainloop()
