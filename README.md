# HealthConnect

Django application for online pharmacy orders and doctor appointments.

## Free demo deployment on Render

The repository includes a Render Blueprint at `render.yaml`. Render hosts the Django app and PostgreSQL database; Resend is the app's email delivery API. The Blueprint runs migrations, seeds sample doctors and medicines, collects static assets, and generates a private admin password.

1. Push this repository to GitHub. Before committing, check `git status --short`; `.gitignore` excludes local `.env` files, SQLite databases, virtual environments, and uploaded media.
2. Sign in to Render and choose **New + → Blueprint**.
3. Connect the GitHub repository containing this project and apply the Blueprint.
4. Wait for the first deploy to finish. In the Render service's **Environment** settings, find `ADMIN_PASSWORD`; the admin email is `admin@healthconnect.com`.
5. Open the service's `onrender.com` URL. The custom admin sign-in is at `/admin-login/`.

The Django project lives in `healthconnect/`, alongside `manage.py` and `build.sh`.

### Free-tier limits

This is a demo deployment. Render free web services sleep after 15 minutes without traffic and can take about a minute to wake. Render's free PostgreSQL databases expire 30 days after creation. Uploaded files are on an ephemeral filesystem, so images uploaded through the app can disappear on restart or redeploy. Do not store real patient or payment data here. See [Render free plan limits](https://render.com/docs/free).

The app sends email through Resend's HTTP API, so it does not require an SMTP connection. Set `RESEND_API_KEY` in the Render service environment. A new Blueprint asks for this secret during setup; for an existing service, add it under **Environment** in the Render Dashboard because Blueprint syncs do not prompt again for `sync: false` values. `onboarding@resend.dev` is configured as the initial sender for testing; set `DEFAULT_FROM_EMAIL` to an address on your verified Resend domain before sending to regular recipients.

## Local development

```bash
cd healthconnect
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For local email delivery, set `RESEND_API_KEY` in `healthconnect/.env`; without a key, Django prints email messages to the console in debug mode. To check Resend delivery from a configured environment, run `python manage.py test_email delivered@resend.dev`.
