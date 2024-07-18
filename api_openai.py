import os
import tiktoken
from dotenv import load_dotenv
from openai import AsyncOpenAI
import json
from utils import search_RFC_in_text
from asis import submit_and_wait_for_response

class OpenAIHelper:
    """A helper class to interact with OpenAI's API for specific tasks such as extracting information from invoices."""

    def __init__(self, model="gpt-4-turbo"):
        """Initializes the OpenAIHelper with the specified model and API key."""
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def extract_fields_from_invoice(self, invoice_text):
        """
        Asynchronously extracts fields from a given invoice text.

        :param invoice_text: Text of the invoice from which to extract information.
        :return: Extracted invoice details in JSON format.
        """
        rfc =  search_RFC_in_text(invoice_text)
    
        if rfc in ["MMJ930128UR6", "EIN0306306H6", "SSC840823JT3", "SSC - 840823 - JT3", "SSC-840823-JT3", "AFR831128KX6", "AFR 831128 KX6", "AOM-210617-IC7", "HSM000316H84", "HSM-000316-H84", "HSM-000316H84", "TME940420LV5", "RME040213EC5", "JTO181002378", "TLA010227C50", "ASH160921KB1", "BUS941126M55"]:
            extracted_text = submit_and_wait_for_response(invoice_text)
            return  extracted_text
        
        responses = [extracted_text]

        combined_response = {}
        
        for response in responses:
            try:
                #regex for extract json el primer { y el ultimo }
                response = response[response.find("{"):response.rfind("}")+1]
                partial_json = json.loads(response)
                for key, value in partial_json.items():
                    combined_response.setdefault(key, []).append(value)
            except json.JSONDecodeError:
                print("Error al decodificar JSON:", response)

        return json.dumps(combined_response, indent=4)