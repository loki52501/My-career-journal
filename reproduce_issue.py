import sys
import os

emoji = "\U0001f50d" # 🔍

print(f"Attempting to print emoji: {emoji}")

try:
    print(f"Printed: {emoji}")
except UnicodeEncodeError as e:
    print(f"Caught expected error printing: {e}")
except Exception as e:
    print(f"Caught unexpected error printing: {e}")

filename = "test_unicode.md"
content = f"""
# Journal Entry
## {emoji} Check
"""

print(f"Attempting to write emoji to file: {filename}")
try:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully wrote to file.")
except UnicodeEncodeError as e:
    print(f"Caught expected error writing to file: {e}")
except Exception as e:
    print(f"Caught unexpected error writing to file: {e}")

# Clean up
if os.path.exists(filename):
    os.remove(filename)
