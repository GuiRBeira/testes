import ast
import os
import sys

def parse_python_for_class_diagram(code_path: str) -> str:
    """
    Analisa um arquivo Python para extrair informações de classes, atributos e métodos,
    gerando uma string PlantUML correspondente.
    """
    try:
        with open(code_path, "r", encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        return f"Erro: Arquivo não encontrado em {code_path}"

    tree = ast.parse(code)
    plantuml_elements = []
    plantuml_relationships = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            class_attributes = []
            class_methods = []
            inherited_classes = []

            # Extrair classes herdadas
            for base in node.bases:
                if isinstance(base, ast.Name):
                    inherited_classes.append(base.id)
                elif isinstance(base, ast.Attribute):
                    # Lida com herança de classes de outros módulos (ex: 'module.ClassName')
                    # Esta parte é complexa e pode não capturar todos os casos.
                    try:
                        inherited_classes.append(f"{base.value.id}.{base.attr}")
                    except AttributeError:
                        # Ignora casos mais complexos que o parser simples não lida
                        pass

            # Analisar o corpo da classe para atributos e métodos
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    # Inferência básica de visibilidade
                    if method_name.startswith('__') and not method_name.endswith('__'):
                        visibility = '-'
                    elif method_name.startswith('_'):
                        visibility = '#'
                    else:
                        visibility = '+'
                    class_methods.append(f"  {visibility}{method_name}()")
                elif isinstance(item, ast.Assign):
                    # Tenta pegar atributos de classe
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            attr_name = target.id
                            if f"  +{attr_name}" not in class_attributes:
                                class_attributes.append(f"  +{attr_name}")

            # Formata a classe para PlantUML
            class_body_lines = []
            if class_attributes:
                class_body_lines.extend(sorted(class_attributes))
                class_body_lines.append("  --")
            if class_methods:
                class_body_lines.extend(sorted(class_methods))
            
            # CORREÇÃO: Usa '\n' em vez de ';\\n' para juntar as linhas
            joined_class_body = '\n'.join(class_body_lines)
            plantuml_elements.append(f"class {class_name} {{\n{joined_class_body}\n}}")

            # Adiciona relações de herança
            for inherited_class in inherited_classes:
                plantuml_relationships.append(f"{inherited_class} <|-- {class_name}")

    if not plantuml_elements:
        return "Nenhuma classe encontrada no código fornecido."

    # --- CORREÇÃO GERAL APLICADA ABAIXO ---
    # Substituído '\\n' por '\n' para criar quebras de linha reais.
    full_plantuml = "@startuml\n"
    full_plantuml += "skinparam classAttributeIconSize 0\n" # Melhora a aparência
    full_plantuml += "skinparam linetype ortho\n\n"
    
    full_plantuml += "\n\n".join(plantuml_elements)
    if plantuml_relationships:
        full_plantuml += "\n\n" + "\n".join(plantuml_relationships)
    full_plantuml += "\n@enduml"

    return full_plantuml

def save_and_render_diagram(plantuml_code: str, output_puml_file: str = "diagrama_classes_manual.puml"):
    """
    Salva o código PlantUML em um arquivo e tenta renderizá-lo em imagem.
    """
    if not plantuml_code or "Erro:" in plantuml_code:
        print(f"Código PlantUML inválido ou erro na análise: {plantuml_code}")
        return

    try:
        with open(output_puml_file, "w", encoding='utf-8') as f:
            f.write(plantuml_code)
        print(f"Código PlantUML salvo em {output_puml_file}")

        print("Renderizando imagem com PlantUML...")
        os.system(f"plantuml {output_puml_file}")

        output_png_file = output_puml_file.replace(".puml", ".png")
        if not os.path.exists(output_png_file):
            print(f"AVISO: O arquivo de imagem '{output_png_file}' NÃO foi gerado.")
            print("Verifique se o PlantUML e o Graphviz estão instalados corretamente no ambiente do Actions.")

    except Exception as e:
        print(f"Erro ao salvar ou renderizar o diagrama: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_file_name = sys.argv[1]
    else:
        # Altere aqui para o arquivo padrão que você quer analisar, se nenhum for passado
        target_file_name = "sistema_zoologico_galactico.py" 

    print(f"Analisando o arquivo: {target_file_name}")
    plantuml_output = parse_python_for_class_diagram(target_file_name)

    if plantuml_output and "Nenhuma classe encontrada" not in plantuml_output:
        print("\n--- Código PlantUML Gerado ---")
        print(plantuml_output)
        save_and_render_diagram(plantuml_output)
    else:
        print(plantuml_output)

