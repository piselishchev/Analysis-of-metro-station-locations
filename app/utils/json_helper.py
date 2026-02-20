import os
import json
import numpy as np
import osmnx as ox
from pathlib import Path
from app.config import Config

def get_data(city):
    file = "city_data.json"
    filepath = Config.DATA_DIR / "cities" / city / file
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'.")
        return
    
    return data