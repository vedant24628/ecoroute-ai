# EcoRoute AI

EcoRoute AI is a Smart Society Waste Management System designed to optimize waste collection routes and improve community cleanliness.
Motto: "Smarter Routes. Cleaner Communities."

## Features
- Smart route optimization for waste collection.
- Vehicle tracking and GPS updates.
- Society management dashboard.
- Web-based interface.

## Technology Stack
- **Backend:** Python, Flask, Flask-SocketIO, SQLAlchemy
- **Database:** SQLite (local development), MySQL (production recommended)
- **Frontend:** HTML, CSS, JavaScript

## Project Structure
- `app/` - Main application logic, routes, and templates.
- `run.py` - Application entry point.
- `config.py` - Configuration settings.
- `requirements.txt` - Python dependencies.
- `vercel.json` - Vercel deployment configuration.
- `.env.example` - Template for environment variables.

## Local Setup

### 1. Create a Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Copy `.env.example` to a new file named `.env` and fill in your values.

### 5. Run the Application
```bash
python run.py
```
The app will run at `http://127.0.0.1:5000`.

## Database Setup
By default, the application uses a local SQLite database (`ecoroute.db`). For production, it is highly recommended to use a hosted MySQL database.

Set `USE_MYSQL=True` and configure the `MYSQL_*` environment variables in your `.env` file to connect to a MySQL database.

## Vercel Deployment Notes
- **WebSockets / SocketIO:** Vercel's Serverless Functions do not natively support persistent WebSocket connections. Real-time features relying on Flask-SocketIO may fall back to long-polling or fail due to timeouts. If real-time connectivity is essential, consider hosting on a platform with persistent processes like Render or Railway.
- **Database:** Vercel has an ephemeral filesystem. You must use a hosted database (like PlanetScale or AWS RDS) because local SQLite files will not persist data across requests in production.

