import sqlite3
import pandas as pd
import re
from verificar_cpf import validar_cpf, formatar_cpf
import os
import shutil

def criar_tabela():
    try:
        conn = sqlite3.connect("colaboradores.db")
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS colaboradores (
            Nome TEXT NOT NULL,
            CPF TEXT UNIQUE NOT NULL,
            Numero TEXT,
            Email TEXT,
            foto_path TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")

def listar_colaboradores():
    try:
        conn = sqlite3.connect("colaboradores.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT rowid, Nome, CPF, Numero, Email, foto_path FROM colaboradores")
        colaboradores = cursor.fetchall()
        
        print("\nLista de Colaboradores:")
        print("ID  | Nome                           | CPF            | Número | Email | Foto")
        print("-" * 70)
        
        for col in colaboradores:
            foto_status = "Sim" if col[5] else "Não"
            print(f"{col[0]:<4} | {col[1]:<30} | {col[2]:<14} | {col[3] if col[3] else 'Não informado':<8} | {col[4] if col[4] else 'Não informado':<30} | {foto_status}")
            
    except Exception as e:
        print(f"\nErro ao listar colaboradores: {str(e)}")
    finally:
        conn.close()

def adicionar_colaborador(nome, cpf, foto_path=None):
    # Validar CPF
    if not validar_cpf(cpf):
        print("CPF inválido!")
        return False
    
    # Formatar CPF
    cpf = formatar_cpf(cpf)
    
    try:
        conn = sqlite3.connect("colaboradores.db")
        cursor = conn.cursor()
        
        # Se uma foto foi fornecida, copiar para a pasta de fotos
        foto_final_path = None
        if foto_path and os.path.exists(foto_path):
            # Criar diretório de fotos se não existir
            if not os.path.exists("static/img/funcionarios"):
                os.makedirs("static/img/funcionarios")
            
            # Gerar nome do arquivo baseado no CPF
            extensao = os.path.splitext(foto_path)[1]
            novo_nome = f"static/img/funcionarios/{cpf.replace('.', '').replace('-', '')}{extensao}"
            
            # Copiar a foto
            shutil.copy2(foto_path, novo_nome)
            foto_final_path = novo_nome
        
        # Inserir no banco de dados
        cursor.execute("""
        INSERT INTO colaboradores (Nome, CPF, Numero, Email, foto_path)
        VALUES (?, ?, ?, ?, ?)
        """, (nome, cpf, None, None, foto_final_path))
        
        conn.commit()
        print(f"\nColaborador {nome} adicionado com sucesso!")
        return True
        
    except sqlite3.IntegrityError:
        print("\nErro: CPF já cadastrado!")
        return False
    except Exception as e:
        print(f"\nErro ao adicionar colaborador: {str(e)}")
        return False
    finally:
        conn.close()

def alterar_colaborador():
    listar_colaboradores()
    
    while True:
        try:
            id_colaborador = int(input("\nDigite o ID do colaborador que deseja alterar (0 para cancelar): "))
            if id_colaborador == 0:
                return
                
            conn = sqlite3.connect("colaboradores.db")
            cursor = conn.cursor()
            
            # Verificar se colaborador existe
            cursor.execute("SELECT * FROM colaboradores WHERE rowid = ?", (id_colaborador,))
            colaborador = cursor.fetchone()
            
            if not colaborador:
                print("Colaborador não encontrado!")
                conn.close()
                continue
            
            print("\nDados atuais:")
            print(f"1. Nome: {colaborador[0]}")
            print(f"2. CPF: {colaborador[1]}")
            print(f"3. Número: {colaborador[2] if colaborador[2] else 'Não informado'}")
            print(f"4. Email: {colaborador[3] if colaborador[3] else 'Não informado'}")
            print("5. Cancelar alteração")
            
            campo = input("\nQual campo deseja alterar? ")
            
            if campo == "5":
                conn.close()
                return
            
            if campo == "1":
                novo_valor = input("Novo nome: ").strip().upper()
                if not novo_valor:
                    print("Nome não pode ficar em branco!")
                    continue
                cursor.execute("UPDATE colaboradores SET Nome = ? WHERE rowid = ?", (novo_valor, id_colaborador))
                
            elif campo == "2":
                novo_cpf = input("Novo CPF (apenas números): ").strip()
                cpf_numerico = re.sub(r'[^0-9]', '', novo_cpf)
                
                if len(cpf_numerico) != 11:
                    print("CPF deve ter 11 dígitos!")
                    continue
                    
                if not validar_cpf(cpf_numerico):
                    print("CPF inválido!")
                    continue
                    
                cpf_formatado = formatar_cpf(cpf_numerico)
                cursor.execute("UPDATE colaboradores SET CPF = ? WHERE rowid = ?", (cpf_formatado, id_colaborador))
                
            elif campo == "3":
                novo_valor = input("Novo número: ").strip()
                cursor.execute("UPDATE colaboradores SET Numero = ? WHERE rowid = ?", 
                             (novo_valor if novo_valor else None, id_colaborador))
                
            elif campo == "4":
                novo_valor = input("Novo email: ").strip()
                cursor.execute("UPDATE colaboradores SET Email = ? WHERE rowid = ?", 
                             (novo_valor if novo_valor else None, id_colaborador))
                
            else:
                print("Opção inválida!")
                continue
            
            conn.commit()
            print("\nDados atualizados com sucesso!")
            break
            
        except ValueError:
            print("Por favor, digite um número válido!")
        except sqlite3.IntegrityError:
            print("Erro: CPF já cadastrado para outro colaborador!")
        except Exception as e:
            print(f"Erro ao alterar dados: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

def excluir_colaborador():
    listar_colaboradores()
    
    while True:
        try:
            id_colaborador = int(input("\nDigite o ID do colaborador que deseja excluir (0 para cancelar): "))
            if id_colaborador == 0:
                return
                
            conn = sqlite3.connect("colaboradores.db")
            cursor = conn.cursor()
            
            # Verificar se colaborador existe
            cursor.execute("SELECT Nome FROM colaboradores WHERE rowid = ?", (id_colaborador,))
            colaborador = cursor.fetchone()
            
            if not colaborador:
                print("Colaborador não encontrado!")
                conn.close()
                continue
            
            confirmacao = input(f"\nTem certeza que deseja excluir o colaborador {colaborador[0]}? (S/N) ")
            if confirmacao.upper() != 'S':
                print("Operação cancelada!")
                conn.close()
                return
            
            cursor.execute("DELETE FROM colaboradores WHERE rowid = ?", (id_colaborador,))
            conn.commit()
            print("\nColaborador excluído com sucesso!")
            break
            
        except ValueError:
            print("Por favor, digite um número válido!")
        except Exception as e:
            print(f"Erro ao excluir colaborador: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

def main():
    criar_tabela()
    
    while True:
        print("\nGerenciamento de Colaboradores")
        print("=" * 30)
        print("1. Listar colaboradores")
        print("2. Adicionar novo colaborador")
        print("3. Alterar dados de colaborador")
        print("4. Excluir colaborador")
        print("5. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            listar_colaboradores()
        elif opcao == "2":
            nome = input("Nome do colaborador: ")
            cpf = input("CPF do colaborador: ")
            foto = input("Caminho da foto (opcional, pressione Enter para pular): ").strip()
            
            if foto and not os.path.exists(foto):
                print("Arquivo de foto não encontrado!")
                continue
                
            adicionar_colaborador(nome, cpf, foto if foto else None)
        elif opcao == "3":
            alterar_colaborador()
        elif opcao == "4":
            excluir_colaborador()
        elif opcao == "5":
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main() 