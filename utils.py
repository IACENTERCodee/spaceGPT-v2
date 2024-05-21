import fitz
import json
import sqlite3
import tiktoken
import re
import pandas as pd
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text_to_fp
from io import BytesIO

prompts = {
    "MMJ930128UR6": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "EIN0306306H6": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "SSC840823JT3": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "AFR831128KX6": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "AOM-210617-IC7": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "HSM-000316-H84": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "TME940420LV5": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "DME961118TX8": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "JTO181002378": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "ASH160921KB1": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "BUS941126M55": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    },
    "GENERAL": {
        "Prompt": """
        {
            "invoice_number": "str",
            "invoice_date": "str",
            "supplier":"str",
            "total":"float",
            "e_docu":"str",
            "incoterm":"str",
            "lumps":"float",
            "freights":"float",
            "buyer": "str",
            "rfc":"str",
            "items": [
                {
                    "part_number":"str",
                    "description":"str",
                    "quantity":"float",
                    "unit_of_measure":"str",
                    "unit_cost":"float",
                    "net_weight":"float",
                    "total":"float",
                    "gross_weight":"float",
                    "raw_material":"float",
                    "value_added":"float",
                    "country_of_origin":"str",
                    "fraction": "str",
                    "rate": "str",
                    "brand": "str",
                    "model": "str",
                    "serie": "str",
                    "po": "str",
                    "ref": "str"
                }
            ]
        }"""
    }
}

def convert_pdf_to_text(pdf_path):
    output_buffer = BytesIO()
    with open(pdf_path, 'rb') as pdf_file:
        extract_text_to_fp(pdf_file, output_buffer, output_type='tag')
        text_content = output_buffer.getvalue().decode('utf-8')
        print(text_content)
    return text_content


def search_word(text, word):
    # Using \b to define whole word boundaries
    # and re.IGNORECASE to ignore case sensitivity
    # The expression (?:(?<=\S)\S*|\b) before and after the word
    # allows handling cases where the text is joined together without spaces
    pattern = r"(?:(?<=\S)\S*|\b){}(?=\S*\S(?=\S)|\b)".format(re.escape(word))
    return re.findall(pattern, text, re.IGNORECASE)


def get_prompt(rfc):
    """
    Retrieves the prompt for a given RFC.
    """
    rfc = rfc.upper()  # Ensure RFC is in uppercase for uniformity
    # Return the prompt for the given RFC if it exists, otherwise return the general prompt
    return prompts.get(rfc, prompts["GENERAL"])["Prompt"]


def search_RFC_in_text(text):
    """
    Searches for an RFC in the given text and returns the corresponding prompt if found.
    """
    rfc_list = ["MMJ930128UR6", "EIN0306306H6", "SSC840823JT3", "SSC - 840823 - JT3", "SSC-840823-JT3", "AFR831128KX6", "AFR 831128 KX6", "AOM-210617-IC7", "HSM000316H84", "HSM-000316-H84", "HSM-000316H84", "TME940420LV5", "RME040213EC5", "JTO181002378", "TLA010227C50", "ASH160921KB1", "BUS941126M55"]
    for rfc in rfc_list:
        # Check if the RFC is found in the text
        if search_word(text, rfc):
            print(f"RFC {rfc} encontrado")
            return get_prompt(rfc), rfc
    # Return the general prompt if no RFC is found
    print("RFC no encontrado")
    return get_prompt("GENERAL"),rfc


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding_name = "cl100k_base"
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def reader(pdf_path):
    text=convert_pdf_to_text(pdf_path)
    numTokens= num_tokens_from_string(text)
    return text,numTokens


def extract_text_from_pdf(pdf_path):
    text=""
    pdf_reader=PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text+=page.extract_text()
    numTokens= num_tokens_from_string(text)
    return text,numTokens


def convert_json_to_dataframe_invoice(invoice_dict):
    if not isinstance(invoice_dict, dict):
        return pd.DataFrame()

    # Extraer el primer elemento de cada lista para obtener los valores reales
    invoice_data = {key: value[0] if isinstance(value, list) else value for key, value in invoice_dict.items()}

    return pd.DataFrame([invoice_data])

def convert_json_to_dataframe_items(items_list):
    if not isinstance(items_list, list) or not all(isinstance(item, list) for item in items_list):
        return pd.DataFrame()

    # Asumimos que los ítems están en la primera lista, si la estructura es una lista de listas
    items = items_list[0] if items_list and isinstance(items_list[0], list) else items_list

    return pd.DataFrame(items)

def is_pdf_readable(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:  # Open the PDF file
            text = ""
            for page in doc: 
                text += page.get_text()
            return True
    except:
        return False
    
