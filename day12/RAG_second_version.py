import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq



import numpy as np
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')#384
text="Ravi Tiwari is a software engineer with expertise in Python, JavaScript, and cloud computing. He has experience working on web development projects and is passionate about open-source contributions."
result = model.encode(text)
print(result.shape)
print(result[:10])
load_dotenv()

def cosine_similarity(a,b):
    return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))
t1="there is 24 paid leaves in a year"
t2=" i love pizza"
a1=model.encode(t1)
a2=model.encode(t2)
print(cosine_similarity(a1,a2))

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=my_api_key)

model = "openai/gpt-oss-20b"
