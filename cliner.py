import os
import json
from openai import OpenAI

# --- CONFIGURATION ---
# OPTION 1: Local/Free (Ollama) - Recommended
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',
)
MODEL = "llama3" # Make sure you have run 'ollama run llama3'

# OPTION 2: OpenAI (Paid)
# client = OpenAI(api_key="YOUR_KEY_HERE")
# MODEL = "gpt-4o"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def analyze_text(history, user_input):
    """
    Asks the LLM to check grammar. Returns JSON.
    """
    system_prompt = """
    You are a strict English Grammar Drill Sergeant.
    Analyze the user's latest input for grammar, tense, or preposition errors.
    
    Output strictly in this JSON format:
    {
        "has_error": boolean,
        "correction": "The corrected version of user input",
        "explanation": "Brief explanation of the rule broken",
        "drills": ["Simpler sentence applying rule", "Medium sentence applying rule", "Complex sentence applying rule"],
        "reply": "A natural conversational reply if there is NO error (leave empty if error)"
    }
    """
    
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_input}]
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"has_error": False, "reply": "System Error: " + str(e)}

def run_drill(data):
    """
    Forces the user to type the corrected examples.
    """
    print(f"\n🛑 \033[1mSTOP. GRAMMAR ERROR DETECTED.\033[0m")
    print(f"❌ You wrote:   {data.get('correction', 'Error loading')}") # Logic to show what they should have written
    print(f"💡 Rule:        {data['explanation']}")
    print("-" * 50)
    print("To return to chat, you must type these 3 practice sentences perfectly:\n")

    drills = data['drills']
    
    for i, sentence in enumerate(drills, 1):
        while True:
            print(f"Drill {i}: \033[1m{sentence}\033[0m")
            user_try = input("TYPE >   ")
            
            if user_try.strip() == sentence.strip():
                print("✅ Correct.\n")
                break
            else:
                print("❌ Incorrect. Type it exactly as shown.")

    print("🎉 Drill complete. Muscle memory updated.")
    input("Press Enter to continue chat...")

def main():
    history = []
    clear_screen()
    print("╔══════════════════════════════════════╗")
    print("║   GRAMMAR DRILL SERGEANT (Active)    ║")
    print("╚══════════════════════════════════════╝")
    print("Start chatting. If you mess up, I will make you work.\n")

    while True:
        user_input = input("YOU > ")
        if user_input.lower() in ['exit', 'quit']:
            break

        # Analyze
        data = analyze_text(history, user_input)

        if data.get('has_error'):
            # If error, we fix the user input in history to keep context clean
            history.append({"role": "user", "content": data['correction']})
            history.append({"role": "assistant", "content": "Correction noted."})
            
            # Run the punishment/drill
            run_drill(data)
            clear_screen()
            print("╔══════════════════════════════════════╗")
            print("║   GRAMMAR DRILL SERGEANT (Active)    ║")
            print("╚══════════════════════════════════════╝")
            print("(Resuming chat...)\n")
        else:
            # No error, continue conversation
            reply = data['reply']
            print(f"AI  > {reply}\n")
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()