import os
import google.generativeai as genai
import re

# Carregar chave da API via variável de ambiente
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""

if not GEMINI_API_KEY:
    raise ValueError("Erro: variável de ambiente GEMINI_API_KEY não está definida")

genai.configure(api_key=GEMINI_API_KEY) # type: ignore
model = genai.GenerativeModel("gemini-2.0-flash") # type: ignore

def extract_plantuml_from_response(response_text: str) -> str:
    pattern = r'@startuml(.*?)@enduml'
    match = re.search(pattern, response_text, re.DOTALL)
    return f"@startuml{match.group(1)}@enduml" if match else ""

def generate_class_diagram(code_path: str = "relogio.py") -> str:
    try:
        with open(code_path, "r") as f:
            code = f.read()

        prompt = f"""
        Gere um diagrama de classes PlantUML completo e preciso para o seguinte código Python.
        Inclua todas as classes, atributos, métodos e relações (herança, composição, etc).
        Use formatação padrão PlantUML e evite explicações textuais extras.

        Código:
        ```python
        {code}
        ```

        Formato esperado:
        @startuml
        ...código PlantUML...
        @enduml
        """

        response = model.generate_content(prompt)

        if response.text:
            return extract_plantuml_from_response(response.text)
        else:
            raise ValueError("Resposta vazia do Gemini")

    except Exception as e:
        print(f"Erro na geração do diagrama: {str(e)}")
        return ""

def save_and_convert_diagram(plantuml_code: str):
    try:
        with open("diagrama_classes.puml", "w") as f:
            f.write(plantuml_code)
        os.system("plantuml diagrama_classes.puml")
        print("Diagrama gerado com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar ou converter o diagrama: {str(e)}")

if __name__ == "__main__":
    plantuml_code = generate_class_diagram()
    if plantuml_code:
        save_and_convert_diagram(plantuml_code)
    else:
        print("Falha na geração do diagrama.")
