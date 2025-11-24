from openai import OpenAI

# Point to the local server
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',  # required but ignored
)

try:
    # Use a model you have downloaded with 'ollama run <model_name>'
    model_name = "llama3"

    print(f"Sending request to Ollama with model: {model_name}...")

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": "Why is the sky blue? Explain it like I'm five.",
            }
        ],
        stream=True # Set to True to see the response generate in real-time
    )

    print("\nResponse from Ollama:")
    full_response = ""
    for chunk in response:
        # Check if the chunk has content to print
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            full_response += chunk.choices[0].delta.content
    
    print("\n\n--- End of response ---")

except Exception as e:
    print(f"\nAn error occurred: {e}")
    print("\nPlease ensure the Ollama application is running and you have downloaded the model by running 'ollama run llama3' in your terminal.")

