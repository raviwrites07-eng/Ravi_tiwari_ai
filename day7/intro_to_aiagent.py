import os
import re
from time import sleep
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("api key kahan hai bhai?")

client = Groq(api_key=my_api_key)
model = "llama-3.3-70b-versatile"


def get_product_price(product):
    if product == "iphone 17":
        return 1000
    elif product == "macbook pro 2024":
        return 2000
    else:
        return 0


def calculator(expression):
    try:
        result = eval(expression)
        return result
    except:
        return "Error: Invalid expression"


tools = {
    "get_product_price": get_product_price,
    "calculator": calculator
}


system_prompt = """
you are a shopping assistant.

you have these tools:

get_product_price(product)
calculator(expression)

IMPORTANT:

call tools like this:

Action: get_product_price("iphone 17")
Action: calculator(2+3)

Never call tools like this:

get_product_price(product="iphone 17")
calculator(expression="2+3")

Rules:

1. Think carefully.
2. If a tool is needed, output ONLY one Action.
3. Stop immediately after Action.
4. Wait for Observation.
5. Continue reasoning.
6. When everything is complete write:

Final Answer: ...
"""


question = """
I have 5000 rupee.
I want to buy iphone 17.
After buying how much money will I have left?
"""


def run_agent(question):

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    for step in range(10):

        print("----------------")
        print("Step", step + 1)
        print("----------------")

        response = client.chat.completions.create(
            model=model,
            messages=messages
        )

        answer = response.choices[0].message.content

        print("\nAssistant:\n")
        print(answer)

        # stop if final answer generated
        if "final answer:" in answer.lower():
            break

        # extract tool
        match = re.search(
            r'Action:\s*(\w+)\((.*?)\)',
            answer,
            re.IGNORECASE
        )

        if not match:
            print("No action found.")
            break

        tool_name = match.group(1)
        argument = match.group(2).strip().strip('"')

        print("\nTool :", tool_name)
        print("Argument :", argument)

        # execute tool
        if tool_name in tools:
            result = tools[tool_name](argument)
        else:
            result = f"Unknown tool : {tool_name}"

        print("Observation :", result)

        # append assistant response
        messages.append({
            "role": "assistant",
            "content": answer
        })

        # append observation
        messages.append({
            "role": "user",
            "content": f"Observation: {result}"
        })

        sleep(2)


run_agent(question)