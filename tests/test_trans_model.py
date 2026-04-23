from models.translation_model import TranslationModel

model = TranslationModel()

model.load_source_data(
    [(1, "Hello"), (2, "World")],
    base_filename="test",
    src_lang="en"
)

print(model.get_current_source_text())  # Hello

model.save_current_translation("Hola")

model.next()
print(model.get_current_source_text())  # World

print(model.completion_percentage())  # 50.0