import os
import sys
import google.generativeai as genai
import re

def extract_plantuml_from_response(response_text: str) -> str:
    """
    Usa regex para extrair o bloco de código PlantUML da resposta da IA.
    Isso é útil para limpar textos extras como "Aqui está o diagrama...".
    """
    # O padrão procura por qualquer texto entre @startuml e @enduml, em múltiplas linhas
    pattern = r'@startuml(.*?)@enduml'
    match = re.search(pattern, response_text, re.DOTALL)
    
    # Se encontrar, reconstrói o bloco completo e limpo
    return f"@startuml{match.group(1).strip()}\n@enduml" if match else ""

def generate_class_diagram(code_path: str) -> str:
    """
    Lê o código de um arquivo, envia para a API Gemini e retorna a definição do diagrama.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Erro: A variável de ambiente GEMINI_API_KEY não está definida.")

    genai.configure(api_key=api_key)
    
    # CORREÇÃO: Ajustado para um nome de modelo válido e eficiente para a tarefa.
    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        with open(code_path, "r", encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Erro Crítico: Arquivo de código '{code_path}' não foi encontrado.")
        return ""

    prompt = f"""
    Gere um diagrama de classes PlantUML completo e preciso para o seguinte código Python.

    Regras Importantes:
    1. Inclua todas as classes, seus atributos e métodos.
    2. Mostre as relações de herança.
    3. Sua resposta deve conter APENAS o bloco de código PlantUML, começando com `@startuml` e terminando com `@enduml`. Não inclua nenhuma outra palavra, explicação ou formatação markdown como ```plantuml.

    Código para Análise:
    ```python
    {code}
    ```
    """

    try:
        response = model.generate_content(prompt)
        if response.text:
            return extract_plantuml_from_response(response.text)
        else:
            raise ValueError("A resposta da API Gemini estava vazia.")
    except Exception as e:
        print(f"Erro ao comunicar com a API Gemini: {e}")
        return ""

def save_and_render_diagram(plantuml_code: str):
    """
    Salva o código PlantUML em um arquivo e tenta renderizá-lo para PNG.
    """
    output_puml_file = "diagrama_classes.puml"
    try:
        with open(output_puml_file, "w", encoding='utf-8') as f:
            f.write(plantuml_code)
        print(f"Definição do diagrama salva em '{output_puml_file}'.")
        
        # Executa o PlantUML para gerar a imagem
        print(f"Renderizando '{output_puml_file}' para imagem...")
        os.system(f"plantuml {output_puml_file}")

    except Exception as e:
        print(f"Erro ao salvar ou renderizar o diagrama: {e}")

if __name__ == "__main__":
    # MELHORIA: O script agora aceita um nome de arquivo como argumento.
    # Se nenhum for passado, ele usa 'relogio.py' como padrão.
    if len(sys.argv) > 1:
        target_file_path = sys.argv[1]
    else:
        target_file_path = "relogio.py"

    print(f"Iniciando geração de diagrama para o arquivo: '{target_file_path}'")
    plantuml_code = generate_class_diagram(target_file_path)

    if plantuml_code:
        save_and_render_diagram(plantuml_code)
        print("Processo finalizado com sucesso.")
    else:
        print("Falha na geração do diagrama. Verifique os logs de erro acima.")
        # Sai com erro para que o workflow do GitHub Actions possa detectar a falha.
        sys.exit(1)
