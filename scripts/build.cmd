pyinstaller --onefile --windowed ^
  --name Anuvad ^
  --icon=assets/images/icon.ico ^
  --add-data "app.cfg;." ^
  --add-data "assets;assets" ^
  --collect-data indic_transliteration ^
  --hidden-import indic_transliteration ^
  main.py