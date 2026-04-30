import json
import os

def save_json(data, file_path, indent=2):
    """Save data to a JSON file, creating directories if needed."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=indent)

def load_json(file_path):
    """Load data from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r") as f:
        return json.load(f)

def save_text(text, file_path):
    """Save text to a file."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        
    with open(file_path, "w") as f:
        f.write(text)

def load_text(file_path):
    """Load text from a file."""
    with open(file_path, "r") as f:
        return f.read()
