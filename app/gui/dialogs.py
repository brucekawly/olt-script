import customtkinter as ctk
from tkinter import messagebox
from app.core.config import COR_PRINCIPAL, COR_HOVER

class AuthSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback_success):
        super().__init__(parent)
        self.callback = callback_success
        self.title("Configuração de Acesso IA")
        self.geometry("400x350")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0F172A")
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 175
        self.geometry(f"+{x}+{y}")

        ctk.CTkLabel(self, text="Configure sua Chave Gemini", 
                     font=ctk.CTkFont(size=18, weight="bold"), text_color=COR_PRINCIPAL).pack(pady=15)

        # --- CHAVE PRÓPRIA ---
        from app.core.config import COR_FUNDO_LISTA, COR_BORDAS
        frame_custom = ctk.CTkFrame(self, fg_color=COR_FUNDO_LISTA, border_width=1, border_color=COR_BORDAS)
        frame_custom.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(frame_custom, text="Insira sua API Key:", font=ctk.CTkFont(weight="bold"), text_color="white").pack(pady=5)
        self.entry_key = ctk.CTkEntry(frame_custom, placeholder_text="AIza...", justify="center", fg_color="#18181B", border_color=COR_BORDAS)
        self.entry_key.pack(pady=5, fill="x", padx=20)
        
        ctk.CTkButton(frame_custom, text="Salvar e Validar", command=self.use_custom_key, 
                      fg_color=COR_PRINCIPAL, hover_color=COR_HOVER, height=35).pack(pady=15)

    def use_custom_key(self):
        key = self.entry_key.get().strip()
        if len(key) > 10: 
            self.callback(key)
            self.destroy()
        else:
            messagebox.showwarning("Atenção", "Chave de API parece inválida ou muito curta.", parent=self)

class LoadingWindow(ctk.CTkToplevel):
    def __init__(self, parent, message="Processando..."):
        super().__init__(parent)
        self.title("Aguarde")
        self.geometry("300x120")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0F0F0F")
        self.overrideredirect(True) 

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 150
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 60
        self.geometry(f"+{x}+{y}")
        
        from app.core.config import COR_FUNDO_LISTA, COR_BORDAS
        self.frame = ctk.CTkFrame(self, fg_color=COR_FUNDO_LISTA, border_width=2, border_color=COR_PRINCIPAL)
        self.frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.frame, text=message, font=ctk.CTkFont(size=14, weight="bold"), 
                     text_color=COR_PRINCIPAL).pack(pady=(20, 10))

        self.progress = ctk.CTkProgressBar(self.frame, width=200, progress_color=COR_PRINCIPAL, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.start()

class ResultWindow(ctk.CTkToplevel):
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x500")
        self.configure(fg_color="#0F172A")
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=20, weight="bold"), 
                     text_color="white").pack(pady=15)

        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 12), fg_color="#030712", text_color="#E2E8F0",
                                      border_width=1, border_color="#333333")
        self.textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.textbox.insert("0.0", content)
        self.textbox.configure(state="disabled")
