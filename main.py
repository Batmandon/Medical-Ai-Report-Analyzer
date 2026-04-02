from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from models import UserSignup, UserLogin,UserRefresh, QuestionRequest
from auth import register_user, login_user, refresh
from document import upload_document, answer_document, all_specific_user_documents, delete_document, chat_history, get_file_summary
from database import create_database
from fastapi import File, UploadFile
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from logger import logger
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
create_database()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Something went wrong"}
    )

@app.post("/register")
@limiter.limit("5/minute")
def registering_user(request:Request, User: UserSignup):
    result = register_user(User)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/login")
@limiter.limit("5/minute")
def logining_user(request: Request, User: UserLogin):
    result = login_user(User)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/refresh")
@limiter.limit("5/minute")
def refresh_user(request: Request, User: UserRefresh):
    result = refresh(User)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@app.post("/summarize/document")
@limiter.limit("5/minute")
def summarize_document(request: Request, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    result = upload_document(file, token)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@app.post("/ask/document")
@limiter.limit("5/minute")
def ask_document_route(request: Request,
    body: QuestionRequest, token: str = Depends(oauth2_scheme)):
    result = answer_document(body, token)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@app.get("/user/files")
@limiter.limit("5/minute")
def my_files(request: Request, token: str = Depends(oauth2_scheme)):
    result = all_specific_user_documents(token)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@app.delete("/delete/files")
@limiter.limit("5/minute")
def delete_files(request: Request, file_id: int, token: str = Depends(oauth2_scheme)):
    result = delete_document(file_id, token)
    if "error" in result:
        raise HTTPException(status_code=401, detail="File not Exists")
    return result

@app.get("/files/{file_id}")
@limiter.limit("5/minute")
def get_file(request: Request, file_id: int, token: str = Depends(oauth2_scheme)):
    result = get_file_summary(file_id, token)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@app.get("/chat/history/{file_id}")
@limiter.limit("5/minute")
def get_chat_history(request: Request, file_id: int, token: str = Depends(oauth2_scheme)):
    result = chat_history(file_id, token)
    if isinstance(result,dict) and "error" in result:
        raise HTTPException(status_code=401, detail="File not Exists")
    return result