import os
import json
import time
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

# --- PART 1: PROFILE & CONTEXT ---
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
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
    with open(PROFILE_FILE, 'w',encoding="utf-8") as f:
        json.dump(profile, f, indent=4)
    return profile

# --- PART 2: THE ALIGNED QUESTION ENGINE ---
def get_aligned_question(topic, profile):
    """
    Generates a question that bridges the Topic -> Long Term Goal.
    """
    print(f"\n🤔 \033[1mConnecting '{topic}' to '{profile['long_term']}'...\033[0m")
    
    prompt = f"""
    Context:
    - User's Long Term Career Goal: {profile['long_term']}
    - User's Current Learning Topic: {topic}
    
    Task:
    Act as a Senior Mentor in the field of {profile['long_term']}.
    Ask ONE deep, complex interview question that forces the user to apply "{topic}" specifically to the problems faced in "{profile['long_term']}".
    
    Do not ask generic questions. Make it a scenario.
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
    """
    Grades based on the specific requirements of the Career Goal.
    """
    print("\n⚖️  \033[1mANALYZING GAP TO GOAL...\033[0m")
    
    prompt = f"""
    You are a Hiring Manager for a {profile['long_term']} role.
    
    Topic: {topic}
    Question: {question}
    Candidate Answer: "{answer}"
    
    Evaluate this candidate based on the standards of a {profile['long_term']}.
    
    Return JSON ONLY:
    {{
        "score": (0-10),
        "gap_analysis": "Your answer was [good/bad], but a Senior {profile['long_term']} would have also mentioned [Missing Concept].",
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
        with open(SKILLS_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}
        
    key = topic.lower().replace(" ", "_")
    if key not in data:
        data[key] = {"name": topic, "xp": 0, "level": "Novice", "aligned_to": goal_role}
        
    # XP Calculation
    gained_xp = 10 + (score * 3) # Heavy weighting on quality
    data[key]["xp"] += gained_xp
    
    # Level Logic
    xp = data[key]["xp"]
    if xp > 100: data[key]["level"] = "Apprentice" 
    if xp > 300: data[key]["level"] = "Specialist"
    if xp > 600: data[key]["level"] = "Authority"
    
    with open(SKILLS_FILE, 'w',encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    return data[key]["level"], gained_xp

def show_dashboard(profile):
    if not os.path.exists(SKILLS_FILE): return
    with open(SKILLS_FILE, 'r',encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"\n📊 \033[1mPATH TO: {profile['long_term'].upper()}\033[0m")
    print(f"{'SKILL':<20} | {'LEVEL':<12} | {'XP':<5}")
    print("-" * 45)
    for k, v in sorted(data.items(), key=lambda item: item[1]['xp'], reverse=True):
        print(f"{v['name']:<20} | {v['level']:<12} | {v['xp']:<5}")
    print("-" * 45)

# --- MAIN LOOP ---
def main():
    # 1. Setup
    profile = load_profile()
    if not profile: profile = create_profile()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    show_dashboard(profile)
    
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
    if not os.path.exists(JOURNAL_DIR): os.makedirs(JOURNAL_DIR)
    with open(filename, "w",encoding="utf-8") as f:
        f.write(md_content)
    print(f"✅ Saved to {filename}")

if __name__ == "__main__":
    main()