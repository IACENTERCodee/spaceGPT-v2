import os
import asyncio
import time
import json
import pandas as pd
from utils import reader,is_pdf_readable,convert_json_to_dataframe_invoice,convert_json_to_dataframe_invoice,convert_json_to_dataframe_items
import api_openai
from db import insert_invoice_data
import re

tokens_processed = 0
token_limit_per_minute = 600000

# Función para procesar un archivo individual
async def process_file(file):
    global tokens_processed

    # Obtienes el texto de PDF y la cantidad de tokens
    text, numTokens = reader(file) 


    if tokens_processed + numTokens > token_limit_per_minute:
        await asyncio.sleep(60 - time.time() % 60)
        tokens_processed = 0


    tokens_processed += numTokens
    print("Prompt tokens: ", numTokens)
    OpenAIHelper = api_openai.OpenAIHelper()
    extracted_text = await OpenAIHelper.extract_fields_from_invoice(text)
    if extracted_text is not None:
        match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
        if match:
            extracted_text = match.group(0)
        # save extracted text to a file
        with open(f"{file}.json", "w") as f:
            f.write(extracted_text)
        json_data = json.loads(extracted_text)
        if is_pdf_readable(file):
            file_name = os.path.basename(file)
            insert_invoice_data(json_data, file_name)
            invoices = convert_json_to_dataframe_invoice(json_data)
            items = convert_json_to_dataframe_items(json_data)
        else:
            invoices = pd.DataFrame()
            items = pd.DataFrame()
    else:
        invoices = pd.DataFrame()
        items = pd.DataFrame()
    try:
        os.remove(file)
        print(f"Archivo {file} eliminado con éxito.")
    except OSError as e:
        print(f"Error al eliminar {file}: {e.strerror}")
    print(f"Archivo {file} procesado con éxito.")
    
    return extracted_text, invoices, items

# Función para procesar todos los archivos en un directorio
async def process_directory(directory_path):
    global tokens_processed
    text_results = []
    invoices_results = []
    items_results = []
    batch = []

    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        # Asegúrate de que el archivo es un PDF
        if os.path.isfile(file_path) and file_name.lower().endswith('.pdf'):
            print(file_name)
            text, numTokens = reader(file_path)
            if tokens_processed + numTokens <= token_limit_per_minute:
                batch.append(file_path)
                tokens_processed += numTokens
            else:
                batch_results = await asyncio.gather(*[process_file(f) for f in batch])
                for text, invoices, items in batch_results:
                    text_results.append(text)
                    invoices_results.append(invoices)
                    items_results.append(items)
                batch = [file_path]
                tokens_processed = numTokens
                await asyncio.sleep(60 - time.time() % 60)

    if batch:
        batch_results = await asyncio.gather(*[process_file(f) for f in batch])
        for text, invoices, items in batch_results:
            text_results.append(text)
            invoices_results.append(invoices)
            items_results.append(items)

    return text_results, invoices_results, items_results


# Ejecución principal
if __name__ == '__main__':
    directory_paths = [
        r'D:/SpaceGpt/Files/MMJ_IMPO/',
        r'D:/SpaceGpt/Files/MMJ_EXPO/',
        r'D:/SpaceGpt/Files/EATON_IMPO/',
        r'D:/SpaceGpt/Files/EATON_EXPO/',
        r'D:/SpaceGpt/Files/SYSCOM_IMPO/',
        r'D:/SpaceGpt/Files/SYSCOM_EXPO/',
        r'D:/SpaceGpt/Files/ASFALTOS_IMPO/',
        r'D:/SpaceGpt/Files/ASFALTOS_EXPO/',
        r'D:/SpaceGpt/Files/HUTCHINSON_IMPO/',
        r'D:/SpaceGpt/Files/HUTCHINSON_EXPO/',
        r'D:/SpaceGpt/Files/TEGRANT_IMPO/',
        r'D:/SpaceGpt/Files/TEGRANT_EXPO/',
        r'D:/SpaceGpt/Files/LAU_IMPO/',
        r'D:/SpaceGpt/Files/LAU_EXPO/',
        r'D:/SpaceGpt/Files/JABIL_IMPO/',
        r'D:/SpaceGpt/Files/JABIL_EXPO/',
        r'D:/SpaceGpt/Files/ADIENT_IMPO/',
        r'D:/SpaceGpt/Files/ADIENT_EXPO/',
        r'D:/SpaceGpt/Files/BUSSMANN_IMPO/',
        r'D:/SpaceGpt/Files/BUSSMANN_EXPO/',
        r'D:/SpaceGpt/Files/ABISA_IMPO/',
        r'D:/SpaceGpt/Files/TIGHITCO_EXPO/',
    ]
    async_tasks = [process_directory(directory_path) for directory_path in directory_paths]
    results = asyncio.run(asyncio.wait(async_tasks))    
