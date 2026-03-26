from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from database import get_cursor
from logger import logger
client = genai.Client(api_key=GEMINI_API_KEY)

def create_embedding(text):
    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )

        return list(response.embeddings[0].values)
    except Exception as e:
        logger.error(f"Embedding failed: {str(e)}")
        raise
    
def response_document(text:str, file_id: int):
  
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=
        f"""You are a medical report analyzer. Analyze this medical report and provide:
        1. A brief overview of what this report is about
        2. Key findings and values (highlight abnormal ones clearly)
        3. What these results mean in simple language a patient can understand
        4. Any values that need immediate attention

        Be clear, concise, and use simple language. Avoid unnecessary medical jargon.

        Report:{text}""")

    summary =  response.text
    token_used = response.usage_metadata.total_token_count

    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO summaries (file_id, summary, tokens_used) VALUES(%s, %s, %s)",
                (file_id, summary, token_used)
        )

    return summary

def ask_document(context, question):

    prompt=f"""You are a helpful medical assistant analyzing a patient's medical report.
            Answer the patient's question using only the information from their report.
            Use simple, clear language that a non-medical person can understand.
            If the answer is not in the report, say so clearly.
            If a value seems concerning, mention it gently but recommend consulting a doctor.


    Report context:
    {context}

    Patience's question:
    {question}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text