import shutil
import gradio as gr
import os
import fitz
import json

def get_text_percentage(file_name: str) -> float:
    """
    Calculate the percentage of document that is covered by (searchable) text.

    If the returned percentage of text is very low, the document is
    most likely a scanned PDF.
    """
    total_page_area = 0.0
    total_text_area = 0.0

    doc = fitz.open(file_name)

    for page_num, page in enumerate(doc):
        total_page_area += abs(page.rect)
        text_area = 0.0
        text_blocks = page.get_text("blocks")
        for block in text_blocks:
            # Each block is a tuple where the first four elements are the rectangle coordinates
            r = fitz.Rect(block[:4])  # Create a rectangle for the text block
            text_area += abs(r)
        total_text_area += text_area

    doc.close()
    return (total_text_area / total_page_area) if total_page_area else 0

def copy_files_to_folder(files, client, invoice_type):

    client_value = client
    invoice_type_value = invoice_type

    if client == "MMJ" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\MMJ_IMPO"
    if client == "MMJ" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\MMJ_EXPO"
    if client == "EATON" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\EATON_IMPO"
    if client == "EATON" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\EATON_EXPO"
    if client == "SYSCOM" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\SYSCOM_IMPO"
    if client == "SYSCOM" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\SYSCOM_EXPO"
    if client == "ASFALTOS" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\ASFALTOS_IMPO"
    if client == "ASFALTOS" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\ASFALTOS_EXPO"
    if client == "HUTCHINSON" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\HUTCHINSON_IMPO"
    if client == "HUTCHINSON" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\HUTCHINSON_EXPO"
    if client == "TEGRANT" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\TEGRANT_IMPO"
    if client == "TEGRANT" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\TEGRANT_EXPO"
    if client == "LAU" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\LAU_IMPO"
    if client == "LAU" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\LAU_EXPO"
    if client == "JABIL" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\JABIL_IMPO"
    if client == "JABIL" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\JABIL_EXPO"
    if client == "ADIENT" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\ADIENT_IMPO"
    if client == "ADIENT" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\ADIENT_EXPO"
    if client == "ABISA" and invoice_type == "IMPO":
        client_folder = "D:\SpaceGpt\Files\ABISA_IMPO"
    if client == "TIGHITCO" and invoice_type == "EXPO":
        client_folder = "D:\SpaceGpt\Files\TIGHITCO_EXPO"

    copied_files = []
    low_text_files = []  # Para llevar un seguimiento de los archivos con menos del 10% de texto
    error_files = []  # Para llevar un seguimiento de los archivos que encontraron errores durante el procesamiento

    if not files:  # Verificar si la lista de archivos está vacía
        return "No se proporcionaron archivos para procesar."

    for file in files:
        destination_path = os.path.join(client_folder, os.path.basename(file.name))
        
        try:
            text_perc = get_text_percentage(file.name)  # Asegurarse de pasar el nombre del archivo, no el objeto de archivo
            print(f"Porcentaje de texto en {file.name}: {text_perc * 100:.2f}%")
            if text_perc > 0.01:
                shutil.copy(file.name, destination_path)
                copied_files.append(os.path.basename(file.name))  # Guardar solo el nombre del archivo para mayor legibilidad
            elif text_perc > 0.1:
                low_text_files.append(os.path.basename(file.name))
                print("El archivo tiene algo de texto pero principalmente imágenes/escaneado.")
            else:
                print("El archivo contiene contenido de texto significativo.")
            
        except Exception as e:
            print(f"Error al procesar {file.name}: {e}")
            error_files.append(os.path.basename(file.name))  # Rastrear archivos que tuvieron errores

            # Guardar los valores en un archivo JSON
    config = {
        "client": client_value,
        "invoice_type": invoice_type_value,
        "file_name": copied_files[0]
    }
    with open("config.json", "w") as f:
        json.dump(config, f)
    
    # Preparando el mensaje de retorno
    message_parts = []
    if copied_files:
        message_parts.append(f"Archivos copiados: {', '.join(copied_files)}")
    if low_text_files:
        message_parts.append(f"Archivos con menos del 10% de texto (no copiados, pero se necesita revisión): {', '.join(low_text_files)}")
    if error_files:
        message_parts.append(f"Archivos con errores: {', '.join(error_files)}")
    if not message_parts:
        message_parts.append("Ningún archivo cumplió con los criterios para ser copiado o revisado especialmente.")

    return "\n".join(message_parts)



if __name__ == '__main__':
    with gr.Blocks(theme=gr.themes.Monochrome()) as ui:
        with gr.Row():
            with gr.Column():
                gr.Markdown("SpaceGPT")
                client_dropdown = gr.Dropdown(label="Cliente", choices=["ABISA", "ADIENT", "ASFALTOS", "EATON", "HUTCHINSON", "JABIL", "LAU", "MMJ", "SYSCOM", "TEGRANT", "TIGHITCO"])
                invoice_type_dropdown = gr.Dropdown(label="Tipo de Factura", choices=["IMPO", "EXPO"])
                file_input = gr.File(label="Subir PDF", type="filepath", file_count="multiple", file_types=["pdf"])
                submit_button = gr.Button("Copiar Archivos")
                output = gr.Textbox(label="Resultado")
            
            submit_button.click(fn=copy_files_to_folder, inputs=[file_input, client_dropdown, invoice_type_dropdown], outputs=output)

    ui.launch(auth=("david.salas@sintek.com.mx", "david.salas@sintek.com.mx"), server_port=8888, server_name="0.0.0.0")
