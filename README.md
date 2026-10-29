# HealthConnect

Django application for doctor appointments and medicine orders.

## Run locally

From the project folder:

```powershell
cd healthconnect
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser. The local database is SQLite and is created at `healthconnect/db.sqlite3`.

## Email for signup verification

Without email settings, Django prints verification codes and other email messages in the terminal running the server. To deliver them to real inboxes, copy `healthconnect/.env.example` to `healthconnect/.env` and enter your SMTP provider's host, port, username, password, and sender address. The local `.env` file is ignored by Git.
