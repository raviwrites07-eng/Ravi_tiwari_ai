import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document

load_dotenv()


# pahle job description ko deal karte hain fir resume ko deal karenge


class JobDescription(BaseModel):
    post: str
    company: str
    education: str
    skills: list[str]
    experience: float


class Experience(BaseModel):
    company: str
    role: str
    duration: str


class Resume(BaseModel):
    name: str
    email: str
    phone: str
    education: str
    skills: list[str]
    experiences: list[Experience]


job_schema = JobDescription.model_json_schema()
resume_schema = Resume.model_json_schema()


# Resume Reader(resume ko read karne ke liye class banayenge)


class ResumeReader:

    def read_resume(self, file_path: str) -> str:

        suffix = Path(file_path).suffix.lower()

        if suffix == ".pdf":
            return self.read_pdf(file_path)

        elif suffix == ".docx":
            return self.read_docx(file_path)

        elif suffix == ".txt":
            return self.read_txt(file_path)

        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def read_pdf(self, file_path: str) -> str:

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    def read_docx(self, file_path: str) -> str:

        document = Document(file_path)

        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    def read_txt(self, file_path: str) -> str:

        return Path(file_path).read_text(encoding="utf-8")

    def read_resume_folder(self, folder_path: str) -> list[str]:

        resumes = []

        folder = Path(folder_path)

        for file in folder.iterdir():

            if file.is_file():

                try:
                    text = self.read_resume(str(file))
                    resumes.append(text)

                except ValueError:
                    continue

        return resumes



# Groq Client


my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API key nahi hai babu.")

client = Groq(api_key=my_api_key)

model = "llama-3.3-70b-versatile"

response_format = {
    "type": "json_object"
}


# Parse Job Description


jd_text = Path("job_description.txt").read_text(encoding="utf-8")

jd_system_prompt = f"""
You are an HR.
Extract the information according to this schema.
Return the result ONLY as valid JSON.

{job_schema}

If any field is missing, return null.
"""

jd_user_prompt = f"""
Here is the job description.

{jd_text}
"""

messages = [
    {
        "role": "system",
        "content": jd_system_prompt
    },
    {
        "role": "user",
        "content": jd_user_prompt
    }
]

response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0.7,
    response_format=response_format
)

answer = response.choices[0].message.content

jd_data = json.loads(answer)

job_description = JobDescription(**jd_data)



reader = ResumeReader()

resume_texts = reader.read_resume_folder("resumes")


parsed_resumes = []

resume_system_prompt = f"""
You are an HR.

Extract the information according to this schema.
Return the result ONLY as valid JSON.

{resume_schema}

If any field is missing, return null.
"""

for resume_text in resume_texts:

    resume_user_prompt = f"""
    Here is the resume.

    {resume_text}
    """

    messages = [
        {
            "role": "system",
            "content": resume_system_prompt
        },
        {
            "role": "user",
            "content": resume_user_prompt
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        response_format=response_format
    )

    resume_answer = response.choices[0].message.content

    resume_data = json.loads(resume_answer)

    resume = Resume(**resume_data)

    parsed_resumes.append(resume)



for resume in parsed_resumes:
    print(resume)
    print("-" * 50)
class MatchResult(BaseModel):
    overall_score: int
    summary: str    
match_schema = MatchResult.model_json_schema()  


match_system_prompt = f"""
You are an experienced Technical HR Recruiter.

Compare the Job Description and Candidate Resume.

Return ONLY valid JSON according to this schema.

{match_schema}

Rules:

1. overall_score should be between 0 and 100.
2. summary should be only 2-3 lines.
3. Mention what makes the candidate suitable.
4. Mention the major missing skills or experience.
5. Don't use markdown.
6. Don't explain your reasoning.
"""  
for resume in parsed_resumes:

    match_user_prompt = f"""
Job Description:

{job_description.model_dump_json(indent=2)}

Candidate Resume:

{resume.model_dump_json(indent=2)}
"""

    messages = [
        {
            "role": "system",
            "content": match_system_prompt
        },
        {
            "role": "user",
            "content": match_user_prompt
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        response_format=response_format
    )

    answer = response.choices[0].message.content

    result = json.loads(answer)

    evaluation = MatchResult(**result)

    print("=" *20)
    print(f"Candidate : {resume.name}")
    print(f"Overall Score : {evaluation.overall_score}")
    print(f"Summary : {evaluation.summary}")