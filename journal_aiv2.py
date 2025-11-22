import os
import json
import glob
from datetime import datetime
from openai import OpenAI

# --- CONFIGURATION ---
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',
)
MODEL = "llama3"

JOURNAL_DIR = "journal_entries"
PROFILE_FILE = "user_profile.json"
SKILLS_FILE = "skills_tracker.json"
README_FILE = "README.md"

# --- PART 1: PROFILE & CONTEXT ---
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r', encoding="utf-8") as f:
            return json.load(f)
    return None

def create_profile():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("╔════════════════════════════════════════╗")
    print("║       CAREER ARCHITECT SETUP           ║")
    print("╚════════════════════════════════════════╝")
    
    name = input("Name: ")
    print("\n🔮 LONG TERM GOAL (Be specific, e.g., 'HFT Quant Dev' or 'CISO'):")
    long_term = input("> ")
    
    print("\n🔥 CURRENT FOCUS (e.g., 'Dynamic Programming' or 'Network Defense'):")
    short_term = input("> ")
    
    profile = {
        "name": name, 
        "long_term": long_term, 
        "short_term": short_term,
        "joined": datetime.now().strftime("%Y-%m-%d")
    }
    with open(PROFILE_FILE, 'w', encoding="utf-8") as f:
        json.dump(profile, f, indent=4)
    return profile

# --- PART 2: THE ALIGNED QUESTION ENGINE ---
def get_aligned_question(topic, profile):
    print(f"\n🤔 \033[1mConnecting '{topic}' to '{profile['long_term']}'...\033[0m")
    prompt = f"""
    Context:
    - User's Long Term Career Goal: {profile['long_term']}
    - User's Current Learning Topic: {topic}
    
    Task:
    Act as a Senior Mentor in the field of {profile['long_term']}.
    Ask ONE deep, complex interview question that forces the user to apply "{topic}" specifically to the problems faced in "{profile['long_term']}".
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except:
        return f"How does {topic} apply to being a {profile['long_term']}?"

def grade_aligned_answer(topic, question, answer, profile):
    print("\n⚖️  \033[1mANALYZING GAP TO GOAL...\033[0m")
    prompt = f"""
    You are a Hiring Manager for a {profile['long_term']} role.
    Topic: {topic} | Question: {question} | Candidate Answer: "{answer}"
    
    Return JSON ONLY:
    {{
        "score": (0-10),
        "gap_analysis": "Critique referencing Senior {profile['long_term']} standards.",
        "executive_rewrite": "Rewrite the answer to be shorter, sharper, and more professional."
    }}
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"score": 5, "gap_analysis": "AI Error", "executive_rewrite": "N/A"}

# --- PART 3: SKILL TRACKER (RPG) ---
def update_skill_db(topic, score, goal_role):
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, 'r', encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
        
    key = topic.lower().replace(" ", "_")
    if key not in data:
        data[key] = {"name": topic, "xp": 0, "level": "Novice", "aligned_to": goal_role}
        
    gained_xp = 10 + (score * 3) 
    data[key]["xp"] += gained_xp
    
    xp = data[key]["xp"]
    if xp > 100: data[key]["level"] = "Apprentice" 
    if xp > 300: data[key]["level"] = "Specialist"
    if xp > 600: data[key]["level"] = "Authority"
    
    with open(SKILLS_FILE, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    return data[key]["level"], gained_xp

# --- PART 4: PORTFOLIO AUTOMATOR (README & SUMMARY) ---
def get_executive_summary(profile):
    files = sorted(glob.glob(os.path.join(JOURNAL_DIR, "*.md")))[-3:]
    if not files: return "New candidate. No data logged yet."
    
    content_dump = ""
    for f in files:
        with open(f, 'r', encoding="utf-8") as file: content_dump += file.read() + "\n"
        
    print("\n📊 \033[1mGENERATING EXECUTIVE SUMMARY FOR README...\033[0m")
    prompt = f"""
    Write a 3-sentence performance review for {profile['name']} based on these logs.
    Highlight their technical growth toward being a {profile['long_term']}.
    Use impressive, corporate language.
    Logs: {content_dump}
    """
    try:
        res = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
        return res.choices[0].message.content.strip()
    except:
        return "User is consistently logging technical progress."

def generate_readme(profile, summary):
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, 'r', encoding="utf-8") as f: skills = json.load(f)
    else: skills = {}
    
    skill_rows = ""
    if skills:
        sorted_skills = sorted(skills.items(), key=lambda x: x[1]['xp'], reverse=True)
        for key, data in sorted_skills[:5]: 
            skill_rows += f"| {data['name']} | {data['level']} | {data['xp']} XP |\n"
    else:
        skill_rows = "| Pending | Novice | 0 XP |"

    file_count = len(glob.glob(os.path.join(JOURNAL_DIR, "*.md")))
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M")

    markdown = f"""
# 🚀 {profile['name']}'s Engineering Journal

> "Documenting the journey to becoming a **{profile['long_term']}**."

### 📋 Executive Summary
{summary}

---

### 🧠 Core Competency Matrix
| Skill / Concept | Mastery Level | Experience Points |
| :--- | :--- | :--- |
{skill_rows}

---

### 📊 Activity Monitor
| Metric | Status |
| :--- | :--- |
| **Current Focus** | {profile['short_term']} |
| **Total Logs** | {file_count} entries |
| **Last Update** | {last_update} |

---
### 📂 Recent Daily Logs
*Browse the `/journal_entries` folder for deep-dives.*
    """
    with open(README_FILE, 'w', encoding="utf-8") as f: f.write(markdown)
    print(f"✅ README.md updated.")

# --- MAIN LOOP ---
def main():
    if not os.path.exists(JOURNAL_DIR): os.makedirs(JOURNAL_DIR)
    
    # 1. Setup
    profile = load_profile()
    if not profile: profile = create_profile()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 2. Input
    print(f"\n🤖 \033[1mMENTOR:\033[0m Welcome, {profile['name']}. What did you learn today?")
    topic = input("TOPIC > ")
    
    # 3. The Deep Question
    question = get_aligned_question(topic, profile)
    print(f"\n🎯 \033[1mSCENARIO CHALLENGE:\033[0m")
    print(question)
    
    print("\n(Type your answer as if you are in the interview)")
    answer = input("ANSWER > ")
    
    # 4. The Grading
    result = grade_aligned_answer(topic, question, answer, profile)
    
    print(f"\n🏆 \033[1mSCORE: {result['score']}/10\033[0m")
    print(f"⚠️ \033[1mGAP ANALYSIS:\033[0m {result['gap_analysis']}")
    print(f"🚀 \033[1mMANAGER MODE:\033[0m \"{result['executive_rewrite']}\"")
    
    # 5. Save Data
    level, xp = update_skill_db(topic, result['score'], profile['long_term'])
    print(f"\n✨ Skill '{topic}' updated to {level} (+{xp} XP)")
    
    # 6. Journal File
    date_str = datetime.now().strftime("%Y-%m-%d")
    md_content = f"""
    # Log: {date_str}
    ## Topic: {topic}
    **Goal Alignment:** {profile['long_term']}
    ### ❓ The Challenge
    {question}
    ### 🗣️ My Response
    {answer}
    ### 🔍 Mentor Feedback
    * **Score:** {result['score']}/10
    * **The Gap:** {result['gap_analysis']}
    * **Pro Rewrite:** {result['executive_rewrite']}
        """
    filename = os.path.join(JOURNAL_DIR, f"{date_str}.md")
    with open(filename, "w", encoding="utf-8") as f: f.write(md_content)
    print(f"✅ Log saved to {filename}")
    
    # 7. GENERATE PORTFOLIO UPDATE
    summary = get_executive_summary(profile)
    generate_readme(profile, summary)
    print(f"\n🎉 \033[1mALL SYSTEMS UPDATED.\033[0m Push to GitHub now.")

if __name__ == "__main__":
    main()