import os
from pathlib import Path 
from dotenv import load_dotenv
from groq import Groq
from time import sleep
load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("api key nahi mili bhai")
client= Groq(api_key=my_api_key)
model="llama-3.3-70b-versatile"
jd=""" # Software Development Engineer I (SDE-1)

We are looking for a passionate **Software Development Engineer I (SDE-1)** to build scalable, high-quality software and solve challenging engineering problems.

### Required Skills

* Strong knowledge of **Data Structures & Algorithms (DSA)**.
* Proficiency in **Python, Java, C++, or JavaScript**.
* Solid understanding of **Object-Oriented Programming (OOP)**.
* Good knowledge of **DBMS, SQL, Operating Systems, and Computer Networks**.
* Experience with **Git** and version control.
* Understanding of **REST APIs** and backend development.
* Familiarity with **system design fundamentals** and software engineering best practices.
* Strong problem-solving, debugging, and analytical skills.
* Excellent communication and teamwork abilities.

### Preferred

* Experience with **FastAPI, Spring Boot, Django, Node.js, or React**.
* Knowledge of **AWS/GCP/Azure**, Docker, CI/CD, and basic microservices.
* Personal projects, internships, or open-source contributions are a plus.
"""
resume=""" # Rahul Sharma

**Software Development Engineer (SDE-1)**

📧 [rahul.sharma@email.com](mailto:rahul.sharma@email.com) | 📱 +91 98765 43210
🔗 LinkedIn: linkedin.com/in/rahulsharma | GitHub: github.com/rahulsharma

## Professional Summary

Passionate Software Development Engineer with a strong foundation in computer science fundamentals and hands-on experience building scalable applications. Proficient in designing efficient algorithms, developing REST APIs, and writing clean, maintainable code. Eager to contribute to high-impact engineering teams and continuously learn modern technologies.

## Technical Skills

* **Programming Languages:** Python, Java, C++, JavaScript
* **Data Structures & Algorithms:** Arrays, Linked Lists, Trees, Graphs, Dynamic Programming, Greedy Algorithms
* **Backend Development:** FastAPI, Spring Boot, Node.js, REST APIs
* **Frontend:** HTML, CSS, JavaScript, React (Basics)
* **Databases:** MySQL, PostgreSQL, MongoDB
* **Cloud & DevOps:** AWS (EC2, S3), Docker, Git, GitHub, CI/CD Basics
* **Computer Science Fundamentals:** OOP, DBMS, Operating Systems, Computer Networks, System Design Fundamentals
* **Testing:** Unit Testing, API Testing (Postman)
* **Tools:** VS Code, Linux, IntelliJ IDEA

## Projects

### E-Commerce Backend API

* Developed RESTful APIs using FastAPI and PostgreSQL.
* Implemented JWT authentication and role-based authorization.
* Optimized database queries, reducing API response time by 35%.

### URL Shortener

* Built a scalable URL shortening service with Redis caching.
* Designed REST APIs and implemented analytics for click tracking.

### Real-Time Chat Application

* Developed a chat application using WebSockets.
* Integrated JWT authentication and persistent message storage.

## Education

**Bachelor of Technology (Computer Science)**
XYZ University | 2026

## Achievements

* Solved **500+ DSA problems** on coding platforms.
* Built **10+ full-stack/backend projects**.
* Active contributor to GitHub with clean and documented repositories.

## Soft Skills

* Problem Solving
* Analytical Thinking
* Communication
* Team Collaboration
* Adaptability
* Continuous Learning
"""
def ask_llm( system_prompt,user_prompt):
    sys_msg={
        "role":"system",
        "content" : system_prompt
    }
    user_msg={
        "role" : "user",
        "content" : user_prompt
    }
    messages=[sys_msg,user_msg]
    response=client.chat.completions.create(model=model,messages=messages)
    answer=response.choices[0].message.content
    return answer
def extract_skill_resume():
    system_prompt =f""" you are professional hr assistent.extract the skill from the candidate resume provided {resume}.only return skill noother filler word"""
    user_prompt=f""" ectract skill from thos resume{resume} """
    return ask_llm(system_prompt,user_prompt)

def extract_skill_jd():
    system_prompt =f""" you are professional hr assistent.extract the skill from the candidate job description provided {jd}.only return skill noother filler word"""
    user_prompt=f""" ectract skill from thos job description{jd} """
    return ask_llm(system_prompt,user_prompt)
def skill_matching (resume,jd):
    system_prompt=""" you are a professional job assistent ,who compare the skill of canditate to skill requires to job description ,and you return a similarity score  in out of 100,and also give two line verdict whether the candidate is good fit or not. do not give more filler word or sentences"""
    user_prompt=f"""compare and match the skills
     jd={jd}
    candidate={candidate}"""
    return ask_llm(system_prompt,user_prompt)
candidate=extract_skill_resume
sleep(2)
jd=extract_skill_jd
sleep(2)
score=skill_matching(candidate,jd)
print (score)



 



#system_prompt=f""" you are a specialized hr assistent , which is secialized in extracting sill from  job description {jd},and resume of candidate { resume}.you should give only skill not filler word"""
#user_prompt=f """ this is my profile {resume} """


