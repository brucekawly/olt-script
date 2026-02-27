import customtkinter as ctk
import os
import sys

# Import components from the new modular structure
from app.core.config import (
    COR_PRINCIPAL, COR_HOVER, COR_TEXTO_TITULO,
    COR_FUNDO_APP, COR_FUNDO_CONTENT
)
from app.gui.manufacturer_frame import ManufacturerFrame
from app.gui.step1_frame import Step1Frame
from app.gui.step2_frame import Step2Frame
from app.gui.chat_frame import GeminiChatFrame
from app.gui.history_frame import HistoryFrame
from app.core.database import Database

# Global Configurations
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class OLTGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OLT Script - Professional GPON Manager")
        self.geometry("1200x900")
        self.configure(fg_color=COR_FUNDO_APP)

        self.db = Database()
        self.selected_manufacturer = "Huawei"
        self.selected_model = "Geral"
        self.selected_template_content = ""
        self.selected_template_name = ""
        self.serial_numbers = []
        self.current_api_key = self.db.get_config("api_key") 

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(20, 0))

        # Title and Buttons Container
        action_bar = ctk.CTkFrame(self.header_frame, fg_color="transparent", height=60)
        action_bar.pack(fill="x", padx=30)
        action_bar.pack_propagate(False) # Ensure the height is respected
        
        # Center Title
        self.label_company = ctk.CTkLabel(action_bar, text="OLT Script",
                                          font=ctk.CTkFont(size=40, weight="bold", family="Arial Black"),
                                          text_color=COR_TEXTO_TITULO)
        self.label_company.place(relx=0.5, rely=0.5, anchor="center")
        
        # Action Buttons on Right
        buttons_box = ctk.CTkFrame(action_bar, fg_color="transparent")
        buttons_box.pack(side="right")

        self.btn_history = ctk.CTkButton(buttons_box, text="📜 Histórico", width=120,
                                         fg_color="#374151", hover_color="#4B5563",
                                         command=lambda: self.show_frame("HistoryFrame"))
        self.btn_history.pack(side="left", padx=5)

        self.btn_ai = ctk.CTkButton(buttons_box, text="🤖 Assistente IA", width=120,
                                    fg_color=COR_PRINCIPAL, hover_color=COR_HOVER,
                                    command=lambda: self.show_frame("GeminiChatFrame"))
        self.btn_ai.pack(side="left", padx=5)

        # Progress bar
        ctk.CTkProgressBar(self, height=3, progress_color=COR_PRINCIPAL).pack(fill="x", padx=30, pady=(0, 20))

        # --- BODY ---
        self.container = ctk.CTkFrame(self, fg_color=COR_FUNDO_CONTENT, corner_radius=15, border_width=1, border_color="#333")
        self.container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.frame_manufacturer = ManufacturerFrame(self.container, controller=self)
        self.frame_step1 = Step1Frame(self.container, controller=self)
        self.frame_step2 = Step2Frame(self.container, controller=self)
        self.frame_ai = GeminiChatFrame(self.container, controller=self)
        self.frame_history = HistoryFrame(self.container, controller=self)

        self.show_frame("ManufacturerFrame")

    def show_frame(self, frame_name):
        self.frame_manufacturer.pack_forget()
        self.frame_step1.pack_forget()
        self.frame_step2.pack_forget()
        self.frame_ai.pack_forget()
        self.frame_history.pack_forget()
        
        if frame_name == "ManufacturerFrame":
            self.frame_manufacturer.pack(fill="both", expand=True)
        elif frame_name == "Step1Frame":
            self.frame_step1.refresh_templates() # New method for filtering
            self.frame_step1.pack(fill="both", expand=True)
        elif frame_name == "Step2Frame":
            self.frame_step2.refresh_dynamic_fields()
            self.frame_step2.pack(fill="both", expand=True)
        elif frame_name == "GeminiChatFrame":
            self.frame_ai.pack(fill="both", expand=True)
        elif frame_name == "HistoryFrame":
            self.frame_history.refresh_logs()
            self.frame_history.pack(fill="both", expand=True)

        # Footer Copyright (Always at bottom)
        if hasattr(self, "label_credit"):
            self.label_credit.destroy()
        self.label_credit = ctk.CTkLabel(self, text="© 2026 Bruce Kawly All rights Reserved", 
                                         font=ctk.CTkFont(size=11), text_color="gray50")
        self.label_credit.pack(side="bottom", pady=5)

if __name__ == "__main__":
    app = OLTGeneratorApp()
    app.mainloop()
