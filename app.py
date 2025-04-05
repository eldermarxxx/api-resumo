import os
import tempfile
import io
import requests
import PyPDF2
import magic
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Inicializar cliente OpenAI com versão compatível
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("AVISO: Chave da API OpenAI não encontrada! Verifique a variável de ambiente OPENAI_API_KEY.")
    
openai_client = OpenAI(api_key=api_key)

def baixar_arquivo(url):
    """Baixa um arquivo a partir de uma URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao baixar o arquivo: {str(e)}")

def verificar_tipo_arquivo(content):
    """Verifica se o conteúdo é um PDF"""
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(content)
    if file_type != 'application/pdf':
        raise Exception(f"O arquivo não é um PDF válido. Tipo detectado: {file_type}")

def extrair_texto_pdf(content):
    """Extrai texto de um arquivo PDF"""
    try:
        with io.BytesIO(content) as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text() + "\n"
        return texto
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

def resumir_texto(texto):
    """Utiliza a API da OpenAI para analisar e resumir extratos bancários"""
    try:
        if len(texto) > 15000:
            texto = texto[:15000]  # Limitar tamanho para evitar tokens excessivos
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """Você é um analista financeiro especializado em extratos bancários.
                    Sua tarefa é analisar extratos bancários e criar relatórios detalhados usando formatação markdown.
                    Identifique e categorize todas as transações, destacando entradas, saídas, tarifas bancárias e outros movimentos relevantes.
                    Faça cálculos precisos de totais e saldos.
                    Ao final, apresente uma avaliação da saúde financeira baseada nos padrões de gastos, receitas e saldo, 
                    com recomendações práticas e específicas para melhorar a gestão financeira."""
                },
                {
                    "role": "user", 
                    "content": f"""Analise detalhadamente o seguinte extrato bancário e crie um relatório completo em formato markdown:

1. Comece com um título e resumo geral das informações do extrato (período, conta, instituição bancária, etc);

2. Detalhe todas as ENTRADAS (créditos, depósitos, transferências recebidas, etc) em uma tabela organizada com data, descrição e valor;

3. Detalhe todas as SAÍDAS (débitos, pagamentos, transferências enviadas, etc) categorizadas (exemplo: alimentação, transporte, moradia) em uma tabela organizada com data, descrição, categoria e valor;

4. Liste todas as TARIFAS bancárias cobradas separadamente;

5. Apresente um RESUMO FINANCEIRO com:
   - Total de entradas
   - Total de saídas
   - Total de tarifas
   - Saldo inicial e final
   - Diferença entre entradas e saídas
   - Maiores despesas por categoria
   - Gráfico de distribuição de gastos (representado em markdown)

6. Finalize com uma ANÁLISE DE SAÚDE FINANCEIRA detalhada que inclua:
   - Indicadores de saúde financeira
   - Pontos positivos identificados
   - Pontos críticos ou de atenção
   - Sugestões práticas e específicas para melhorar a gestão financeira
   - Previsões para os próximos meses se mantido o mesmo padrão

Extrato bancário:
{texto}"""
                }
            ],
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erro ao analisar o extrato bancário com OpenAI: {str(e)}")

@app.route('/', methods=['GET'])
def index():
    """Rota principal com instruções de uso da API"""
    return jsonify({
        "api": "API de Análise de Extratos Bancários com OpenAI",
        "descricao": "Esta API permite analisar extratos bancários em PDF e gerar relatórios detalhados utilizando IA",
        "endpoints": {
            "/status": {
                "metodo": "GET",
                "descricao": "Verifica se a API está funcionando corretamente"
            },
            "/resumir": {
                "metodo": "POST",
                "descricao": "Recebe a URL de um PDF de extrato bancário, baixa o arquivo, extrai o texto e gera uma análise detalhada",
                "parametros": {
                    "url": "URL do arquivo PDF do extrato bancário a ser analisado"
                },
                "exemplo": {
                    "requisicao": {
                        "url": "https://exemplo.com/extrato-bancario.pdf"
                    }
                }
            }
        }
    })

@app.route('/resumir', methods=['POST'])
def resumir_pdf():
    """Endpoint para resumir o conteúdo de um PDF a partir de uma URL"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({"erro": "URL do PDF não fornecida"}), 400
        
        url = data['url']
        
        # Baixar o PDF
        content = baixar_arquivo(url)
        
        # Verificar se é um PDF
        verificar_tipo_arquivo(content)
        
        # Extrair texto do PDF
        texto = extrair_texto_pdf(content)
        
        if not texto or len(texto.strip()) == 0:
            return jsonify({"erro": "Não foi possível extrair texto do PDF"}), 400
        
        # Resumir o texto
        resumo = resumir_texto(texto)
        
        return jsonify({
            "resumo": resumo,
            "tamanho_original": len(texto),
            "tamanho_resumo": len(resumo)
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar o status da API"""
    return jsonify({"status": "online"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7897))
    app.run(host='0.0.0.0', port=port, debug=True) 