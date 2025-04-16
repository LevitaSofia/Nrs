import sqlite3

def criar_banco():
    # Conectar ao banco
    conn = sqlite3.connect("colaboradores.db")
    cursor = conn.cursor()
    
    # Criar tabela com todos os campos necessários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        Nome TEXT NOT NULL,
        CPF TEXT NOT NULL UNIQUE,
        Numero TEXT,
        Email TEXT,
        foto_path TEXT
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    criar_banco()
    
    try:
        import pandas as pd
        
        # Conectar ao banco
        conn = sqlite3.connect("colaboradores.db")
        
        # Consultar todos os dados
        df = pd.read_sql("SELECT * FROM colaboradores", conn)
        print("\nColaboradores cadastrados:")
        print(df)
        
    except ModuleNotFoundError:
        print("O módulo pandas não está instalado.")
        print("Por favor, instale usando: pip install pandas")
        exit(1)
