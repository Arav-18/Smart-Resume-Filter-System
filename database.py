import sqlite3

# Function to initialize the database and create table
def init_db():
    conn = sqlite3.connect('resume_data.db')  # creates resume_data.db
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_score INTEGER,
            top_skills TEXT,
            improvement_tips TEXT,
            recommendation TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert analysis result
def insert_result(score, skills, tips, recommendation):
    conn = sqlite3.connect('resume_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resume_results (match_score, top_skills, improvement_tips, recommendation)
        VALUES (?, ?, ?, ?)
    ''', (score, ', '.join(skills), ', '.join(tips), recommendation))
    conn.commit()
    conn.close()
def get_all_results():
    conn = sqlite3.connect('resume_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT match_score, top_skills, improvement_tips, recommendation FROM resume_results")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Optional: Manual test to run this file alone
if __name__ == "__main__":
    init_db()
    print("Database connected and table created.")
    