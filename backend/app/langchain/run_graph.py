from backend.app.langchain.graph import resume_graph

jd_text = open('D:\\Machine_learning\\Projects\\Hackathon1\\backend\\app\\langchain\\sample_jd_1.pdf', "rb").read()
resume_text = open('D:\\Machine_learning\\Projects\\Hackathon1\\backend\\app\\langchain\\RK_Resume.pdf', "rb").read()

result = resume_graph.invoke({
    "jd_text": jd_text,
    "resume_text": resume_text
})

print(result["score"])
print(result["suggestions"])