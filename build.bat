@echo off
echo Building Dine-Dash FastAPI Backend EXE...
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --console --add-data "app;app" ^
 --hidden-import "uvicorn.logging" ^
 --hidden-import "uvicorn.loops" ^
 --hidden-import "uvicorn.loops.auto" ^
 --hidden-import "uvicorn.protocols" ^
 --hidden-import "uvicorn.protocols.http" ^
 --hidden-import "uvicorn.protocols.http.auto" ^
 --hidden-import "uvicorn.protocols.websockets" ^
 --hidden-import "uvicorn.protocols.websockets.auto" ^
 --hidden-import "uvicorn.lifespan" ^
 --hidden-import "uvicorn.lifespan.on" ^
 app/main.py
echo Done! The executable is in the dist folder.
pause
