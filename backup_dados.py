import sqlite3
import pandas as pd

# Fazer backup dos dados existentes
conn = sqlite3.connect("colaboradores.db")
df = pd.read_sql("SELECT * FROM colaboradores", conn)
conn.close()

# Salvar backup
df.to_csv("backup_colaboradores.csv", index=False)

print("Backup realizado com sucesso!") 