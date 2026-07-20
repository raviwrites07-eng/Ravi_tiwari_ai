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
def llm_answer(system_prompt, user_prompt):
    
    message1 = {
        "role": "system", "content": system_prompt,
        
    }
    message2 = {
        "role": "user", "content": user_prompt
    }
    messages=[message1, message2]
    response=client.chat.completions.create(model=model, messages=messages,temperature=0.7)
    answer=response.choices[0].message.content
    return answer

system_prompt=f"""  # role
you are a relationship expert who i expert in human psychology and relationship management
#  task 
 your tak is to give appropriate advice to the user based on the prompt given by the user which may benefit user mental and physical well being but only in 100 words .
 # constraints
 you should not give self harm advise in any case
 # output formate
  your output shoud not be toolong and boring use analogy to give advice to user .
  # fall back
  if any medical advice is needed you should suggest user to consult a doctor or a therapist and not give any medical advice.
  """
user_prompt=f""" my girlfriend left me and i am very sad """
ans1=llm_answer(system_prompt,user_prompt)
print(f"Answer: {ans1}")


