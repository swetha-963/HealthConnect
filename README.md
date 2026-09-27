# HealthConnect

A responsive Django healthcare e-commerce platform: browse doctors, book appointments,
order medicines online, and run the whole operation from a purpose-built admin dashboard.

- Patients: register, browse doctors/specializations, book a slot, shop the pharmacy,
  manage a cart, check out, and track orders.
- Administrators: dashboard analytics, doctor CRUD with photo upload, schedules with
  availability, appointment confirmation, medicine/stock management and order status updates.
- Email notifications for registration, bookings, confirmations, orders and status changes.

---

## 1. Project structure

```
healthconnect/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── healthconnect/              # project package
│   ├── settings.py             # env-driven settings (SQLite/PostgreSQL, email, media)
│   ├── urls.py                 # root routes + media/static serving in DEBUG
│   ├── asgi.py
│   └── wsgi.py
├── accounts/                   # custom user (patient/admin), auth, profile
│   ├── models.py  forms.py  views.py  urls.py  admin.py  tests.py
│   └── migrations/0001_initial.py
├── core/                       # public pages, email helpers, seed command
│   ├── views.py  forms.py  urls.py  emails.py  context_processors.py  tests.py
│   └── management/commands/seed_data.py
├── doctors/                    # Specialization, Doctor, DoctorSchedule, Appointment
│   ├── models.py  forms.py  views.py  urls.py  admin.py  tests.py
│   └── migrations/0001_initial.py
├── pharmacy/                   # Category, Medicine, Cart, CartItem, Order, OrderItem
│   ├── models.py  forms.py  views.py  urls.py  admin.py  tests.py
│   └── migrations/0001_initial.py
├── dashboard/                  # admin-only dashboard (decorators, views, urls, tests)
├── static/
│   ├── css/style.css           # responsive design system
│   └── js/main.js              # nav, sidebar, alerts, image preview, qty steppers
├── templates/
│   ├── base.html  404.html  500.html
│   ├── partials/               # field.html, form.html, pagination.html
│   ├── accounts/               # login, register, profile
│   ├── core/                   # home, about, contact
│   ├── doctors/                # list, detail, my_appointments, _doctor_card
│   ├── pharmacy/               # medicine_list/detail, cart, checkout, orders
│   ├── dashboard/              # base, home, doctors, schedules, appointments,
│   │                           # medicines, categories, orders
│   └── emails/                 # welcome, appointment_booked/confirmed, order_placed,
│                               # order_status, contact
└── media/                      # uploaded doctor/medicine/profile images (gitignored)
```

### Key model fields

| Model            | Field         | Purpose                                                       |
| ---------------- | ------------- | ------------------------------------------------------------- |
| `DoctorSchedule` | `is_available`| Toggles whether patients can book the slot                     |
| `Appointment`    | `confirmed`   | Boolean kept in sync with `status`; set by dashboard confirm   |
| `Medicine`       | `stock`       | Decremented atomically at checkout; drives low/out-of-stock UI |
| `Order`          | `order_id`    | Public identifier, auto-generated as `HC-XXXXXXXX`             |
| `Order`          | `status`      | pending → confirmed → packed → shipped → delivered / cancelled |

---

## 2. Installation

```bash
git clone <repository-url>
cd healthconnect

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

`psycopg2-binary` is only needed for PostgreSQL; it is safe to leave installed with SQLite.

---

## 3. .env configuration

```bash
cp .env.example .env
```

Then edit `.env`:

| Variable | Default | Notes |
| --- | --- | --- |
| `SECRET_KEY` | insecure dev key | **Change for production** |
| `DEBUG` | `True` | Set `False` in production |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,...` | Comma separated |
| `CSRF_TRUSTED_ORIGINS` | empty | Needed behind HTTPS proxies |
| `DB_ENGINE` | `sqlite` | Set `postgresql` to use `DB_NAME/USER/PASSWORD/HOST/PORT` |
| `EMAIL_BACKEND` | `console` | `console` prints emails to the terminal; `smtp` sends real mail |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_USE_TLS` | Gmail SMTP defaults | Used when `EMAIL_BACKEND=smtp` |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | empty | SMTP credentials / app password |
| `DEFAULT_FROM_EMAIL` | `HealthConnect <no-reply@...>` | From header |
| `SITE_NAME` / `SITE_URL` | HealthConnect / `http://127.0.0.1:8000` | Used in emails |
| `SUPPORT_EMAIL` / `SUPPORT_PHONE` | demo values | Shown in the footer and contact page |
| `CURRENCY_SYMBOL` | `$` | Displayed with all prices |
| `DELIVERY_FEE` | `4.99` | Charged below the free-delivery threshold |
| `FREE_DELIVERY_THRESHOLD` | `50` | Cart subtotal that unlocks free delivery |
| `DJANGO_SUPERUSER_*` | admin / admin12345 | Only used by `seed_data` |

Never commit `.env` — it is already in `.gitignore`.

### PostgreSQL (optional)

```env
DB_ENGINE=postgresql
DB_NAME=healthconnect
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

---

## 4. Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

(The initial migrations for `accounts`, `doctors` and `pharmacy` are committed, so
`migrate` alone is enough on a fresh clone.)

---

## 5. Run

```bash
python manage.py runserver
```

| URL | Purpose |
| --- | --- |
| `http://127.0.0.1:8000/` | Home |
| `/doctors/` | Doctor directory & booking |
| `/pharmacy/` | Medicine catalogue, cart, checkout |
| `/accounts/login/` | Login (admins land on the dashboard) |
| `/dashboard/` | Admin dashboard |
| `/django-admin/` | Django admin |

---

## 6. Test admin credentials

Option A — seed demo data **and** the admin account (doctors, schedules, medicines,
sample appointments):

```bash
python manage.py seed_data
```

Creates:

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin12345` |
| Patient | `patient` | `patient12345` |

Override the admin credentials with `DJANGO_SUPERUSER_USERNAME`,
`DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` in `.env` before seeding.

Option B — create your own superuser:

```bash
python manage.py createsuperuser
```

Any superuser/staff account, or a user whose `role` is `admin`, can reach `/dashboard/`.

---

## 7. API / external service configuration

The project needs **no third-party API keys** to run. The only external integration is
email:

- `EMAIL_BACKEND=console` (default) — no credentials, emails print to the terminal.
- `EMAIL_BACKEND=smtp` — set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`,
  `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`. For Gmail use an
  [App Password](https://support.google.com/accounts/answer/185833) rather than your
  account password.

Email sending never breaks a request: failures are logged and the user flow continues.
Media uploads are stored locally under `media/` and served by Django while `DEBUG=True`;
behind a production web server, serve `MEDIA_ROOT` at `MEDIA_URL` and run
`python manage.py collectstatic`.

---

## 8. Automated tests

```bash
python manage.py test
```

40 tests cover admin login/permissions, the dashboard, doctor CRUD and image upload,
schedules and availability, appointment booking/confirmation, medicine stock filters,
cart/checkout stock decrement, order ids and status updates, emails and logout.

---

## 9. Final verification steps

```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py check
python manage.py test
python manage.py runserver
```

Then walk the admin workflow at `http://127.0.0.1:8000`:

1. **Admin login** — `/accounts/login/` with `admin / admin12345` → redirected to `/dashboard/`.
2. **Dashboard** — counters for doctors, appointments, medicines, orders and revenue.
3. **Add doctor** — Doctors → *Add doctor*, save, and confirm it appears in the list.
4. **Add doctor image** — Doctors → *Photo*, upload a JPG/PNG (≤5 MB); the thumbnail updates
   and the file lands in `media/doctors/`.
5. **Add schedule** — Schedules → *Add schedule*; past dates and end ≤ start are rejected.
6. **View schedules** — filter by doctor and availability; toggle `is_available` and see the badge flip.
7. **View appointments** — book one first as `patient / patient12345` from `/doctors/`,
   then filter by status/reference in the dashboard.
8. **Confirm appointment** — click *Confirm*: status becomes Confirmed, `confirmed=True`,
   `confirmed_at` is stamped, and the confirmation email prints in the terminal.
9. **View medicines** — filter by low/out of stock; badges reflect `stock`.
10. **Add medicine** — set price, stock and image; it shows immediately on `/pharmacy/`.
11. **View orders** — place one as the patient (cart → checkout) and find it by `order_id`.
12. **Update order status** — change to Shipped from the list or detail page; the badge
    updates and a status email is sent.
13. **Logout** — the user menu → *Logout* returns you to the public home page.

Also check responsiveness: at ≤768 px the header collapses to a hamburger menu, the
dashboard sidebar becomes a slide-in drawer, and tables scroll horizontally.
