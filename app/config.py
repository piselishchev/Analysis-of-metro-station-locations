from pathlib import Path

class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    
    DATA_DIR = PROJECT_ROOT / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)