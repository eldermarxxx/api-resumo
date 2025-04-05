# API de Resumo de PDF com OpenAI

Esta API permite gerar resumos de documentos PDF utilizando o modelo GPT da OpenAI.

## Requisitos

- Python 3.8+
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone o repositório:

```bash
git clone [url-do-repositorio]
cd [nome-do-diretorio]
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure a chave da API da OpenAI:

A chave já está configurada no arquivo `.env`. Caso precise substituir, edite o arquivo e modifique a variável `OPENAI_API_KEY`.

## Executando a API

```bash
python app.py
```

Por padrão, a API será iniciada na porta 5000.

## Endpoints

### GET /status

Verifica se a API está funcionando corretamente.

**Resposta:**
```json
{
  "status": "online"
}
```

### POST /resumir

Recebe a URL de um PDF, baixa o arquivo, extrai o texto e gera um resumo utilizando a OpenAI.

**Corpo da requisição:**
```json
{
  "url": "https://exemplo.com/caminho/para/documento.pdf"
}
```

**Resposta de sucesso:**
```json
{
  "resumo": "Texto do resumo gerado pela OpenAI...",
  "tamanho_original": 12345,
  "tamanho_resumo": 2000
}
```

**Resposta de erro:**
```json
{
  "erro": "Mensagem de erro específica"
}
```

## Exemplo de uso com curl

```bash
curl -X POST http://localhost:5000/resumir \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com/caminho/para/documento.pdf"}'
```

## Exemplo de uso com Python

```python
import requests

url = "http://localhost:5000/resumir"
payload = {
    "url": "https://exemplo.com/caminho/para/documento.pdf"
}

response = requests.post(url, json=payload)
data = response.json()

print(data["resumo"])
```

## Limitações

- A API atualmente suporta apenas documentos PDF
- Para evitar exceder limites de tokens da OpenAI, o texto extraído é limitado a 15.000 caracteres
- O resumo gerado é limitado a 1.000 tokens 