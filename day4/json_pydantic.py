import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
from pydantic import BaseModel
class TicketInfo(BaseModel): 
    name: str
    product: str
    email: str
    application_no: str
    address: str
schema=TicketInfo.model_json_schema()   
responce_format={
"type": "json_object"
    
}
system_prompt=f"""extract in information based on ticket schema and return in json format{schema}"""

message_system={
    "role": "system", "content": system_prompt
}
my_api_key=os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("api key kahan hai bhai?")
client = Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
role="user"
text ="hello my name is ravi tiwari i buy i phone which came across faulty my mail id is ravi123@gmail.com ,i am a good boy .my application no is 12345432.my current address is delhi "
prompt=f"""this is a custemer complain please extract the following information and return in JSON format{text}"""
message={"role": role, "content": prompt}
messages=[message_system, message]
response=client.chat.completions.create(model=model, messages=messages,temperature=0.7,response_format=responce_format)
answer=response.choices[0].message.content
print(f"Answer: {answer}")
import json
raw_json=answer
data_file=json.loads(raw_json)
ticket_info=TicketInfo(**data_file)
print(ticket_info.name)
print(ticket_info.product)
print(ticket_info.email)
print(ticket_info.application_no)
print(ticket_info.address)