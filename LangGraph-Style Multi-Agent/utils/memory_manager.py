"""
A tiny file-based memory for persisting queries across runs (optional).
"""
import json
from pathlib import Path

MEM_FILE = Path(".memory.json")

def save_query(topic: str, summary: str):
    data = {}
    if MEM_FILE.exists():
        data = json.loads(MEM_FILE.read_text())
    data[topic] = {"summary": summary}
    MEM_FILE.write_text(json.dumps(data, indent=2))

def get_summary(topic: str):
    if not MEM_FILE.exists():
        return None
    data = json.loads(MEM_FILE.read_text())
    return data.get(topic)
