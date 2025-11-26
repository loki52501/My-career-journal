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

def get_last_session_content():
    """
    Reads the content of the most recent markdown file.
    """
    files = sorted(glob.glob(os.path.join(JOURNAL_DIR, "*.md")))
    if not files:
        return "No previous journal entries found."
    
    last_file = files[-1]
    with open(last_file, 'r', encoding='utf-8') as f:
        return f.read()

def chat_with_future_self(last_session_content):
    """
    Conducts a conversation with the AI acting as the user's future self.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"\n🔮 \033[1mCONVERSATION WITH FUTURE SELF: {date_str}\033[0m")
    print("-" * 50)
    
    print(f"\n🤖 \033[1mAI (Your Future Self):\033[0m Hello past self. I've reviewed your last journal entry:\n")
    print(f"\033[3m{last_session_content}\033[0m\n")
    
    print("What's on your mind today? Any questions for me, your future self, or anything you want to reflect on?")
    user_reflection = input("YOU > ")

    print(f"\n🤖 \033[1mAI (Your Future Self):\033[0m Interesting. Let me think about that from my perspective. What are your biggest hopes or fears right now regarding your goals?")
    user_hopes_f