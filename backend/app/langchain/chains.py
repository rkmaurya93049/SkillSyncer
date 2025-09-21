from langchain.agent import get_resume_agent

agent = get_resume_agent()
response = agent.invoke("Evaluate this resume against the JD for Python Developer")

print(response)
