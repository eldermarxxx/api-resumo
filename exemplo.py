import requests
import json

def resumir_pdf(url_pdf):
    """
    Exemplo de como usar a API para resumir um PDF a partir de uma URL
    
    Args:
        url_pdf (str): URL do arquivo PDF
        
    Returns:
        dict: Resposta da API contendo o resumo
    """
    api_url = "http://localhost:5000/resumir"
    
    # Preparar dados para a requisição
    payload = {
        "url": url_pdf
    }
    
    # Enviar requisição POST para a API
    response = requests.post(api_url, json=payload)
    
    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print(f"Erro: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # URL do PDF para resumir
    pdf_url = "https://documentos-gedbahia.s3.sa-east-1.amazonaws.com/1743517388625-330_18032025_1930.pdf"
    
    print("Enviando PDF para resumo...")
    resultado = resumir_pdf(pdf_url)
    
    if resultado:
        print("\n=== RESUMO GERADO ===\n")
        print(resultado["resumo"])
        print("\n=== ESTATÍSTICAS ===")
        print(f"Tamanho do texto original: {resultado['tamanho_original']} caracteres")
        print(f"Tamanho do resumo: {resultado['tamanho_resumo']} caracteres")
        print(f"Taxa de compressão: {100 - (resultado['tamanho_resumo'] / resultado['tamanho_original'] * 100):.2f}%")
    else:
        print("Não foi possível obter o resumo.") 