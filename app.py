# =========================
# FILE: app.py
# =========================

from flask import Flask, request, render_template
from pdfminer.high_level import extract_text
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

skills_db = [
    "python",
    "java",
    "c++",
    "javascript",
    "html",
    "css",
    "react",
    "node",
    "flask",
    "django",
    "sql",
    "mongodb",
    "machine learning",
    "data science",
    "deep learning",
    "tensorflow",
    "git",
    "docker",
    "rest api"
]


def allowed_file(filename):

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_skills(text):

    text = text.lower()

    found = []

    for skill in skills_db:

        if skill in text:
            found.append(skill)

    return list(set(found))


def resume_score(skills):

    return int((len(skills) / len(skills_db)) * 100)


def ats_score(resume_text, job_desc):

    resume_words = set(
        re.findall(r'\w+', resume_text.lower())
    )

    job_words = set(
        re.findall(r'\w+', job_desc.lower())
    )

    match = resume_words.intersection(job_words)

    if len(job_words) == 0:
        return 0

    return int((len(match) / len(job_words)) * 100)


def skill_gap(resume_skills, job_desc):

    missing = []

    for skill in skills_db:

        if skill in job_desc.lower() and \
           skill not in resume_skills:

            missing.append(skill)

    return missing


def suggestions(score, missing):

    tips = []

    if score < 40:

        tips.append(
            "Add more technical skills to your resume."
        )

    if missing:

        tips.append(
            "Consider learning these skills: " +
            ", ".join(missing)
        )

    tips.append(
        "Add GitHub links to your projects."
    )

    tips.append(
        "Use action verbs like Developed, Built, Implemented."
    )

    tips.append(
        "Mention measurable achievements in projects."
    )

    return tips


@app.route("/", methods=["GET", "POST"])

def home():

    skills = []
    score = None
    ats = None
    missing = []
    tips = []

    if request.method == "POST":

        file = request.files["resume"]

        job_desc = request.form["job_desc"]

        if file and allowed_file(file.filename):

            path = os.path.join(
                UPLOAD_FOLDER,
                file.filename
            )

            file.save(path)

            text = extract_text(path)

            skills = extract_skills(text)

            score = resume_score(skills)

            ats = ats_score(text, job_desc)

            missing = skill_gap(skills, job_desc)

            tips = suggestions(score, missing)

    return render_template(
        "index.html",
        skills=skills,
        score=score,
        ats=ats,
        missing=missing,
        tips=tips
    )


if __name__ == "__main__":
    app.run(debug=True)
