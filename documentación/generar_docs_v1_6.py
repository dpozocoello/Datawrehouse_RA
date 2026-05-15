import os
import markdown
import sys

def convert_md_to_doc(md_file_path):
    """
    Convierte un archivo Markdown a un HTML compatible con Word (.doc).
    """
    try:
        if not os.path.exists(md_file_path):
            print(f"File not found: {md_file_path}")
            return

        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convertir MD a HTML
        # Nota: Word interpreta bien el HTML básico si se guarda con .doc
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])

        # Estilización básica para Word (Inter, tablas con bordes, etc.)
        doc_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
                h2 {{ color: #2980b9; margin-top: 30px; border-bottom: 1px solid #ddd; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                code {{ background-color: #f8f9fa; color: #e83e8c; padding: 2px 4px; border-radius: 4px; font-family: 'Courier New', Courier, monospace; }}
                pre {{ background-color: #f8f9fa; padding: 15px; border-left: 5px solid #2980b9; border-radius: 4px; overflow-x: auto; }}
                blockquote {{ border-left: 5px solid #ccc; margin: 20px 0; padding: 10px 20px; color: #666; font-style: italic; background: #f9f9f9; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        output_path = md_file_path.replace('.md', '.doc')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc_html)
        
        print(f"Successfully converted: {os.path.basename(output_path)}")

    except Exception as e:
        print(f"Error converting {md_file_path}: {e}")

def main():
    docs_dir = r"D:\Datawrehouse_RA\documentación"
    files_to_convert = [
        "DWH_Arquitectura_Integral_v1_6.md",
        "DWH_Diccionario_Tecnico_Datos_v1_6.md",
        "DWH_Especificacion_Tecnica_Maestra_v1_6.md",
        "DWH_Matriz_Mapeo_Origen_Destino_v1_6.md",
        "ETL_Ecosistema_Hibrido_Sistemas_v1_6.md",
        "Manual_Uso_DWH_Analitica_v1_6.md",
        "DWH_Catalogo_Scripts_SQL_v1_6.md",
        "Informe_Ejecucion_Arquitectura_v1_6.md",
        "DWH_Evaluacion_Registro_Generador_v1_6.md"
    ]

    print("\n" + "="*50)
    print("CONVERSOR MAESTRO DE DOCUMENTACIÓN v1.6")
    print("="*50)

    for doc in files_to_convert:
        path = os.path.join(docs_dir, doc)
        convert_md_to_doc(path)

    print("="*50 + "\n")

if __name__ == "__main__":
    main()
