import customtkinter as ctk
import os
import re
from datetime import datetime
from tkinter import messagebox
from app.core.config import (
    COR_PRINCIPAL, COR_HOVER, COR_FUNDO_LISTA, 
    PRIORITY_ORDER, VAR_DESCRIPTIONS, get_app_path, COR_BORDAS
)

class Step2Frame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.dynamic_widgets = {}

        ctk.CTkLabel(self, text="Passo 2: Parâmetros da OLT", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").pack(anchor="w", pady=(0, 5))

        # --- Help Info ---
        help_info = ctk.CTkFrame(self, fg_color=COR_FUNDO_LISTA, corner_radius=10, border_width=1, border_color=COR_BORDAS)
        help_info.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(help_info, text="⚙️ INSTRUÇÃO: Defina os parâmetros globais da OLT. O arquivo gerado conterá os comandos configurados no Passo 1 repetidos para cada Serial informado, incrementando automaticamente o ID da ONU.", 
                     font=ctk.CTkFont(size=12), text_color="#E0E0E0", wraplength=900, justify="left").pack(padx=15, pady=10)

        id_frame = ctk.CTkFrame(self, fg_color="transparent")
        id_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(id_frame, text="ID Inicial da ONU (0-127):", width=200, anchor="w", text_color="#BABABA", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.entry_id = ctk.CTkEntry(id_frame, width=120, height=35, border_color=COR_BORDAS, fg_color="#18181B")
        self.entry_id.pack(side="left", padx=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#151515", corner_radius=12, border_width=1, border_color=COR_BORDAS)
        self.scroll_frame.pack(fill="both", expand=True, pady=15)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10, side="bottom")

        ctk.CTkButton(btn_frame, text="< Voltar", command=self.go_back, fg_color="gray", hover_color="gray40").pack(side="left")
        ctk.CTkButton(btn_frame, text="GERAR ARQUIVO ✅", command=self.generate_file, fg_color=COR_PRINCIPAL,
                      hover_color=COR_HOVER, height=45, font=ctk.CTkFont(size=14, weight="bold")).pack(side="right")

    def refresh_dynamic_fields(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        self.dynamic_widgets.clear()
        template = str(self.controller.selected_template_content)
        needed_vars = list(set(re.findall(r'\$[A-Z0-9_]+', template)))
        vars_to_ask = [v for v in needed_vars if v not in ['$SN', '$ONU_ID']]
        
        sorted_vars = []
        for p in PRIORITY_ORDER:
            if p in vars_to_ask:
                sorted_vars.append(p)
                vars_to_ask.remove(p)
        sorted_vars.extend(sorted(vars_to_ask))

        for var in sorted_vars:
            desc = VAR_DESCRIPTIONS.get(var, var)
            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f"{desc}:", width=250, anchor="w", text_color="#E0E0E0").pack(side="left", padx=5)
            
            placeholder = "Ex: INTERNET"
            if "ID" in var or "GEM" in var: placeholder = "Ex: 1"
            if "VLAN" in var: placeholder = "Ex: 100"
            if "SLOT" in var or "PON" in var: placeholder = "0"
            
            entry = ctk.CTkEntry(row, placeholder_text=placeholder, height=35, border_color="#333", fg_color="#18181B")
            entry.pack(side="right", expand=True, fill="x", padx=10)
            self.dynamic_widgets[var] = entry

    def go_back(self):
        self.controller.show_frame("Step1Frame")

    def generate_file(self):
        try:
            id_ini = int(self.entry_id.get().strip())
            if not (0 <= id_ini <= 127): raise ValueError()
        except:
            return messagebox.showerror("Erro", "ID Inicial inválido.")

        params = {}
        missing = []
        for var_key, w in self.dynamic_widgets.items():
            val = w.get().strip()
            if not val: 
                missing.append(str(VAR_DESCRIPTIONS.get(str(var_key), str(var_key))))
            params[str(var_key)] = str(val)
        if missing: return messagebox.showwarning("Vazio", f"Preencha: {', '.join(missing)}")

        slot = params.get('$SLOT', '0')
        pon = params.get('$PON', '0')
        
        # --- Create Output Folder ---
        scripts_dir = os.path.join(get_app_path(), "scripts_gerados")
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
            
        # --- Clear Naming ---
        templ_name = self.controller.selected_template_name.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SCRIPT_{templ_name}_SLOT{slot}_PON{pon}_{timestamp}.txt"
        filepath = os.path.join(scripts_dir, filename)

        try:
            is_huawei = self.controller.selected_manufacturer == "Huawei"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"// {str(self.controller.selected_manufacturer)} - {str(self.controller.selected_model)}\n")
                f.write(f"// Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
                
                if is_huawei:
                    f.write("undo smart\n")
                    f.write(f"interface gpon 0/{slot}\n")
                
                curr = id_ini
                for sn in self.controller.serial_numbers:
                    txt = self.controller.selected_template_content
                    for k, v in params.items(): txt = txt.replace(k, v)
                    txt = txt.replace('$SN', sn).replace('$ONU_ID', str(curr))
                    f.write(txt + "\n")
                    curr += 1
                
                if is_huawei:
                    f.write("\nsmart\n")
            
            # Log to DB
            self.controller.db.add_log(
                slot, pon, len(self.controller.serial_numbers), 
                filename, str(self.controller.selected_manufacturer), 
                str(self.controller.selected_model)
            )
            
            messagebox.showinfo("Sucesso", f"O script foi gerado com sucesso!\n\nSalvo em:\n{filepath}")
            
            # --- Auto Open ---
            try:
                os.startfile(filepath)
            except Exception as e_open:
                print(f"Erro ao abrir arquivo: {e_open}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
