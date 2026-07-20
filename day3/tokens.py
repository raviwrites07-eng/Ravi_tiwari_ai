import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("api key kahan hai bhai?")
client = Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
role="user"
prompt1="hii"
prompt2="explain time travel in detail"
prompt3="write a 1000 word essay on machine learning"
prompts=[prompt1, prompt2, prompt3]
for prompt in prompts:
    message={"role": role, "content": prompt}
    messages=[message]
    response=client.chat.completions.create(model=model, messages=messages,temperature=0.7)
    answer=response.choices[0].message.content
    #print(f"Answer: {answer}")
    print(f"prompt:{response.usage.prompt_tokens}")
    print(f"completion:{response.usage.completion_tokens}")