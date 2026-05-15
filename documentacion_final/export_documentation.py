import os

def export_to_html():
    input_file = r"d:\Datawrehouse_RA\documentación\DWH_RGD_Consolidated_Documentation.md"
    output_file = r"d:\Datawrehouse_RA\documentación\DWH_Documentacion_Final.html"
    
    if not os.path.exists(input_file):
        print(f"Error: No se encuentra el archivo de entrada {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Simple Markdown to HTML conversion logic (Basic for documentation)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Documentación Data Warehouse RA</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: auto; padding: 40px; }}
            h1, h2, h3 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
            pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; border: 1px solid #ddd; }}
            code {{ font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace; color: #d63384; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f8f9fa; }}
            .page-break {{ page-break-before: always; }}
            .signatures {{ margin-top: 50px; display: flex; justify-content: space-between; }}
            .sig-box {{ border-top: 1px solid #000; width: 30%; text-align: center; padding-top: 10px; }}
        </style>
    </head>
    <body>
        {md_content.replace("# ", "<h1>").replace("## ", "<h2>").replace("### ", "<h3>").replace("#### ", "<h4>").replace("\n", "<br>")}
        <div class="page-break"></div>
        <h2>Firmas de Responsabilidad</h2>
        <div class="signatures">
            <div class="sig-box">Elaborado por:<br>Ingeniería de Datos</div>
            <div class="sig-box">Revisado por:<br>Arquitectura de Datos</div>
            <div class="sig-box">Aprobado por:<br>Gerencia de TI</div>
        </div>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"SUCCESS: Documento consolidado generado en: {output_file}")
    print("Sugerencia: Abra el archivo .html en su navegador y use Ctrl+P para guardar como PDF.")

if __name__ == "__main__":
    export_to_html()
