"""
Módulo pasta_usuario.py
Alias para perfil_usuario.py para manter compatibilidade e flexibilidade de importação.
"""
from perfil_usuario import PerfilUsuario, abrir_modal_novo_veiculo

__all__ = ["PerfilUsuario", "abrir_modal_novo_veiculo"]


if __name__ == "__main__":
    import customtkinter as ctk
    import database
    from menu import Menu

    database.inicializar_banco()
    app = ctk.CTk()
    admin = database.autenticar_usuario("admin", "123")
    PerfilUsuario(
        app,
        admin or {"id": 1, "nome": "Cliente Teste", "email": "teste@eletrobel.com", "usuario": "teste", "tipo": "cliente"},
        lambda: Menu(app),
    )
    app.mainloop()

