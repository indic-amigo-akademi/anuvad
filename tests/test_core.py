# test_core.py

from core.parser import parse_raw_text
from core.file_handler import save_structured_file
from core.language import detect_language
from models.translation_model import TranslationModel

filepath = "thanda_gosht.txt"

data = parse_raw_text(filepath)

sample_text = data[0][1]
lang = detect_language(sample_text)

print("Detected:", lang)

model = TranslationModel()
model.load_source_data(data, "dracula", lang)

save_structured_file("dracula", lang, data, metadata=model.metadata)