from fastapi import UploadFile
from database import get_cursor
from auth import get_user_by_email
from jwt import decode_token
import shutil
import json
import os
import uuid
from models import QuestionRequest
from ai import response_document, create_embedding, ask_document
from rag import process_document,search_similar_chunks

def upload_document(file:UploadFile, token:str): 

    payload = decode_token(token)
    email = payload.get("sub")
    
    with get_cursor() as cursor:
        user = get_user_by_email(cursor,email)
        if not user:
            return {"error": "User not found"}
        user_id = user["id"]
         
    allowed = ["application/pdf"]
    if file.content_type not in allowed:
        return {"error": "Only PDFs are allowed"}
    
    os.makedirs("uploads", exist_ok=True)

    unique_id = str(uuid.uuid4())
    file_path = f"uploads/{unique_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file,buffer)


    text, chunks_with_embeddings = process_document(file_path)
    summary, token_used = response_document(text)

    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO files (user_id, filename, path) VALUES (%s, %s, %s) RETURNING id",
            (user_id, file.filename, str(file_path))
        )
        file_row = cursor.fetchone()
        file_id = file_row["id"]

        cursor.execute("INSERT INTO chat_history(file_id, history) VALUES (%s, %s)",
                       (file_id, json.dumps([])))
        
        for chunk, embedding in chunks_with_embeddings:

            cursor.execute(
                "INSERT INTO document_chunks (file_id, chunk_text, embedding) VALUES (%s, %s, %s)",
                (file_id, chunk, embedding)
            )

        cursor.execute(
            "INSERT INTO summaries (file_id, summary, tokens_used) VALUES (%s, %s, %s)",
            (file_id, summary, token_used)
        )

    return {
        "message": "File uploaded sucessfully",
        "summary": summary,
        "file_id": file_id
    }

def answer_document(ques: QuestionRequest, token: str):
    payload = decode_token(token)
    email = payload.get("sub")

    with get_cursor() as cursor:
        user = get_user_by_email(cursor,email)
        if not user:
            return {"error": "User not found"}

        cursor.execute("SELECT * FROM files WHERE id = %s", (ques.file_id,))
        file = cursor.fetchone()

        if not file:
            return {"error": "file not found"}
        
        embed = create_embedding(ques.question)

        chunks = search_similar_chunks(embed, ques.file_id)

        context = "\n".join([row["chunk_text"] for row in chunks])

        answer = ask_document(context, ques.question)

        cursor.execute("SELECT * FROM chat_history WHERE file_id = %s", (ques.file_id,))
        history1 = cursor.fetchone()

        if not history1: 
            return {"error": "No chat history found for this file"}
        
        history = history1["history"]
        history.append({"role": "user", "content": ques.question})
        history.append({"role": "model", "content": answer}
                       )
        cursor.execute("UPDATE chat_history SET history = %s WHERE file_id = %s", (json.dumps(history), ques.file_id))

        return answer


def all_specific_user_documents(token: str):

    payload = decode_token(token)
    email = payload.get("sub")

    with get_cursor() as cursor:
        user = get_user_by_email(cursor, email)
    
        if not user:
            return {"error": "User not found"}
        user_id = user["id"]
        cursor.execute ("SELECT * FROM files WHERE user_id = %s", (user_id,))
        files= cursor.fetchall()

        if not files:
            return {"error": "File not found"}
        
        return files

def delete_document(file_id: int, token: str):
    payload = decode_token(token)
    email = payload.get("sub")

    with get_cursor() as cursor:
        user = get_user_by_email(cursor, email)

        if not user:
            return {"error": "User not found"}

        user_id = user["id"]

        cursor.execute("SELECT * FROM  files WHERE id = %s AND user_id = %s", (file_id, user_id))
        file = cursor.fetchone()

        if not file:
            return {"error": "You donot have access to delete it "}

        cursor.execute("DELETE FROM files WHERE id = %s AND user_id = %s", (file_id, user_id))
        
        return {"message": "file deleted successfully"}
    
def get_file_summary(file_id: int, token: str):
    payload = decode_token(token)
    email = payload.get("sub")

    with get_cursor() as cursor:
        user = get_user_by_email(cursor, email)
        if not user:
            return {"error": "User not found"}

        user_id = user["id"]

        cursor.execute("SELECT s.summary, f.filename FROM summaries s JOIN files f ON f.id = s.file_id WHERE s.file_id = %s AND f.user_id = %s", 
                   (file_id, user_id))
        row = cursor.fetchone()

        if not row:
            return {"summary": None}

        return {
            "summary": row["summary"],
            "filename": row["filename"]
        }

def chat_history(file_id: int , token: str):
    payload = decode_token(token)
    email = payload.get("sub")

    with get_cursor() as cursor:
        user = get_user_by_email(cursor, email)

        if not user:
            return {"error": "User not found"}
        
        cursor.execute("SELECT * FROM chat_history WHERE file_id = %s", (file_id,))
        history = cursor.fetchone()

        if not history:
            return []
        
        return history["history"]