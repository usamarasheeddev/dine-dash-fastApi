# Dine-Dash FastAPI Backend

Modern FastAPI implementation of the Dine-Dash POS backend.

## Prerequisite
- Python 3.10+
- PostgreSQL Database

## Installation

1. **Clone the repository** (if not already done).
2. **Create a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Configure environment variables**:
   Create a `.env` file from the provided template and update your database credentials.

## Running the Application

### Development Mode (with reload)
```powershell
cls
```

### Production Mode
```powershell
python -m app.main
```

## Creating Executable (.exe)

We use **PyInstaller** to bundle the application into a single executable file.

### 1. Install PyInstaller
```bash
pip install pyinstaller
```

### 2. Build the EXE
Run the following command in the root directory:
```bash
pyinstaller --noconfirm --onefile --console --add-data "app;app" --hidden-import "uvicorn.logging" --hidden-import "uvicorn.loops" --hidden-import "uvicorn.loops.auto" --hidden-import "uvicorn.protocols" --hidden-import "uvicorn.protocols.http" --hidden-import "uvicorn.protocols.http.auto" --hidden-import "uvicorn.protocols.websockets" --hidden-import "uvicorn.protocols.websockets.auto" --hidden-import "uvicorn.lifespan" --hidden-import "uvicorn.lifespan.on" app/main.py
```

The executable will be generated in the `dist/` folder as `main.exe`.

### 3. Running the EXE
1. Copy the `.env` file to the same directory as `main.exe`.
2. Run `main.exe`.
