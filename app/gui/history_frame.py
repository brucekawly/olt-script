import customtkinter as ctk
import os
from datetime import datetime, timedelta
from tkinter import messagebox
from app.core.config import (
    COR_PRINCIPAL, COR_HOVER, COR_FUNDO_LISTA, 
    get_app_path, COR_BORDAS, COR_PERIGOSA
)

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Histórico de Scripts Gerados", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").pack(anchor="w", pady=(0, 5))
        
        # --- Layout Container for Columns ---
        content_box = ctk.CTkFrame(self, fg_color="transparent")
        content_box.pack(fill="both", expand=True)

        # Left side: List of logs
        self.list_container = ctk.CTkFrame(content_box, fg_color=COR_FUNDO_LISTA, corner_radius=12, border_width=1, border_color=COR_BORDAS, width=420)
        self.list_container.pack(side="left", fill="both", expand=False, padx=(0, 10), pady=10)
        
        ctk.CTkLabel(self.list_container, text="Atividades Recentes", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        self.scroll_list = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.scroll_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Right side: Preview
        self.preview_container = ctk.CTkFrame(content_box, fg_color="#1E1E1E", corner_radius=12, border_width=1, border_color=COR_BORDAS)
        self.preview_container.pack(side="left", fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(self.preview_container, text="Visualização do Script", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        self.preview_box = ctk.CTkTextbox(self.preview_container, font=("Consolas", 12), fg_color="#121212", 
                                          text_color="#FFFFFF", border_width=1, border_color="#333")
        self.preview_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        btn_footer = ctk.CTkFrame(self.preview_container, fg_color="transparent")
        btn_footer.pack(pady=(0, 15))

        self.btn_open_external = ctk.CTkButton(btn_footer, text="📂 Abrir Arquivo", command=self.open_current_file,
                                               fg_color=COR_PRINCIPAL, hover_color=COR_HOVER, width=150)
        self.btn_open_external.pack(side="left", padx=5)

        self.btn_delete_log = ctk.CTkButton(btn_footer, text="🗑️ Excluir Registro", command=self.delete_current_log,
                                            fg_color=COR_PERIGOSA, hover_color="#991B1B", width=150)
        self.btn_delete_log.pack(side="left", padx=5)
        
        self.current_selected_path = ""
        self.current_selected_id = 0

        # Back button
        ctk.CTkButton(self, text="< Voltar para o Início", command=lambda: self.controller.show_frame("Step1Frame"),
                      fg_color="gray", hover_color="gray40").pack(side="bottom", pady=10)

    def refresh_logs(self):
        for widget in self.scroll_list.winfo_children():
            widget.destroy()
        
        logs = self.controller.db.get_logs()
        if not logs:
            ctk.CTkLabel(self.scroll_list, text="Nenhum script gerado ainda.", text_color="gray").pack(pady=20)
            return

        current_date_group = None
        for log in logs:
            log_id, ts, slot, pon, count, filename, fab, mod = log
            
            # Extract date for grouping
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                date_key = dt.date()
                
                # Title for the group
                today = datetime.now().date()
                if date_key == today:
                    group_label = "HOJE"
                elif date_key == today - timedelta(days=1):
                     group_label = "ONTEM"
                else:
                    group_label = date_key.strftime("%d/%m/%Y")
                
                if group_label != current_date_group:
                    current_date_group = group_label
                    lbl = ctk.CTkLabel(self.scroll_list, text=group_label, font=ctk.CTkFont(size=12, weight="bold"),
                                       text_color=COR_PRINCIPAL, anchor="w")
                    lbl.pack(fill="x", pady=(15, 5), padx=5)
                
                display_ts = dt.strftime("%H:%M")
            except:
                display_ts = ts

            btn_text = f"[{display_ts}] {fab} ({mod}) | S:{slot} P:{pon} | Qty:{count}"
            btn = ctk.CTkButton(self.scroll_list, text=btn_text, anchor="w", height=45,
                                fg_color="#2A2A2A", hover_color="#3A3A3A", font=ctk.CTkFont(size=10),
                                command=lambda f=filename, lid=log_id: self.load_preview(f, lid))
            btn.pack(fill="x", pady=1, padx=5)

    def load_preview(self, filename, log_id):
        scripts_dir = os.path.join(get_app_path(), "scripts_gerados")
        filepath = os.path.join(scripts_dir, filename)
        self.current_selected_path = filepath
        self.current_selected_id = log_id
        
        self.preview_box.configure(state="normal")
        self.preview_box.delete("1.0", "end")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.preview_box.insert("1.0", content)
            except Exception as e:
                self.preview_box.insert("1.0", f"Erro ao ler arquivo: {e}")
        else:
            self.preview_box.insert("1.0", "Arquivo não encontrado. Ele pode ter sido movido ou excluído.")
            
        self.preview_box.configure(state="disabled")

    def delete_current_log(self):
        if not self.current_selected_id:
            return messagebox.showwarning("Atenção", "Selecione um registro para excluir.")
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este registro do histórico?\n(O arquivo físico NÃO será excluído)"):
            self.controller.db.delete_log(self.current_selected_id)
            self.current_selected_id = 0
            self.current_selected_path = ""
            self.preview_box.configure(state="normal")
            self.preview_box.delete("1.0", "end")
            self.preview_box.configure(state="disabled")
            self.refresh_logs()
            messagebox.showinfo("Sucesso", "Registro removido com sucesso.")

    def open_current_file(self):
        if self.current_selected_path and os.path.exists(self.current_selected_path):
            try:
                os.startfile(self.current_selected_path)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")
        else:
            messagebox.showwarning("Atenção", "Selecione um script válido primeiro.")
