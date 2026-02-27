import sqlite3
import os
from app.core.config import get_app_path, TEMPLATES_PADRAO

class Database:
    def __init__(self):
        self.db_path = os.path.join(get_app_path(), "olt_data.db")
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create templates table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE,
                    conteudo TEXT,
                    fabricante TEXT,
                    modelo TEXT,
                    is_padrao INTEGER DEFAULT 0
                )
            ''')
            
            # Migration: Ensure all columns exist individually
            def add_column(col_def):
                try:
                    cursor.execute(f"ALTER TABLE templates ADD COLUMN {col_def}")
                except sqlite3.OperationalError:
                    pass

            add_column("fabricante TEXT DEFAULT 'Huawei'")
            add_column("modelo TEXT DEFAULT 'Geral'")
            add_column("is_padrao INTEGER DEFAULT 0")

            # Table for App Configurations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configs (
                    chave TEXT PRIMARY KEY,
                    valor TEXT
                )
            ''')
            
            # Table for Migration Logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS migration_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    slot TEXT,
                    pon TEXT,
                    serial_count INTEGER,
                    filename TEXT,
                    fabricante TEXT DEFAULT 'Huawei',
                    modelo TEXT DEFAULT 'Geral'
                )
            ''')
            
            # Migration for existing migration_logs table
            def add_log_column(col_def):
                try:
                    cursor.execute(f"ALTER TABLE migration_logs ADD COLUMN {col_def}")
                except sqlite3.OperationalError:
                    pass
            
            add_log_column("fabricante TEXT DEFAULT 'Huawei'")
            add_log_column("modelo TEXT DEFAULT 'Geral'")
            
            # Seed initial templates or update them to be system scripts
            for fabricante, modelos in TEMPLATES_PADRAO.items():
                for modelo, templates in modelos.items():
                    for nome, conteudo in templates.items():
                        cursor.execute("""
                            INSERT OR REPLACE INTO templates (nome, conteudo, is_padrao, fabricante, modelo) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (nome, conteudo, 1, fabricante, modelo))
            
            conn.commit()

    # --- Template Operations ---
    def get_templates(self, fabricante=None, modelo=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT nome, conteudo, is_padrao FROM templates"
            params = []
            if fabricante and modelo:
                query += " WHERE fabricante = ? AND modelo = ?"
                params = [fabricante, modelo]
            
            cursor.execute(query, params)
            return {row[0]: {"content": row[1], "is_default": bool(row[2])} for row in cursor.fetchall()}

    def save_template(self, nome, conteudo, fabricante, modelo, is_default=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO templates (nome, conteudo, is_padrao, fabricante, modelo) 
                VALUES (?, ?, ?, ?, ?)
            """, (nome, conteudo, is_default, fabricante, modelo))
            conn.commit()

    def delete_template(self, nome):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM templates WHERE nome = ? AND is_padrao = 0", (nome,))
            conn.commit()

    # --- Config Operations ---
    def get_config(self, chave, default=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT valor FROM configs WHERE chave = ?", (chave,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_config(self, chave, valor):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO configs (chave, valor) VALUES (?, ?)", (chave, valor))
            conn.commit()

    # --- Log Operations ---
    def add_log(self, slot, pon, serial_count, filename, fabricante, modelo):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO migration_logs (slot, pon, serial_count, filename, fabricante, modelo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (slot, pon, serial_count, filename, fabricante, modelo))
            conn.commit()

    def get_logs(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, slot, pon, serial_count, filename, fabricante, modelo FROM migration_logs ORDER BY timestamp DESC")
            return cursor.fetchall()
            
    def delete_log(self, log_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM migration_logs WHERE id = ?", (log_id,))
            conn.commit()
