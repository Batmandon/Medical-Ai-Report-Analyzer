# MedRep 🏥

An AI-powered medical report analyzer that helps patients and doctors understand complex medical reports in simple, plain language.

## What it does

Upload a medical report (PDF) and MedRep will:
- Summarize the report in simple language anyone can understand
- Highlight abnormal values that need attention
- Answer follow-up questions about the report
- Store all your reports and chat history for future reference

## Tech Stack

**Backend**
- FastAPI
- PostgreSQL + pgvector (Supabase)
- Google Gemini API
- JWT Authentication (access + refresh tokens)
- RAG (Retrieval Augmented Generation) for Q&A

**Frontend**
- HTML, CSS, JavaScript
- Marked.js for markdown rendering

**Deployment**
- Backend → Railway

## Features

- 🔐 User authentication (register, login, token refresh)
- 📄 PDF upload and AI-powered summarization
- 💬 Q&A chat about your report using RAG
- 📁 Sidebar with all uploaded reports
- 🗑️ Delete reports
- ⏳ Chat history saved per report
- 📱 Responsive layout

## Getting Started

### Prerequisites
- Python 3.10+
- Supabase account (PostgreSQL database)
- Google Gemini API key

### Installation

```bash
git clone https://github.com/Batmandon/Medical-Ai-Report-Analyzer.git
cd Medical-Ai-Report-Analyzer

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_supabase_connection_string
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
```

### Run Locally

```bash
uvicorn main:app --reload
```

Open `dashboard.html` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Login user |
| POST | `/refresh` | Refresh access token |
| POST | `/summarize/document` | Upload and summarize PDF |
| POST | `/ask/document` | Ask question about report |
| GET | `/my/files` | Get all user files |
| GET | `/files/{file_id}` | Get file summary |
| GET | `/chat/history/{file_id}` | Get chat history |
| DELETE | `/delete/files` | Delete a file |

## Roadmap

- [ ] Fix Railway deployment database connection
- [ ] AI-generated diet chart based on report findings
- [ ] Doctor dashboard with patient report management
- [ ] Multi-language support
- [ ] Mobile app

## Author

Built by Batman 🦇 — a self-taught developer learning by building real projects.

## License

MIT
