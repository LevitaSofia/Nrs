import sqlite3
import pandas as pd
import re

def validar_cpf(cpf):
    # Remover caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verificar se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verificar se todos os dígitos são iguais
    if len(set(cpf)) == 1:
        return False
    
    # Validar primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    if int(cpf[9]) != digito1:
        return False
    
    # Validar segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    if int(cpf[10]) != digito2:
        return False
    
    return True

def formatar_cpf(cpf):
    # Remover caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Formatar CPF (XXX.XXX.XXX-XX)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def verificar_cpfs_banco():
    try:
        # Conectar ao banco
        conn = sqlite3.connect("colaboradores.db")
        df = pd.read_sql("SELECT rowid, Nome, CPF FROM colaboradores", conn)
        conn.close()
        
        print("\nVerificando CPFs no banco de dados:")
        print("=" * 50)
        
        for _, row in df.iterrows():
            cpf = row['CPF']
            nome = row['Nome']
            cpf_numerico = re.sub(r'[^0-9]', '', cpf)
            
            print(f"\nColaborador: {nome}")
            print(f"CPF Original: {cpf}")
            
            if len(cpf_numerico) != 11:
                print("Status: ERRO - CPF não tem 11 dígitos")
                print(f"Sugestão: Verifique se o CPF está completo")
            else:
                cpf_formatado = formatar_cpf(cpf_numerico)
                if validar_cpf(cpf_numerico):
                    print("Status: VÁLIDO")
                    if cpf != cpf_formatado:
                        print(f"Sugestão de formatação: {cpf_formatado}")
                else:
                    print("Status: INVÁLIDO - Dígitos verificadores incorretos")
                    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")

def testar_cpf_individual():
    while True:
        cpf = input("\nDigite um CPF para testar (ou 'sair' para encerrar): ")
        
        if cpf.lower() == 'sair':
            break
        
        cpf_numerico = re.sub(r'[^0-9]', '', cpf)
        
        print(f"\nCPF Informado: {cpf}")
        
        if len(cpf_numerico) != 11:
            print("Status: ERRO - CPF não tem 11 dígitos")
            print(f"Quantidade atual: {len(cpf_numerico)} dígitos")
        else:
            cpf_formatado = formatar_cpf(cpf_numerico)
            if validar_cpf(cpf_numerico):
                print("Status: VÁLIDO")
                print(f"Formatação correta: {cpf_formatado}")
            else:
                print("Status: INVÁLIDO - Dígitos verificadores incorretos")

def main():
    while True:
        print("\nVerificador de CPF")
        print("=" * 30)
        print("1. Verificar todos os CPFs do banco de dados")
        print("2. Testar um CPF específico")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            verificar_cpfs_banco()
        elif opcao == "2":
            testar_cpf_individual()
        elif opcao == "3":
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main() 