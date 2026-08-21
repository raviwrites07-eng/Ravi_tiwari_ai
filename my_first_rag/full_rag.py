import os

from pathlib import Path

from dotenv import load_dotenv
from groq import Groq



import numpy as np
from sentence_transformers import SentenceTransformer
load_dotenv()
model = SentenceTransformer('all-MiniLM-L6-v2')#384
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=my_api_key)

groqmodel = "openai/gpt-oss-20b"
documents = [
    "The quick brown fox jumps over the lazy dog.",
    "The rain in Spain stays mainly in the plain.",
    "To be or not to be, that is the question.",
    "All that glitters is not gold.",
    "A journey of a thousand miles begins with a single step.",
    "The pen is mightier than the sword.",]
document_embeddings=model.encode(documents)
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve(qembedding):
    scores=[]
    for i,document in enumerate(document_embeddings):
        score=cosine_similarity(qembedding,document)
        scores.append((score,documents[i]))
    scores.sort(reverse=True)    
    return scores[0]
query="mind is more powerful than physical power"
qembedding=model.encode(query)
score,context=retrieve(qembedding)
def ask_llm(query,context):
    #context=retrival_function(question)
    sys_prompt=f""" You are an assistant that explains retrieved information.

Retrieved context:
{context}

Your task:
- Explain the retrieved context clearly in your own words.
- Use the user's query only to understand why this context
  was retrieved.
- Do NOT explain the user's query itself.
- Do NOT change the meaning of the retrieved context.
- If the context is insufficient to explain anything useful,
  say "I don't know."

Give a concise explanation of the retrieved context in 3 lines."""
    system_message={
        "role": "system",
        "content": sys_prompt
    }
    message={
        "role": "user",
        "content": query
    }
    messages = [system_message, message]
    response = client.chat.completions.create(model=groqmodel, messages=messages)
    answer=response.choices[0].message.content
    return answer

answer=ask_llm(query,context)
print(answer)
