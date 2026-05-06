pyinstaller --onefile --windowed ^
  --name Anuvad ^
  --icon=assets/images/icon.ico ^
  --add-data "app.cfg;." ^
  --add-data "assets;assets" ^
  main.py