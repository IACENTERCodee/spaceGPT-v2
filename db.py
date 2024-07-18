import pyodbc
import json
import re
import os 
from dotenv import load_dotenv
import json

# Cargar los valores del archivo de configuración JSON
with open("config.json", "r") as f:
    config = json.load(f)

global_client = config["client"]
global_invoice_type = config["invoice_type"]
global_folder_path = config["folder_path"]

if global_invoice_type == "EXPO":
    operation_type = 0
else:
    operation_type = 1

def connect_db():
    """Create and return a connection to the database using environment variables."""
    load_dotenv()

    host = os.getenv("HOST")
    user = os.getenv("USER")
    password = os.getenv("PASS")
    database = os.getenv("DATABASE")

    try:
        # The driver name might vary depending on the SQL Server version and the operating system.
        # Common drivers are 'SQL Server', 'ODBC Driver 17 for SQL Server', etc.
        # Make sure to install the correct ODBC driver for your SQL Server version.
        connection_string = f'DRIVER={{SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password}'
        dbconection=pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',Server=host,Database=database,UID=user,PWD=password,autocommit=True)
        print("Connection to database successful")
        return dbconection
    except Exception as e:
        print(e)
        print("Connection to database failed")


def insert_invoice_data(json_data, file_name):
    """Inserta datos de factura en la base de datos."""
    if json_data is None:
        return
    if json_data == '':
        return
    
    conn = connect_db()
    try:
        with conn:
            cur = conn.cursor()
            # Procesa y convierte los datos del JSON
            processed_data = json_data

            processed_data["processed"] = 0

            # Lista de todas las columnas esperadas en la tabla de facturas
            expected_columns = ["supplier", "buyer", "e_docu", "incoterm", "lumps", "freights"]

            # Verificar y agregar columnas faltantes con valor None
            for column in expected_columns:
                if column not in processed_data:
                    processed_data[column] = None
            
            if processed_data['freights'] == None:
                processed_data['freights'] = 0.0

            # Inserta en la tabla de facturas
            invoice_data = processed_data
            cur.execute("""
                INSERT INTO invoices (invoice_number, invoice_date, supplier, buyer, total, e_docu, incoterm, lumps, freights, rfc, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (invoice_data['invoice_number'], invoice_data['invoice_date'], 
                  invoice_data['supplier'], invoice_data['buyer'], invoice_data['total'], 
                  invoice_data['e_docu'], invoice_data['incoterm'],
                  invoice_data['lumps'], invoice_data['freights'], 
                  invoice_data['rfc'], invoice_data['processed']))
            # Lista de todas las columnas esperadas en la tabla de line_items
            expected_columns = ["part_number", "unit_of_measure", 
                                "unit_cost", "net_weight", "gross_weight", 
                                "country_of_origin", "fraction", "rate", "brand", "model", 
                                "serie", "po", "ref", "raw_material", "value_added"]

            cur.execute("SELECT IDENT_CURRENT('invoices');")
            invoice_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO pdf (invoice_id, operation_type, client_name, folder_path, file_name)
                VALUES (?, ?, ?, ?, ?);
            """, (invoice_id, global_invoice_type, global_client, global_folder_path, file_name))


            for item in invoice_data['items']: 
                # Verificar y agregar columnas faltantes con valor None
                for column in expected_columns:
                    if column not in item:
                        item[column] = None
                if item['unit_cost'] == None:
                    item['unit_cost'] = 0.0
                if item['net_weight'] == None:
                    item['net_weight'] = 0.0
                if item['gross_weight'] == None:
                    item['gross_weight'] = 0.0
                if item['raw_material'] == None:
                    item['raw_material'] = 0.0
                if item['value_added'] == None:
                    item['value_added'] = 0.0

                cur.execute("""
                    INSERT INTO line_items (invoice_id, part_number, description, quantity, unit_of_measure, unit_cost, 
                                            net_weight, total, gross_weight, country_of_origin, fraction, rate, brand, model, 
                                            serie, po, ref, raw_material, value_added)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (invoice_id, item['part_number'], item['description'], 
                    item['quantity'], item['unit_of_measure'], item['unit_cost'], 
                    item['net_weight'], item['total'], item['gross_weight'],
                    item['country_of_origin'], item['fraction'], item['rate'], 
                    item['brand'], item['model'], item['serie'], item['po'], 
                    item['ref'], item['raw_material'], item['value_added']))
            conn.commit()
    except pyodbc.Error as e:
        print(f"Error de SQL Server: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
