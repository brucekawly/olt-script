import customtkinter as ctk
from app.core.config import OLT_MODELS, COR_PRINCIPAL, COR_HOVER

class ManufacturerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Title
        ctk.CTkLabel(self, text="Selecione o Equipamento", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True)

        # Manufacturer Selection
        ctk.CTkLabel(container, text="Selecione o Fabricante da OLT:", 
                     font=ctk.CTkFont(size=16)).pack(pady=(0, 10))
        
        self.manufacturer_var = ctk.StringVar(value="Huawei")
        self.manufacturer_menu = ctk.CTkOptionMenu(container, 
                                                   values=list(OLT_MODELS.keys()),
                                                   variable=self.manufacturer_var,
                                                   command=self.update_models,
                                                   width=300, height=40)
        self.manufacturer_menu.pack(pady=10)

        # Model/Version Selection
        ctk.CTkLabel(container, text="Selecione a Versão/Modelo:", 
                     font=ctk.CTkFont(size=14)).pack(pady=(20, 10))
        
        self.model_var = ctk.StringVar(value="Geral")
        self.model_menu = ctk.CTkOptionMenu(container, 
                                            values=OLT_MODELS["Huawei"],
                                            variable=self.model_var,
                                            width=300, height=40)
        self.model_menu.pack(pady=10)

        # Navigation
        self.btn_next = ctk.CTkButton(self, text="Próximo Passo >", 
                                      command=self.next_step,
                                      fg_color=COR_PRINCIPAL, hover_color=COR_HOVER,
                                      width=200, height=45)
        self.btn_next.pack(side="bottom", pady=40)

    def update_models(self, manufacturer):
        models = OLT_MODELS.get(manufacturer, ["Geral"])
        self.model_menu.configure(values=models)
        self.model_var.set(models[0])

    def next_step(self):
        self.controller.selected_manufacturer = self.manufacturer_var.get()
        self.controller.selected_model = self.model_var.get()
        self.controller.show_frame("Step1Frame")
