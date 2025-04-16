# Sistema de Geração de Certificados NR

Sistema para geração de certificados de treinamento NR (Normas Regulamentadoras) para colaboradores da Alta Telas.

## Funcionalidades

- Gerenciamento de colaboradores
- Upload de fotos dos colaboradores
- Geração de certificados em formato PPTX e PDF
- Suporte para múltiplas NRs (06, 12, 18, 35)

## Requisitos

- Python 3.8+
- Flask
- pandas
- comtypes (para conversão PPTX para PDF)
- Microsoft PowerPoint (para conversão de arquivos)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd [NOME_DO_REPOSITÓRIO]
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Inicialize o banco de dados:
```bash
python banco.py
```

## Executando o Projeto

1. Ative o ambiente virtual (se ainda não estiver ativo):
```bash
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

2. Execute o servidor Flask:
```bash
python app.py
```

3. Acesse o sistema no navegador:
```
http://localhost:5000
```

## Estrutura do Projeto

```
├── app.py                  # Aplicação principal Flask
├── banco.py                # Script de inicialização do banco de dados
├── gerar_certificado.py    # Lógica de geração de certificados
├── verificar_cpf.py        # Validação de CPF
├── static/                 # Arquivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
├── templates/              # Templates HTML
├── certificados/           # Certificados gerados
└── colaboradores.db        # Banco de dados SQLite
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença [MIT](LICENSE). 