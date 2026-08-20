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

knowledge_base = {"age": "ravi tiwari age is 23", "networth": "ravi tiwari networth is 1.5 crore", "education": "ravi tiwari education is btech in computer science", "skills": "ravi tiwari skills are python,java,sql,html,css,javascript,reactjs,fastapi,django,flask"}

def retrival_function(question):
    question=question.lower()
    for key in knowledge_base:
        if key in question:
            return knowledge_base[key]
    return "I don't know"

def ask_llm(question):
    context=retrival_function(question)
    sys_prompt=f""" answer the question in a good manner. If you don't know the answer, say "I don't know". Here is some context that might help: {context}"""
    system_message={
        "role": "system",
        "content": sys_prompt
    }
    message={
        "role": "user",
        "content": question
    }
    messages = [system_message, message]
    response = client.chat.completions.create(model=model, messages=messages)
    answer=response.choices[0].message.content
    return answer
question = "What is the  skills of ravi?"
answer = ask_llm(question)
print(answer)