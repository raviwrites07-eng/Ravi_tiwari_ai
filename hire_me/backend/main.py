
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
        "http://localhost:5173"
        "http://127.0.0.1:5173",
        "https://ravi-tiwari-ai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    education: str | None = None

    skills: list[str] = []

    experiences: list[Experience] = []

    projects: list[str] = []

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

Your task is to extract information ONLY from the
resume text provided by the user.

Return ONLY valid JSON according to this schema:

{resume_schema}

Rules:

1. Never invent information.
2. Never assume information.
3. Use only information explicitly present in the resume.
4. If a field is unavailable, return null.
5. For list fields, return an empty list if nothing is found.

Use exactly these JSON fields:

{{
    "name": null,
    "email": null,
    "phone": null,
    "education": null,
    "skills": [],
    "experiences": [],
    "projects": [],
    "achievements": []
}}

If information is not present in the resume:
- use null for a single-value field
- use [] for a list field

Resume information must come only from the provided resume text.
"""



resume_user_prompt = f"""
Extract the resume information into JSON.

Resume text:



{resume_text}


"""


# Messages for the first LLM call
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
    
    

    
    response_format={
        "type": "json_object"
    }
)



raw_resume_json = resume_response.choices[0].message.content



resume_data = json.loads(raw_resume_json)




resume = Resume(**resume_data)




# SYSTEM PROMPT FOR RECRUITER CHATBOT


chat_system_prompt = f"""
You are an AI assistant representing the candidate.

You answer recruiter questions using ONLY the
structured resume information provided below.

================ RESUME JSON ================

{resume.model_dump_json(indent=2)}

============== END RESUME JSON ==============

IMPORTANT RULES:

1. Only use information present in the resume JSON.
2. Never invent any information.
3. Never assume missing information.
4. Do not claim a skill, company, role, project,
   qualification, or experience unless it exists
   in the resume JSON.
5. If the answer cannot be found in the resume,
   return exactly:

"I don't have information about that in my resume."

6. Keep the answer concise and professional.
7. Return ONLY valid JSON.
8. Do not use markdown.
9. Do not add text before or after the JSON.

Required output schema:

{chat_schema}
"""


# ============================================================
# STEP 10
# FUNCTION FOR RECRUITER QUESTIONS
# ============================================================

def ask_resume_bot(question: str) -> ChatResponse:
    """
    Send the recruiter question to the LLM.

    The LLM receives:
        1. System prompt
        2. Structured Resume JSON
        3. Recruiter's question
    """

    
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

        # Low temperature because we want factual answers
        temperature=0,
        

        # Force JSON output
        response_format={
            "type": "json_object"
        }
    )


    
    raw_answer = response.choices[0].message.content


    # Convert JSON string into Python dictionary
    answer_data = json.loads(raw_answer)


    
    result = ChatResponse(**answer_data)

    return result



@app.get("/")
def home():
    """
    Simple route to check if backend is running.
    """

    return {
        "message": "Hire Me Resume Bot is running!"
    }



@app.get("/resume")
def get_resume():
    """
    Return the structured resume JSON.

    Useful for checking whether the LLM extracted
    the resume correctly.
    """

    return resume.model_dump()



@app.get("/ask", response_model=ChatResponse)
def ask(question: str):
    
    

    result = ask_resume_bot(question)

   
    return result