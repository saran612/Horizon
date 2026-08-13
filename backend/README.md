# Horizon Backend

FastAPI-powered backend service for Horizon.

## Setup Instructions

1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**:
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

The application will be running at `http://localhost:8000`.

## Key Endpoints

- **Root API**: `http://localhost:8000/`
- **Swagger Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`


