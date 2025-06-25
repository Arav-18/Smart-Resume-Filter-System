from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import csv
import io
from your_resume_parser import analyze_resume  # Updated import
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# ✅ Create DB if not exists
def init_db():
    conn = sqlite3.connect('resume_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER,
            skills TEXT,
            tips TEXT,
            recommendation TEXT,
            resume_text TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Insert result into DB
def insert_result(score, skills, tips, recommendation):
    # Convert tip list to a single string before saving to DB
    if isinstance(tips, list):
        tips = '\n'.join(tips)

    conn = sqlite3.connect('resume_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO resume_results (score, skills, tips, recommendation) VALUES (?, ?, ?, ?)',
                   (score, skills, tips, recommendation))
    conn.commit()
    conn.close()


# ✅ Delete record
@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    conn = sqlite3.connect('resume_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resume_results WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# ✅ Home page
@app.route('/')
def home():
    return render_template('upload.html')

# ✅ Resume Analysis
@app.route('/upload', methods=['POST'])
def upload_resume():
    resume_file = request.files['resume']
    jd_file = request.files['jd']

    # ✅ Use enhanced analyzer
    score, top_skills, improvement_tips, recommendation, highlighted_resume = analyze_resume(resume_file, jd_file)

    # ✅ Insert result into DB
    top_skills_str = ", ".join(top_skills)
    insert_result(score, top_skills_str, improvement_tips, recommendation)

    # ✅ Render result page
    return render_template(
        'analyze.html',
        score=score,
        matched_skills=top_skills,
        improvement_tips=improvement_tips,
        recommendation=recommendation,
        resume_text=highlighted_resume  # resume with highlights
    )

# ✅ Recruiter Dashboard
@app.route('/dashboard')
def dashboard():
    score_filter = request.args.get('score_filter')
    conn = sqlite3.connect('resume_data.db')
    cursor = conn.cursor()

    if score_filter:
        cursor.execute("SELECT * FROM resume_results WHERE score >= ?", (score_filter,))
    else:
        cursor.execute("SELECT * FROM resume_results")
    
    results = cursor.fetchall()
    conn.close()

    # 📊 Prepare pie chart data
    chart_data = [0, 0, 0, 0]  # Excellent, Strong, Moderate, Low
    for row in results:
        score = row[1]
        if score >= 85:
            chart_data[0] += 1
        elif score >= 65:
            chart_data[1] += 1
        elif score >= 45:
            chart_data[2] += 1
        else:
            chart_data[3] += 1

    return render_template("dashboard.html", results=results, chart_data=chart_data)


# ✅ CSV Export
@app.route('/export')
def export_csv():
    conn = sqlite3.connect('resume_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resume_results")
    results = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Score', 'Skills', 'Tips', 'Recommendation'])
    writer.writerows(results)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv',
                     as_attachment=True, download_name='resume_results.csv')

# ✅ Start app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
