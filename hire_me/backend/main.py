
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from pypdf import PdfReader
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=my_api_key)

model = "openai/gpt-oss-20b"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ravi-tiwari-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    responsibilities: list[str] = []


class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = []


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    education: str | None = None
    skills: list[str] = []
    experiences: list[Experience] = []
    projects: list[Project] = []
    achievements: list[str] = []


resume_schema = Resume.model_json_schema()


class ChatResponse(BaseModel):
    answer: str


chat_schema = ChatResponse.model_json_schema()


def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


BASE_DIR = Path(__file__).resolve().parent

RESUME_PATH = BASE_DIR / "ravi_tiwari_resume(ai).pdf"

resume_text = read_pdf(str(RESUME_PATH))


resume_system_prompt = f"""
You are a resume information extraction assistant.

Extract structured information ONLY from the resume text provided by the user.

Return ONLY valid JSON using this schema:

{resume_schema}

Rules:
1. Never invent information.
2. Never assume information not supported by the resume.
3. Extract as much useful detail as the resume provides.
4. Preserve important technical details.
5. For projects, capture the name, description, and technologies when available.
6. For experience, capture company, role, duration, and responsibilities when available.
7. If a single-value field is missing, use null.
8. If a list field has no information, use [].
9. Return only the JSON object.
"""

resume_user_prompt = f"""
Extract the candidate's resume information into JSON.

Resume text:

---------------- RESUME ----------------

{resume_text}

-------------- END RESUME --------------
"""

resume_messages = [
    {
        "role": "system",
        "content": resume_system_prompt
    },
    {
        "role": "user",
        "content": resume_user_prompt
    }
]

resume_response = client.chat.completions.create(
    model=model,
    messages=resume_messages,
    temperature=0,
    response_format={"type": "json_object"}
)

raw_resume_json = resume_response.choices[0].message.content

resume_data = json.loads(raw_resume_json)

resume = Resume(**resume_data)


chat_system_prompt = f"""
You are an AI assistant representing the candidate.

Answer recruiter questions using ONLY the structured resume information below.

================ RESUME JSON ================

{resume.model_dump_json(indent=2)}

============== END RESUME JSON ==============

Rules:

1. The resume is your only source of factual information.
2. Never invent skills, experience, companies, projects, education,
   achievements, technologies, or responsibilities.
3. You may summarize, paraphrase, combine, and explain information
   that is already present in the resume.
4. Understand the recruiter's intent instead of requiring exact
   wording from the resume.
5. For project questions, use the project name, description,
   technologies, and other relevant resume information.
6. For experience questions, combine relevant roles,
   companies, durations, and responsibilities.
7. For questions such as:
   - "Why should we hire you?"
   - "Why are you a good fit?"
   - "Why are you suitable for this role?"
   - "What makes you a strong candidate?"

   combine relevant skills, projects, experience, education,
   and achievements from the resume and explain why they could
   make the candidate suitable.
8. If job requirements are provided, compare them with the
   candidate's resume and explain the overlap using only
   resume-supported information.
9. Do not claim that the candidate is definitely the best candidate.
10. If something is completely absent from the resume, return exactly:

"I don't have information about that in my resume."

11. Keep answers professional and reasonably concise.
12. Return ONLY valid JSON.
13. Do not use markdown.
14. Do not add anything before or after the JSON.

Required output schema:

{chat_schema}
"""


def ask_resume_bot(question: str) -> ChatResponse:
    user_prompt = f"""
Recruiter's question:

{question}
"""

    chat_messages = [
        {
            "role": "system",
            "content": chat_system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=chat_messages,
        temperature=0,
        response_format={"type": "json_object"}
    )

    raw_answer = response.choices[0].message.content

    answer_data = json.loads(raw_answer)

    return ChatResponse(**answer_data)


@app.get("/")
def home():
    return {
        "message": "Hire Me Resume Bot is running!"
    }


@app.get("/resume")
def get_resume():
    return resume.model_dump()


@app.get("/ask", response_model=ChatResponse)
def ask(question: str):
    return ask_resume_bot(question)