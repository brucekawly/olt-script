import customtkinter as ctk
import threading
from app.core.config import (
    COR_PRINCIPAL, COR_HOVER, COR_FUNDO_LISTA, COR_BORDAS
)
from app.gui.dialogs import AuthSelectionDialog, LoadingWindow
from app.services.gemini_service import GeminiService

class GeminiChatFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # --- Header ---
        header = ctk.CTkFrame(self, fg_color=COR_FUNDO_LISTA, corner_radius=12, border_width=1, border_color=COR_BORDAS) 
        header.pack(fill="x", padx=20, pady=10)
        
        # Guide Tip
        guide_text = "💡 Pergunte sobre comandos Huawei, peça para analisar scripts ou tire dúvidas sobre provisionamento GPON."
        ctk.CTkLabel(self, text=guide_text, font=ctk.CTkFont(size=11), text_color="#A0A0A0").pack(pady=(0, 5))
        
        ctk.CTkLabel(header, text="🤖 Assistente Especialista Huawei", 
                     font=ctk.CTkFont(size=16, weight="bold"), text_color=COR_PRINCIPAL).pack(pady=(10, 5))
        
        config_frame = ctk.CTkFrame(header, fg_color="transparent")
        config_frame.pack(pady=(0, 10))

        self.btn_config = ctk.CTkButton(config_frame, text="⚙️ Trocar Chave API", width=120, height=25,
                                        fg_color="#334155", text_color="white", hover_color="#475569",
                                        command=self.force_reauth)
        self.btn_config.pack(side="left", padx=5)

        ctk.CTkLabel(config_frame, text="Modelo:", text_color="white", font=ctk.CTkFont(size=12)).pack(side="left", padx=(10, 5))
        self.model_combo = ctk.CTkComboBox(config_frame, width=200, values=["Aguardando Chave..."],
                                            fg_color="#334155", border_color="#475569")
        self.model_combo.pack(side="left")

        # --- Chat Area ---
        self.chat_display = ctk.CTkTextbox(self, state="disabled", font=("Arial", 12), wrap="word",
                                           fg_color="#151515", border_width=1, border_color=COR_BORDAS)
        self.chat_display.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Input Area ---
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)

        self.msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Digite sua dúvida sobre OLT Huawei...", height=40)
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda e: self.check_auth_and_send())

        self.btn_send = ctk.CTkButton(input_frame, text="Enviar", width=100, height=40,
                                      fg_color=COR_PRINCIPAL, hover_color=COR_HOVER,
                                      command=self.check_auth_and_send)
        self.btn_send.pack(side="right")
        
        self.btn_back = ctk.CTkButton(self, text="Voltar ao Gerador", fg_color="gray", 
                                      command=lambda: controller.show_frame("Step1Frame"))
        self.btn_back.pack(pady=10)

    def force_reauth(self):
        self.controller.current_api_key = None
        self.model_combo.configure(values=["Aguardando Chave..."])
        self.model_combo.set("Aguardando Chave...")
        AuthSelectionDialog(self, self.auth_success)

    def check_auth_and_send(self):
        if self.controller.current_api_key:
            self.send_message()
        else:
            AuthSelectionDialog(self, self.auth_success)

    def auth_success(self, key):
        self.controller.current_api_key = key
        self.controller.db.set_config("api_key", key)
        # Busca modelos em background
        threading.Thread(target=self.fetch_models, args=(key,)).start()
        if self.msg_entry.get().strip():
            self.send_message()

    def fetch_models(self, api_key):
        models = GeminiService.list_models()
        default_model = GeminiService.get_best_model(models)
        self.after(0, lambda: self.update_combo(models, default_model))

    def update_combo(self, models, default):
        self.model_combo.configure(values=models)
        self.model_combo.set(default)

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg: return
        self.append_chat(f"Você: {msg}\n", "black")
        self.msg_entry.delete(0, "end")
        self.loading_win = LoadingWindow(self, "Consultando Especialista...")
        model_name = self.model_combo.get()
        threading.Thread(target=self.call_gemini_thread, args=(msg, model_name)).start()

    def call_gemini_thread(self, prompt, model_name):
        contexto = "Você é um especialista em OLTs Huawei e redes GPON. Responda de forma técnica, direta e concisa. "
        resposta_texto = GeminiService.call_gemini(prompt, model_name, self.controller.current_api_key, contexto)
        self.after(0, lambda: self.finish_request(resposta_texto))

    def finish_request(self, text):
        if hasattr(self, 'loading_win'): self.loading_win.destroy()
        self.append_chat(f"IA: {text}\n\n", COR_PRINCIPAL)

    def append_chat(self, text, color):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
