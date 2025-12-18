#  Personal Cloud Backend

This repository contains the backend service for a Personal Cloud application.

The backend is implemented as a Flask-based REST API using a proper application package structure.  
It handles authentication, file uploads, file downloads, database access, and communication with client applications such as an Android app.

---

##  Tech Stack

- Python 3.10+
- Flask
- Werkzeug
- REST API
- JSON
- Virtual Environment (venv)

---

##  Project Structure

```
personal-cloud-backend/
├── app/ # Flask application package
│ ├── init.py # App factory & initialization
│ ├── config.py # Configuration settings
│ ├── models.py # Database models
│ ├── routes/ # API route definitions
│ │ ├── auth.py # Authentication routes
│ │ └── files.py # File upload & download routes
│ └── utils/ # Helper utilities & decorators
│
├── run.py # Application entry point
├── check_users.py # Utility / maintenance script
├── database.db # SQLite database
├── requirements.txt # Python dependencies
├── .gitignore # Files and folders to be ignored by Git
├── .env # Local environment variables (include in .gitignore)
├── venv/ # Virtual environment (not committed)
└── README.md
```


---

##  Prerequisites

Make sure the following are installed:

- Python 3.10 or newer
- pip
- Git
- Linux / macOS / Windows

Verify Python installation:

```bash
python3 --version
```

---

##  Configuration Reference

This application requires several environment variables to function correctly. These variables should be stored in a `.env` file in the project's root directory.

The **setup instructions** below will guide you through creating this file. Here is the template you will need to copy and fill in with your own values:

```ini
# .env

# Used by Flask for session security. Generate a strong, random key.
SECRET_KEY='your_very_secret_key_here'

# The folder where uploaded files will be stored.
UPLOAD_FOLDER='app/uploads'

# Your Google OAuth 2.0 Client ID for authentication.
GOOGLE_CLIENT_ID='your_google_client_id_here.apps.googleusercontent.com'

# Connection string for the database.
DATABASE_URL='sqlite:///database.db'
```

---


##  Setup Instructions

1. Clone the repository

```bash
git clone https://github.com/sachinisandreas-del/personal-cloud-server
cd personal-cloud-backend
```

2. Create the environment file

Now that you are in the project root, create the .env file.

```bash
touch .env
```
  
  
Next, open the new .env file and copy the contents from the **[Configuration Reference](#-configuration-reference)** section above. Be sure to fill in your own secret values.


3. Create a virtual environment

```bash
python3 -m venv venv
```

4. Activate the virtual environment

``` bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

5. Install dependencies

```bash
pip install -r requirements.txt
```

---

##  Running the Application (Terminal)

From the project root (with venv activated):

```bash
python run.py
```
The backend will start on:
```cpp
http://127.0.0.1:5000/
```

##  Running the Application (IntelliJ IDEA)

1. Ensure the **Python plugin** is installed and enabled
2. Open **Settings &rarr; Project &rarr; Python Interpreter.**
3. Select the interpreter located at:
   ```bash
   venv/bin/python3
   ```
4. Create a run configuration:
   - Go to **Run &rarr; Edit Configurations**
   - Click **+ &rarr; Python**
5. Configure:
   - **Script path:** `path/to/personal-cloud-backend/run.py`
   - **Working directory:** `path/to/personal-cloud-backend`
   - **Python interpreter:** `venv/bin/python3`
6. Click **Apply &rarr; Run** 

IntelliJ will now run the backend exactly the same way as the terminal.

---

##  API Overview

| Method | Endpoint      | Description        |
|--------|---------------|--------------------|
| `POST` | `/upload`     | Uploads a new file (multipart/form-data).|
| `GET`  | `/download/<filename>` | Returns the requested file if it exists.  |


(To Add More...)

---

##  Security & File Handling

- Filenames are sanitized using secure_filename
- Files are stored using UUID-based names to prevent collisions
- Direct filesystem paths are never exposed to clients

---

##  Development Notes

   - Always activate the virtual environment before running the app
   - Do not commit the `venv/` directory
   - Restart the server after code changes
   - Ensure correct permissions for `database.db`
   - `check_users.py` is a helper script and not part of server startup

---

##  .gitignore

This project includes a comprehensive `.gitignore` file to ensure that temporary files, sensitive credentials, and environment-specific folders are not committed to the repository.

<details>
<summary>Click to view the contents of .gitignore</summary>

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads
/mnt/

# Logs
*.log
```

</details>

---


