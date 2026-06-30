"""Generate the NLP model files in storage/.

Run this once after cloning or when intents change:
    python scripts/generate_model.py

To use a custom intents file:
    INTENTS_PATH=my_intents.json python scripts/generate_model.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from esc_chatbot.nlp.engine import NLPAttention

engine = NLPAttention()
engine.save()
print("Model generated in storage/")
print("  - storage/w2v.model")
print("  - storage/faiss.index")
print("  - storage/meta.json")
