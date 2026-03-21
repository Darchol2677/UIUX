import os
import sys
import ai_engine
import app

print(f"CWD: {os.getcwd()}")
print(f"PYTHONPATH: {sys.path}")
print(f"ai_engine file: {ai_engine.__file__}")
print(f"app file: {app.__file__}")

with open(ai_engine.__file__, 'r') as f:
    content = f.read()
    print(f"ai_engine contains 'AI Redesigned Hero': {'AI Redesigned Hero' in content}")
    print(f"ai_engine length: {len(content)}")
