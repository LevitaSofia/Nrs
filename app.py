from flask import Flask, render_template, request, jsonify, send_file, url_for
import sqlite3
import pandas as pd
from datetime import datetime
import os
from verificar_cpf import validar_cpf, formatar_cpf
import json
import comtypes.client
import time
import pythoncom
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuração para upload de arquivos
UPLOAD_FOLDER = 'static/img/funcionarios'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar diretório de certificados se não existir
if not os.path.exists('certificados'):
    os.makedirs('certificados')

# Criar diretório para fotos se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Configuração das NRs disponíveis
NRS = {
    "06": {
        "titulo": "NR 06",
        "nome_curso": "Curso sobre uso e guarda de EPI",
        "carga_horaria": "04",
        "modelo": "Certificado - NR06.pptx"
    },
    "12": {
        "titulo": "NR 12",
        "nome_curso": "Curso de Segurança no Trabalho em Máquinas e Equipamentos",
        "carga_horaria": "08",
        "modelo": "Certificado - NR12.pptx"
    },
    "18": {
        "titulo": "NR 18",
        "nome_curso": "Curso de Segurança na Construção Civil",
        "carga_horaria": "16",
        "modelo": "Certificado - NR18.pptx"
    },
    "35": {
        "titulo": "NR 35",
        "nome_curso": "Curso de Trabalho em Altura",
        "carga_horaria": "08",
        "modelo": "Certificado - NR35.pptx"
    }
}


def get_colaboradores():
    conn = sqlite3.connect("colaboradores.db")
    df = pd.read_sql("""
        SELECT 
            rowid as id, 
            Nome as nome, 
            CPF as cpf,
            Numero as numero,
            Email as email,
            foto_path
        FROM colaboradores
    """, conn)
    conn.close()
    return df.to_dict('records')


def converter_para_pdf(pptx_path):
    try:
        if not pptx_path:
            print("Erro: Caminho do arquivo PPTX é None")
            return None

        # Garantir que o caminho seja absoluto
        pptx_path = os.path.abspath(pptx_path)
        print(f"Convertendo arquivo: {pptx_path}")

        if not os.path.exists(pptx_path):
            print(f"Erro: Arquivo PPTX não encontrado em {pptx_path}")
            return None

        # Caminho absoluto para o arquivo PDF
        pdf_path = os.path.splitext(pptx_path)[0] + '.pdf'
        print(f"Caminho do PDF a ser gerado: {pdf_path}")

        # Inicializar COM
        print("Inicializando COM...")
        pythoncom.CoInitialize()

        # Inicializar PowerPoint
        print("Inicializando PowerPoint...")
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = True

        try:
            # Abrir apresentação
            print(f"Abrindo apresentação: {pptx_path}")
            presentation = powerpoint.Presentations.Open(pptx_path)

            # Salvar como PDF
            print(f"Salvando como PDF: {pdf_path}")
            presentation.SaveAs(pdf_path, 32)  # 32 é o código para formato PDF

            # Fechar
            presentation.Close()
            powerpoint.Quit()

            # Verificar se o PDF foi criado
            if os.path.exists(pdf_path):
                print(f"PDF gerado com sucesso: {pdf_path}")
                return pdf_path
            else:
                print(f"Erro: PDF não foi criado em {pdf_path}")
                return None

        except Exception as e:
            print(f"Erro durante a conversão: {str(e)}")
            try:
                presentation.Close()
            except:
                pass
            try:
                powerpoint.Quit()
            except:
                pass
            return None

    except Exception as e:
        print(f"Erro ao converter para PDF: {str(e)}")
        return None
    finally:
        # Desinicializar COM
        try:
            pythoncom.CoUninitialize()
        except:
            pass


@app.route('/')
def index():
    conn = sqlite3.connect('colaboradores.db')
    cursor = conn.cursor()

    # Busca todos os funcionários
    cursor.execute("""
        SELECT rowid, Nome, CPF, Numero, Email, foto_path 
        FROM colaboradores 
        ORDER BY Nome
    """)

    funcionarios = []
    for row in cursor.fetchall():
        funcionarios.append({
            'id': row[0],
            'nome': row[1],
            'cpf': row[2],
            'numero': row[3],
            'email': row[4],
            'foto_path': row[5]
        })

    # Busca as NRs disponíveis
    nrs = {
        '06': {
            'titulo': 'NR 06',
            'nome_curso': 'Curso sobre uso e guarda de EPI',
            'carga_horaria': '04 horas'
        },
        '12': {
            'titulo': 'NR 12',
            'nome_curso': 'Curso de Segurança no Trabalho em Máquinas e Equipamentos',
            'carga_horaria': '08 horas'
        },
        '18': {
            'titulo': 'NR 18',
            'nome_curso': 'Curso de Segurança na Construção Civil',
            'carga_horaria': '16 horas'
        },
        '35': {
            'titulo': 'NR 35',
            'nome_curso': 'Curso de Trabalho em Altura',
            'carga_horaria': '08 horas'
        }
    }

    conn.close()
    return render_template('index.html', funcionarios=funcionarios, nrs=nrs)


@app.route('/gerenciar')
def gerenciar():
    colaboradores = get_colaboradores()
    return render_template('gerenciar.html', funcionarios=colaboradores)


@app.route('/gerenciar/adicionar', methods=['POST'])
def adicionar_funcionario():
    try:
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        numero = request.form.get('numero')
        email = request.form.get('email')
        foto = request.files.get('foto')

        # Validar CPF
        if not validar_cpf(cpf):
            return jsonify({'success': False, 'error': 'CPF inválido'})

        # Formatar CPF
        cpf = formatar_cpf(cpf)

        # Processar foto se fornecida
        foto_path = None
        if foto and allowed_file(foto.filename):
            filename = secure_filename(
                f"{cpf.replace('.', '').replace('-', '')}.{foto.filename.rsplit('.', 1)[1].lower()}")
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(foto_path)
            # Normalizar caminho para URL
            foto_path = foto_path.replace('\\', '/')

        # Inserir no banco de dados
        conn = sqlite3.connect('colaboradores.db')
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO colaboradores (Nome, CPF, Numero, Email, foto_path)
        VALUES (?, ?, ?, ?, ?)
        """, (nome, cpf, numero, email, foto_path))

        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/gerenciar/funcionario/<int:id>')
def get_funcionario(id):
    try:
        conn = sqlite3.connect('colaboradores.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT rowid, Nome, CPF, Numero, Email, foto_path 
            FROM colaboradores 
            WHERE rowid = ?
        """, (id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            funcionario = {
                'id': row[0],
                'nome': row[1],
                'cpf': row[2],
                'numero': row[3],
                'email': row[4],
                'foto_path': row[5]
            }
            return jsonify({'success': True, 'funcionario': funcionario})
        else:
            return jsonify({'success': False, 'error': 'Funcionário não encontrado'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/gerenciar/atualizar/<int:id>', methods=['POST'])
def atualizar_funcionario(id):
    try:
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        numero = request.form.get('numero')
        email = request.form.get('email')
        foto = request.files.get('foto')

        # Validar CPF
        if not validar_cpf(cpf):
            return jsonify({'success': False, 'error': 'CPF inválido'})

        # Formatar CPF
        cpf = formatar_cpf(cpf)

        conn = sqlite3.connect('colaboradores.db')
        cursor = conn.cursor()

        # Obter foto atual
        cursor.execute(
            "SELECT foto_path FROM colaboradores WHERE rowid = ?", (id,))
        atual_foto_path = cursor.fetchone()[0]

        # Processar nova foto se fornecida
        foto_path = atual_foto_path
        if foto and allowed_file(foto.filename):
            # Remover foto antiga se existir
            if atual_foto_path and os.path.exists(atual_foto_path):
                os.remove(atual_foto_path)

            filename = secure_filename(
                f"{cpf.replace('.', '').replace('-', '')}.{foto.filename.rsplit('.', 1)[1].lower()}")
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(foto_path)
            # Normalizar caminho para URL
            foto_path = foto_path.replace('\\', '/')

        # Atualizar no banco de dados
        cursor.execute("""
        UPDATE colaboradores 
        SET Nome = ?, CPF = ?, Numero = ?, Email = ?, foto_path = ?
        WHERE rowid = ?
        """, (nome, cpf, numero, email, foto_path, id))

        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/gerenciar/excluir/<int:id>', methods=['POST'])
def excluir_funcionario(id):
    try:
        conn = sqlite3.connect('colaboradores.db')
        cursor = conn.cursor()

        # Obter foto atual
        cursor.execute(
            "SELECT foto_path FROM colaboradores WHERE rowid = ?", (id,))
        foto_path = cursor.fetchone()[0]

        # Remover foto se existir
        if foto_path and os.path.exists(foto_path):
            os.remove(foto_path)

        # Remover do banco de dados
        cursor.execute("DELETE FROM colaboradores WHERE rowid = ?", (id,))

        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/gerar_certificado', methods=['POST'])
def gerar_certificado():
    try:
        data = request.json
        colaborador_id = data.get('colaborador_id')
        nr = data.get('nr')
        data_ministerio = data.get('data_ministerio')

        print(
            f"Recebida requisição para gerar certificado - Colaborador ID: {colaborador_id}, NR: {nr}, Data: {data_ministerio}")

        # Verificar se os dados necessários foram fornecidos
        if not colaborador_id or not nr or not data_ministerio:
            return jsonify({'error': 'Dados incompletos'}), 400

        # Buscar dados do colaborador
        conn = sqlite3.connect("colaboradores.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Nome, CPF FROM colaboradores WHERE rowid = ?", (colaborador_id,))
        colaborador = cursor.fetchone()
        conn.close()

        if not colaborador:
            return jsonify({'error': 'Colaborador não encontrado'}), 404

        print(f"Dados do colaborador encontrados: {colaborador}")

        # Importar o módulo de geração de certificados
        import gerar_certificado

        # Criar o certificado PowerPoint
        pptx_arquivo = gerar_certificado.gerar_certificado({
            'Nome': colaborador[0],
            'CPF': colaborador[1]
        }, {
            'numero': nr,
            'modelo': NRS[nr]['modelo'],
            'data_ministerio': data_ministerio
        })

        print(f"Arquivo PPTX gerado: {pptx_arquivo}")

        if not pptx_arquivo:
            return jsonify({'error': 'Falha ao gerar o arquivo PPTX'}), 500

        # Verificar se o arquivo PPTX existe
        if not os.path.exists(pptx_arquivo):
            print(f"Erro: Arquivo PPTX não encontrado em {pptx_arquivo}")
            return jsonify({'error': 'Arquivo PPTX não encontrado'}), 500

        # Converter para PDF
        pdf_arquivo = converter_para_pdf(pptx_arquivo)

        if pdf_arquivo:
            print(f"PDF gerado com sucesso: {pdf_arquivo}")
            return jsonify({
                'success': True,
                'message': 'Certificado gerado com sucesso!',
                'arquivo_pptx': pptx_arquivo,
                'arquivo_pdf': pdf_arquivo
            })
        else:
            print("Erro na conversão para PDF")
            return jsonify({
                'success': True,
                'message': 'Certificado PowerPoint gerado com sucesso, mas houve erro na conversão para PDF',
                'arquivo_pptx': pptx_arquivo
            })

    except Exception as e:
        print(f"Erro ao gerar certificado: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>')
def download(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/gerenciar/atualizar_foto/<int:id>', methods=['POST'])
def atualizar_foto(id):
    try:
        if 'foto' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhuma foto enviada'})

        foto = request.files['foto']
        if not foto or not allowed_file(foto.filename):
            return jsonify({'success': False, 'error': 'Arquivo inválido'})

        conn = sqlite3.connect('colaboradores.db')
        cursor = conn.cursor()

        # Obter CPF do funcionário para nomear o arquivo
        cursor.execute(
            "SELECT CPF, foto_path FROM colaboradores WHERE rowid = ?", (id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({'success': False, 'error': 'Funcionário não encontrado'})

        cpf, atual_foto_path = result

        # Remover foto antiga se existir
        if atual_foto_path and os.path.exists(atual_foto_path):
            try:
                os.remove(atual_foto_path)
            except Exception as e:
                print(f"Erro ao remover foto antiga: {e}")

        # Criar diretório se não existir
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Salvar nova foto
        filename = secure_filename(
            f"{cpf.replace('.', '').replace('-', '')}.{foto.filename.rsplit('.', 1)[1].lower()}")
        foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        foto.save(foto_path)
        foto_path = foto_path.replace('\\', '/')  # Normalizar caminho para URL

        # Atualizar caminho no banco de dados
        cursor.execute("""
        UPDATE colaboradores 
        SET foto_path = ?
        WHERE rowid = ?
        """, (foto_path, id))

        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        print(f"Erro ao atualizar foto: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/gerenciar/excluir_foto/<int:id>', methods=['POST'])
def excluir_foto(id):
    try:
        conn = sqlite3.connect('colaboradores.db')
        cursor = conn.cursor()

        # Obter caminho da foto atual
        cursor.execute(
            "SELECT foto_path FROM colaboradores WHERE rowid = ?", (id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'success': False, 'error': 'Funcionário não encontrado'})

        foto_path = result[0]

        # Remover foto se existir
        if foto_path and os.path.exists(foto_path):
            os.remove(foto_path)

        # Atualizar banco de dados
        cursor.execute("""
        UPDATE colaboradores 
        SET foto_path = NULL
        WHERE rowid = ?
        """, (id,))

        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
