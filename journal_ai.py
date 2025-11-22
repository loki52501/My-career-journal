import os
import sys
import glob
from datetime import datetime
from openai import OpenAI

# --- CONFIGURATION ---
# Use Ollama (Local/Free) or change to OpenAI if you prefer
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',
)
MODEL = "llama3" 

JOURNAL_DIR = "journal_entries"

def ensure_dir():
    if not os.path.exists(JOURNAL_DIR):
        os.makedirs(JOURNAL_DIR)

def get_last_session_goals():
    """
    Reads the most recent markdown file to find 'Goals for Tomorrow'.
    """
    files = sorted(glob.glob(os.path.join(JOURNAL_DIR, "*.md")))
    if not files:
        return "No previous records found. This is your first entry."
    
    last_file = files[-1]
    with open(last_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Simple parsing to find the Goals section
    if "## 🎯 Goals for Tomorrow" in content:
        return content.split("## 🎯 Goals for Tomorrow")[1].strip()
    else:
        return "goals were not clearly recorded last time."

def chat_with_mentor(previous_goals):
    """
    Conducts the interview and returns the answers.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n📅 \033[1mJOURNAL SESSION: {date_str}\033[0m")
    print("-" * 50)
    
    # 1. Review Yesterday
    print(f"\n🤖 \033[1mAI MENTOR:\033[0m Welcome back. Let's look at your previous goals:\n")
    print(f"\033[3m{previous_goals}\033[0m\n")
    print("Did you achieve these? (Be honest, I'm recording this).")
    review = input("YOU > ")

    # 2. Learnings
    print(f"\n🤖 \033[1mAI MENTOR:\033[0m Understood. Now, what is the most valuable thing you learned today?")
    learnings = input("YOU > ")

    # 3. Brain Dump
    print(f"\n🤖 \033[1mAI MENTOR:\033[0m Any blockers, frustrations, or wins you want to log?")
    thoughts = input("YOU > ")

    # 4. Setting Tomorrow's Goals
    print(f"\n🤖 \033[1mAI MENTOR:\033[0m Finally, list your top 3 priorities for tomorrow.")
    goals = input("YOU > ")

    return review, learnings, thoughts, goals

def generate_markdown(review, learnings, thoughts, goals):
    """
    Formats the user's raw input into a beautiful Markdown document.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # We ask the AI to summarize/polish the text slightly for the record
    prompt = f"""
    Take these raw journal inputs and format them into a clean Markdown entry.
    Use professional, concise English.
    
    Inputs:
    - Review of yesterday: {review}
    - New Learnings: {learnings}
    - General Thoughts: {thoughts}
    - Goals for Tomorrow: {goals}
    
    Output Format:
    # Journal Entry: {date_str}
    ## 🔍 Accountability Check
    [Summary of review]
    
    ## 🧠 Knowledge Log
    [Bullet points of learnings]
    
    ## 📝 Notes
    [Summary of thoughts]
    
    ## 🎯 Goals for Tomorrow
    [Bulleted list of goals]
    """
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def save_entry(content):
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(JOURNAL_DIR, f"{date_str}.md")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\n✅ Entry saved to {filename}")

def main():
    # Ensure we can print emojis on Windows
    sys.stdout.reconfigure(encoding='utf-8')
    ensure_dir()
    
    # Step 1: Get Context
    prev_goals = get_last_session_goals()
    
    # Step 2: Interview
    review, learn, thoughts, goals = chat_with_mentor(prev_goals)
    
    # Step 3: AI Processing
    print("\n⏳ Processing and formatting your entry...")
    markdown_content = generate_markdown(review, learn, thoughts, goals)
    
    # Step 4: Save
    save_entry(markdown_content)

if __name__ == "__main__":
    main()