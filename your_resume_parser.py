import re
import logging

# Disable pdfminer warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)


# Skill set for matching
SKILL_KEYWORDS = [
    'python', 'java', 'sql', 'html', 'css', 'flask', 'django', 'react',
    'javascript', 'git', 'github', 'mysql', 'mongodb', 'c++', 'c',
    'data analysis', 'machine learning', 'communication', 'problem solving'
]

# Extract text from resume file (.txt or .pdf)
def extract_text_from_resume(file):
    filename = file.filename.lower()

    if filename.endswith('.txt') or filename.endswith('.pdf'):
        content = file.read().decode('utf-8', errors='ignore') if filename.endswith('.txt') else ""
        if filename.endswith('.pdf'):
            from io import StringIO
            from pdfminer.high_level import extract_text_to_fp
            output_string = StringIO()
            extract_text_to_fp(file, output_string)
            content = output_string.getvalue()

        # Normalize punctuation spacing
        content = content.replace("•", "\n- ").replace("●", "\n- ").replace("|", " ")
        content = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', content)
        content = re.sub(r'\.([^\n])', r'.\n\1', content)
        content = re.sub(r'\n+', '\n', content)
        content = re.sub(r'\s{2,}', ' ', content)

        # Add extra newlines before common sections
        headers = ['SUMMARY', 'PROJECTS', 'EDUCATION', 'SKILLS', 'CERTIFICATIONS', 'EXPERIENCE', 'LANGUAGES']
        for h in headers:
            content = re.sub(rf'({h})', r'\n\n\1', content, flags=re.IGNORECASE)

        return content.strip()

    else:
        return ""

# Clean and tokenize text into a set of normalized lowercase words
def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+\#]', ' ', text)
    tokens = set(text.split())
    return tokens

# Calculate the match score based on skill keywords
def match_score(resume_text, jd_text):
    resume_tokens = clean_and_tokenize(resume_text)
    jd_tokens = clean_and_tokenize(jd_text)

    matched = [skill for skill in SKILL_KEYWORDS if all(word in resume_tokens for word in skill.split()) and
                                                     all(word in jd_tokens for word in skill.split())]
    total = [skill for skill in SKILL_KEYWORDS if all(word in jd_tokens for word in skill.split())]

    if not total:
        return 0
    return round((len(matched) / len(total)) * 100, 2)

# Get top matched skills from resume and JD
def get_top_skills(resume_text, jd_text):
    resume_tokens = clean_and_tokenize(resume_text)
    jd_tokens = clean_and_tokenize(jd_text)

    return [
        skill for skill in SKILL_KEYWORDS
        if all(word in resume_tokens for word in skill.split()) and
           all(word in jd_tokens for word in skill.split())
    ]

# Generate improvement tips based on missing skills — returns a LIST
def generate_tips(resume_text, jd_text):
    resume_tokens = clean_and_tokenize(resume_text)
    jd_tokens = clean_and_tokenize(jd_text)

    missing = [
        skill for skill in SKILL_KEYWORDS
        if all(word in jd_tokens for word in skill.split()) and
           not all(word in resume_tokens for word in skill.split())
    ]

    tips = []

    if missing:
        tips.append(f"Try adding these skills: {', '.join(missing)}.")

    if len(resume_tokens) < 150:
        tips.append("Your resume seems short. Consider adding more content like projects, achievements, or tools used.")

    tech_skills = [
        skill for skill in SKILL_KEYWORDS
        if skill in resume_tokens and skill not in ['communication', 'problem solving']
    ]
    if len(tech_skills) < 3:
        tips.append("Include more technical skills relevant to your domain (e.g., databases, frameworks, languages).")

    if not any(keyword in resume_text.lower() for keyword in ['project', 'developed', 'built']):
        tips.append("Mention at least one project you've worked on or technologies you've used.")

    if not tips:
        tips.append("Great match! Minimal suggestions.")

    return tips  # return as list

# Generate a recommendation based on the match score
def generate_recommendation(score):
    if score > 85:
        return "Excellent match – you're highly aligned with this role!"
    elif score > 65:
        return "Strong fit – just a few improvements could strengthen your application."
    elif score > 45:
        return "Moderate fit – consider tailoring your resume to the job requirements."
    else:
        return "Low match – revise your skills, experiences, and keywords to better align with the role."

# Highlight matched skills in resume preview
def highlight_skills(text, skills):
    for skill in skills:
        pattern = r'\b' + re.escape(skill) + r'\b'
        text = re.sub(pattern, r'<mark style="background-color: #ffd54f; color: black;">\g<0></mark>', text, flags=re.IGNORECASE)
    return text

# Main function to analyze resume and job description
def analyze_resume(resume_file, jd_file):
    resume_text = extract_text_from_resume(resume_file)
    jd_text = extract_text_from_resume(jd_file)

    if not resume_text or not jd_text:
        return None, [], [], "Invalid input", ""

    score = match_score(resume_text, jd_text)
    top_skills = get_top_skills(resume_text, jd_text)
    improvement_tips = generate_tips(resume_text, jd_text)
    recommendation = generate_recommendation(score)
    highlighted_resume = highlight_skills(resume_text, top_skills)

    return score, top_skills, improvement_tips, recommendation, highlighted_resume
