import time
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# Cargar los valores del archivo de configuración JSON
with open("config.json", "r") as f:
    config = json.load(f)

global_client = config["client"]
global_invoice_type = config["invoice_type"]

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def submit_and_wait_for_response(rfc, question):
    try:
        # Retrieve an existing assistant by ID
        if global_client == "MMJ" and global_invoice_type == "IMPO":
            print("MMJ-IMPO")
            assistant_id = "asst_Sidz8WQuW51PbhY2BihgvweC"
        elif global_client == "MMJ" and global_invoice_type == "EXPO":
            print("MMJ-EXPO")
            assistant_id = "asst_pQVz6SfbJ3RHMdxPxw0Y7SFn"
        elif global_client == "EATON" and global_invoice_type == "IMPO":
            print("EATON-IMPO")
            assistant_id = "asst_Ml9mh1nRrLroOPcWbCmfSbZR"
        elif global_client == "EATON" and global_invoice_type == "EXPO":
            print("EATON-EXPO")
            assistant_id = "asst_mxxoMvgJP92y85zMFS9q1INB"
        elif global_client == "SYSCOM" and global_invoice_type == "IMPO":
            print("SYSCOM-EXPO")
            assistant_id = "asst_Psl5gObCPzVWZIeUbsdIlv6P"
        elif global_client == "SYSCOM" and global_invoice_type == "EXPO":
            print("SYSCOM-EXPO")
            assistant_id = "asst_6z7JLlo9aqYudxr9Bu4TC5Xu"
        elif global_client == "ASFALTOS" and global_invoice_type == "IMPO":
            print("ASFALTOS-IMPO")
            assistant_id = "asst_WxZ8MSUD4xNZxnkRcfLOiDRZ"
        elif global_client == "ASFALTOS" and global_invoice_type == "EXPO":
            print("ASFALTOS-EXPO")
            assistant_id = "asst_AGv5R8CSHoLqyLOZv5ZAnZGD"
        elif global_client == "HUTCHINSON" and global_invoice_type == "IMPO":
            print("HUTCHINSON-IMPO")
            assistant_id = "asst_TeYdTu8e5HDCwS823WL4ZtBk"
        elif global_client == "HUTCHINSON" and global_invoice_type == "EXPO":
            print("HUTCHINSON-EXPO")
            assistant_id = "asst_KeS0fPWWWiSKrr8lF1ON7J21"
        elif global_client == "TEGRANT" and global_invoice_type == "IMPO":
            print("TEGRANT-IMPO")
            assistant_id = "asst_IEHIhJGYrDLjuPSDaLKZLnG1"
        elif global_client == "TEGRANT" and global_invoice_type == "EXPO":
            print("TEGRANT-EXPO")
            assistant_id = "asst_5ZXlHjwcpk9oTJYxDoSR38QB"
        elif global_client == "LAU" and global_invoice_type == "IMPO":
            print("LAU-IMPO")
            assistant_id = "asst_o7l0cRJrFLY6HV37d24V0WT0"
        elif global_client == "LAU" and global_invoice_type == "EXPO":
            print("LAU-EXPO")
            assistant_id = "asst_hjL9FagSwLDSC7WiS3l0CwvL"
        elif global_client == "JABIL" and global_invoice_type == "IMPO":
            print("JABIL-IMPO")
            assistant_id = "asst_Vobk3ESaXTb9UU9TuSiEpTe9"
        elif global_client == "JABIL" and global_invoice_type == "EXPO":
            print("JABIL-EXPO")
            assistant_id = "asst_7VStyb86PVZv2gLBeM7jl1Zw"
        elif global_client == "ADIENT" and global_invoice_type == "IMPO":
            print("ADIENT-IMPO")
            assistant_id = "asst_zb3VZ0z9rYX7JON302ve0wxo"
        elif global_client == "ADIENT" and global_invoice_type == "EXPO":
            print("ADIENT-EXPO")
            assistant_id = "asst_QEeGhMoekux2rfaoblvQF7Ph"
        elif global_client == "ABISA" and global_invoice_type == "IMPO":
            print("ABISA-IMPO")
            assistant_id = "asst_XWZNf6zTX6yrbC9xDZM7Rd8X"
        elif global_client == "TIGHITCO" and global_invoice_type == "EXPO":
            print("TIGHITCO-EXPO")
            assistant_id = "asst_rLBqgG7Nrpt0Kq0zdGD4XdJN"


        # Create a new thread
        thread = client.beta.threads.create()

        # Send the question to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # Execute the thread with the specified assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            extra_headers={"OpenAI-Beta": "assistants=v2"} 
        )

        # Wait for the run to complete
        run = wait_on_run(run, thread)

        # Get the response from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        last_message = messages.data[0]  
        response = last_message.content[0].text.value

        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage