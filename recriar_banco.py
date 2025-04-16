import sqlite3
import pandas as pd
import os

def recriar_banco():
    # Remover banco de dados antigo
    if os.path.exists("colaboradores.db"):
        os.remove("colaboradores.db")
    
    # Criar novo banco
    conn = sqlite3.connect("colaboradores.db")
    cursor = conn.cursor()
    
    # Criar tabela com a estrutura correta
    cursor.execute("""
    CREATE TABLE colaboradores (
        Nome TEXT NOT NULL,
        CPF TEXT NOT NULL UNIQUE,
        Numero TEXT,
        Email TEXT,
        foto_path TEXT
    )
    """)
    
    # Se existir backup, restaurar os dados
    if os.path.exists("backup_colaboradores.csv"):
        df = pd.read_csv("backup_colaboradores.csv")
        
        # Preparar os dados para inserção
        for _, row in df.iterrows():
            cursor.execute("""
            INSERT INTO colaboradores (Nome, CPF, Numero, Email, foto_path)
            VALUES (?, ?, ?, ?, ?)
            """, (
                row['Nome'],
                row['CPF'],
                row.get('Numero', None),  # Usar get para evitar erro se a coluna não existir
                row.get('Email', None),
                row.get('foto_path', None)
            ))
    
    conn.commit()
    conn.close()
    
    print("Banco de dados recriado com sucesso!")

if __name__ == "__main__":
    recriar_banco() 