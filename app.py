from flask import Flask, request, render_template_string
from pdfminer.high_level import extract_text
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

skills_db = [
"python","java","c++","javascript","html","css","react",
"node","flask","django","sql","mongodb","machine learning",
"data science","deep learning","tensorflow","git","docker"
]

HTML_PAGE = """

<!DOCTYPE html>
<html>

<head>

<title>AI Resume Analyzer</title>

<style>

body{
font-family: Arial;
background:#eef2f7;
text-align:center;
padding:40px;
}

.container{
background:white;
padding:30px;
border-radius:10px;
width:65%;
margin:auto;
box-shadow:0 0 10px rgba(0,0,0,0.1);
}

h1{
color:#333;
}

input,textarea{
width:80%;
padding:10px;
margin:10px;
}

button{
padding:10px 20px;
background:#007bff;
border:none;
color:white;
cursor:pointer;
border-radius:5px;
}

button:hover{
background:#0056b3;
}

.result{
margin-top:30px;
}

ul{
list-style:none;
}

</style>

</head>

<body>

<div class="container">

<h1>AI Resume Analyzer</h1>

<form method="POST" enctype="multipart/form-data">

<input type="file" name="resume" required>

<br>

<textarea name="job_desc" placeholder="Paste Job Description Here"></textarea>

<br>

<button type="submit">Analyze Resume</button>

</form>

{% if score is not none %}

<div class="result">

<h2>Resume Score: {{score}}%</h2>

<h2>ATS Match Score: {{ats}}%</h2>

<h3>Detected Skills</h3>

<ul>
{% for skill in skills %}
<li>{{skill}}</li>
{% endfor %}
</ul>

<h3>Missing Skills (Skill Gap)</h3>

<ul>
{% for skill in missing %}
<li>{{skill}}</li>
{% endfor %}
</ul>

<h3>Suggestions to Improve Resume</h3>

<ul>
{% for tip in tips %}
<li>{{tip}}</li>
{% endfor %}
</ul>

</div>

{% endif %}

</div>

</body>

</html>

"""


def extract_skills(text):

    text = text.lower()
    found = []

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return list(set(found))


def resume_score(skills):

    return int((len(skills)/len(skills_db))*100)


def ats_score(resume_text, job_desc):

    resume_words = set(re.findall(r'\w+',resume_text.lower()))
    job_words = set(re.findall(r'\w+',job_desc.lower()))

    match = resume_words.intersection(job_words)

    if len(job_words)==0:
        return 0

    score = int((len(match)/len(job_words))*100)

    return score


def skill_gap(resume_skills, job_desc):

    job_words = job_desc.lower()

    missing = []

    for skill in skills_db:

        if skill in job_words and skill not in resume_skills:
            missing.append(skill)

    return missing


def suggestions(score, missing):

    tips=[]

    if score<40:
        tips.append("Add more technical skills to your resume.")

    if missing:
        tips.append("Consider learning these missing skills: " + ", ".join(missing))

    tips.append("Add real projects related to your skills.")

    tips.append("Include GitHub links to your projects.")

    tips.append("Use action words like Developed, Built, Implemented.")

    return tips


@app.route("/",methods=["GET","POST"])

def home():

    skills=[]
    score=None
    ats=None
    missing=[]
    tips=[]

    if request.method=="POST":

        file=request.files["resume"]
        job_desc=request.form["job_desc"]

        path=os.path.join(UPLOAD_FOLDER,file.filename)

        file.save(path)

        text=extract_text(path)

        skills=extract_skills(text)

        score=resume_score(skills)

        ats=ats_score(text,job_desc)

        missing=skill_gap(skills,job_desc)

        tips=suggestions(score,missing)

    return render_template_string(
        HTML_PAGE,
        skills=skills,
        score=score,
        ats=ats,
        missing=missing,
        tips=tips
    )


if __name__=="__main__":
    app.run(debug=True)