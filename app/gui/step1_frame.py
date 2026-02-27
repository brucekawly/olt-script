import customtkinter as ctk
import re
import threading
from tkinter import messagebox
from app.core.config import (
    COR_PRINCIPAL, COR_HOVER, COR_FUNDO_LISTA, TEMPLATES_PADRAO, 
    VAR_DESCRIPTIONS, AVAILABLE_VARS, COR_BORDAS, COR_FUNDO_CONTENT,
    COR_AVISO, COR_PERIGOSA, VARS_HUAWEI
)
from app.gui.dialogs import AuthSelectionDialog, LoadingWindow, ResultWindow
from app.services.gemini_service import GeminiService

class AddVarDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Nova Variável")
        self.geometry("400x300")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="white")
        ctk.CTkLabel(self, text="Criar Nova Variável", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COR_PRINCIPAL).pack(pady=20)
        ctk.CTkLabel(self, text="Nome (ex: $WIFI):", text_color="black").pack(anchor="w", padx=20)
        self.entry_name = ctk.CTkEntry(self, placeholder_text="$VARIAVEL")
        self.entry_name.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(self, text="Descrição (ex: Nome da Rede):", text_color="black").pack(anchor="w", padx=20)
        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Explicação")
        self.entry_desc.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(self, text="Salvar", command=self.save_var, fg_color=COR_PRINCIPAL,
                      hover_color=COR_HOVER).pack(pady=10)

    def save_var(self):
        name = self.entry_name.get().strip().upper()
        desc = self.entry_desc.get().strip()
        if not name: return
        if not name.startswith("$"): name = "$" + name
        if not desc: desc = "Personalizada"
        self.callback(name, desc)
        self.destroy()

class Step1Frame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        ctk.CTkLabel(self, text="Passo 1: Configuração do Script", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").pack(anchor="w", pady=(0, 5))
        
        # --- Help Info ---
        help_info = ctk.CTkFrame(self, fg_color=COR_FUNDO_LISTA, corner_radius=10, border_width=1, border_color=COR_BORDAS)
        help_info.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(help_info, text="💡 DICA: Use as variáveis da lista ao lado no seu script. O sistema irá perguntar o valor de cada uma no próximo passo. Cole os Seriais da OLT um por linha no campo abaixo.", 
                     font=ctk.CTkFont(size=12), text_color="#E0E0E0", wraplength=900, justify="left").pack(padx=15, pady=10)

        # --- Template Selection ---
        combo_frame = ctk.CTkFrame(self, fg_color="transparent")
        combo_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(combo_frame, text="Selecione o Modelo:", text_color="white").pack(side="left", padx=(0, 10))
        
        self.template_combo = ctk.CTkOptionMenu(combo_frame, command=self.on_template_change, 
                                                width=300, fg_color="#262626", button_color="#333", button_hover_color="#444")
        self.template_combo.pack(side="left")
        
        # Track template name in controller
        self.controller.selected_template_name = "Personalizado"

        # Editor Container
        self.editor_container = ctk.CTkFrame(self, fg_color=COR_FUNDO_CONTENT, corner_radius=12, border_width=1, border_color=COR_BORDAS)
        self.editor_container.pack(fill="both", expand=True, pady=10)
        self.editor_container.grid_columnconfigure(0, weight=1) # Kept this as it's essential for layout
        self.editor_container.grid_columnconfigure(1, weight=0)
        self.editor_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.editor_container, text="Editor de Script", font=ctk.CTkFont(weight="bold", size=12),
                     text_color="white").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.custom_script_box = ctk.CTkTextbox(self.editor_container, height=220, font=("Consolas", 14), 
                                                fg_color="#18181B", text_color="#FFFFFF", 
                                                border_width=1, border_color=COR_BORDAS, undo=True)
        self.custom_script_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        btn_row = ctk.CTkFrame(self.editor_container, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.btn_analyze = ctk.CTkButton(btn_row, text="🔍 Analisar com IA", fg_color="#4CAF50", hover_color="#388E3C",
                      height=30, command=self.check_auth_and_analyze)
        self.btn_analyze.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.btn_save_template = ctk.CTkButton(btn_row, text="💾 Salvar Template", fg_color=COR_AVISO, hover_color="#B45309",
                      height=35, font=ctk.CTkFont(weight="bold"), command=self.save_current_as_template)
        # Visible only for 'Personalizado'
        
        self.btn_delete_template = ctk.CTkButton(btn_row, text="🗑️ Remover", fg_color=COR_PERIGOSA, hover_color="#991B1B",
                      height=35, font=ctk.CTkFont(weight="bold"), command=self.delete_selected_template)
        # Visible only for non-default templates

        right_header = ctk.CTkFrame(self.editor_container, fg_color="transparent")
        right_header.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(right_header, text="Variáveis", font=ctk.CTkFont(weight="bold"), text_color="white").pack(side="left")
        ctk.CTkButton(right_header, text="+ Criar", width=60, height=22, fg_color=COR_PRINCIPAL, hover_color=COR_HOVER,
                      command=lambda: AddVarDialog(self, self.add_custom_variable)).pack(side="right")

        self.vars_scroll = ctk.CTkScrollableFrame(self.editor_container, width=280, fg_color="transparent")
        self.vars_scroll.grid(row=1, column=1, sticky="nsew", padx=10, pady=(0, 10))
        # vars list will be refreshed in show_frame transition or refresh_templates

        # --- SNS ---
        sn_frame = ctk.CTkFrame(self, fg_color="transparent")
        sn_frame.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(sn_frame, text="Serial Numbers (um por linha):", text_color="#BABABA", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.sn_textbox = ctk.CTkTextbox(sn_frame, height=140, fg_color="#18181B", text_color="#FFFFFF", 
                                         border_width=1, border_color=COR_BORDAS)
        self.sn_textbox.pack(fill="both", expand=True, pady=(5, 0))

        # --- FOOTER ---
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(10, 0))
        
        self.btn_back = ctk.CTkButton(footer_frame, text="< VOLTAR", command=self.go_back, 
                                      fg_color="#4B5563", hover_color="#374151")
        self.btn_back.pack(side="left")

        self.btn_next = ctk.CTkButton(footer_frame, text="AVANÇAR >", command=self.go_next, height=45,
                                      hover_color=COR_HOVER)
        self.btn_next.pack(side="right")
        
        # Load templates after all buttons (btn_save_template, etc) are initialized
        self.load_templates()

    def insert_var(self, var_name):
        self.custom_script_box.insert("insert", var_name)

    def add_custom_variable(self, name, desc):
        VAR_DESCRIPTIONS[name] = desc
        if name not in AVAILABLE_VARS: AVAILABLE_VARS.append(name)
        self.refresh_vars_list()
        self.insert_var(name)

    def refresh_vars_list(self):
        for w in self.vars_scroll.winfo_children(): w.destroy()
        
        is_huawei = self.controller.selected_manufacturer == "Huawei"
        
        for var in AVAILABLE_VARS:
            # Filter Huawei specific vars
            if var in VARS_HUAWEI and not is_huawei:
                continue
                
            desc = VAR_DESCRIPTIONS.get(var, "")
            btn = ctk.CTkButton(self.vars_scroll, text=f"{var} - {desc}", height=32, anchor="w",
                                fg_color="#262626", text_color="#E0E0E0", hover_color="#333333",
                                border_width=1, border_color="#404040",
                                command=lambda v=var: self.insert_var(v))
            btn.pack(fill="x", pady=2)

    def refresh_templates(self):
        # This is called when switching to Step1Frame
        self.refresh_vars_list()
        self.load_templates()

    def load_templates(self):
        manufacturer = self.controller.selected_manufacturer
        model = self.controller.selected_model
        
        self.all_templates = self.controller.db.get_templates(manufacturer, model)
        opcoes = []
        for nome, data in self.all_templates.items():
            is_system = data["is_default"]
            display_name = f"{nome} [Sistema]" if is_system else nome
            opcoes.append(display_name)
        
        opcoes.append("Personalizado (Criar Novo)")
        self.template_combo.configure(values=opcoes)
        
        # Select first system template if available
        default_choice = "Personalizado (Criar Novo)"
        for opt in opcoes:
            if "[Sistema]" in str(opt):
                default_choice = str(opt)
                break
        
        self.template_combo.set(default_choice)
        self.on_template_change(default_choice)

    def on_template_change(self, choice):
        # Clean current selection UI
        self.btn_save_template.pack_forget()
        self.btn_delete_template.pack_forget()
        
        if choice == "Personalizado (Criar Novo)":
            self.custom_script_box.delete("1.0", "end")
            self.controller.selected_template_content = ""
            self.controller.selected_template_name = "Personalizado"
            self.btn_save_template.pack(side="left", expand=True, fill="x", padx=(5, 0))
        else:
            # Revert display name to real key
            real_name = choice.replace(" [Sistema]", "")
            self.controller.selected_template_name = real_name
            data = self.all_templates.get(real_name, {})
            content = data.get("content", "")
            
            self.custom_script_box.delete("1.0", "end")
            self.custom_script_box.insert("1.0", content)
            self.controller.selected_template_content = content
            
            # If not system/default, show delete button
            is_system = data.get("is_default") or real_name in ["Router Generico", "Bridge", "Veip", "VEIP"]
            if not is_system:
                self.btn_delete_template.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def delete_selected_template(self):
        choice = self.template_combo.get()
        real_name = choice.replace(" [Sistema]", "")
        if messagebox.askyesno("Confirmar", f"Deseja remover o template '{real_name}'?"):
            self.controller.db.delete_template(real_name)
            self.load_templates()

    def save_current_as_template(self):
        script = self.custom_script_box.get("1.0", "end").strip()
        if not script: return messagebox.showwarning("Atenção", "Script vazio.")
        
        # Simple name prompt
        dialog = ctk.CTkInputDialog(text="Digite o nome para este modelo:", title="Salvar Template")
        name = dialog.get_input()
        
        if name:
            fabricante = self.controller.selected_manufacturer
            modelo = self.controller.selected_model
            self.controller.db.save_template(name, script, fabricante, modelo)
            messagebox.showinfo("Sucesso", f"Template '{name}' salvo!")
            self.load_templates()
            # Set to new template
            self.template_combo.set(name)
            self.on_template_change(name)

    def go_back(self):
        self.controller.show_frame("ManufacturerFrame")

    def go_next(self):
        # Always use what is currently in the script box
        raw = self.custom_script_box.get("1.0", "end").strip()
        if not raw: return messagebox.showwarning("Atenção", "Script vazio.")
        self.controller.selected_template_content = raw
        
        raw_sns = self.sn_textbox.get("1.0", "end")
        lines = [line.strip().upper() for line in raw_sns.splitlines() if line.strip()]
        
        if not lines: return messagebox.showwarning("Atenção", "Insira pelo menos um Serial Number.")
        
        # 1. Deduplication
        unique_sns = list(dict.fromkeys(lines))
        duplicates_removed = len(lines) - len(unique_sns)
        
        # 2. Limit 128
        if len(unique_sns) > 128:
            messagebox.showwarning("Limite Excedido", "O sistema permite no máximo 128 seriais por vez.")
            unique_sns = unique_sns[:128]
            
        # 3. GPON Format Validation (Common format: 4 chars Vendor + 8 chars Serial Hex/ID)
        # We'll allow 12-16 chars to be safe but warn if it doesn't look like a standard serial
        invalid_sns = []
        gpon_pattern = re.compile(r'^[A-Z0-9]{12,16}$')
        
        for sn in unique_sns:
            if not gpon_pattern.match(sn):
                invalid_sns.append(sn)
                
        if invalid_sns:
            msg = f"Os seguintes seriais parecem inválidos (devem ter 12-16 caracteres alfanuméricos):\n\n"
            msg += "\n".join(invalid_sns[:5])
            if len(invalid_sns) > 5: msg += f"\n... e mais {len(invalid_sns)-5}"
            if not messagebox.askyesno("Seriais Inválidos", msg + "\n\nDeseja ignorar e prosseguir mesmo assim?"):
                return

        if duplicates_removed > 0:
            messagebox.showinfo("Limpeza Realizada", f"{duplicates_removed} seriais duplicados foram removidos automaticamente.")

        # Update controller and proceed
        self.controller.serial_numbers = unique_sns
        self.controller.show_frame("Step2Frame")

    def check_auth_and_analyze(self):
        if self.controller.current_api_key:
            self.analyze_script()
        else:
            AuthSelectionDialog(self, self.auth_success)

    def auth_success(self, key):
        self.controller.current_api_key = key
        # Also triggers fetch_models for chat frame
        threading.Thread(target=self.controller.frame_ai.fetch_models, args=(key,)).start()
        self.analyze_script()

    def analyze_script(self):
        script = self.custom_script_box.get("1.0", "end").strip()
        if not script: return
        self.loading_win = LoadingWindow(self, "Analisando Script...")
        model_name = self.controller.frame_ai.model_combo.get()
        threading.Thread(target=self.run_gemini_analysis, args=(script, model_name)).start()

    def run_gemini_analysis(self, script, model_name):
        prompt = f"Atue como um Engenheiro Sênior Huawei. Analise o script GPON: {script}"
        result_text = GeminiService.call_gemini(prompt, model_name, self.controller.current_api_key)
        self.after(0, lambda: self.show_result(result_text))

    def show_result(self, text):
        if hasattr(self, 'loading_win'): self.loading_win.destroy()
        ResultWindow(self, "Resultado da Análise IA", text)
