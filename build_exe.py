import PyInstaller.__main__
import customtkinter
import os
import sys

# Obtém o caminho da instalação do customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

# Define o separador de caminho (ponto e vírgula para Windows)
separator = ';' if os.name == 'nt' else ':'

print("Iniciando a criação do executável...")
print(f"Biblioteca CustomTkinter encontrada em: {ctk_path}")

PyInstaller.__main__.run([
    'main.py',                        # Seu arquivo principal
    '--name=MigradorOLT',             # Nome do executável final
    '--onefile',                      # Cria um único arquivo .exe (não uma pasta)
    '--noconsole',                    # Não abre a tela preta do terminal (apenas a GUI)
    f'--add-data={ctk_path}{separator}customtkinter', # Inclui os arquivos do tema
    '--clean',                        # Limpa cache de builds anteriores
])

print("\nProcesso finalizado! Verifique a pasta 'dist'.")
