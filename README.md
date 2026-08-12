# Finance Bot

A Telegram bot for tracking income and expenses.
The bot logs transactions by category and generates weekly and monthly reports on demand.

## Stack

**Backend:** Python, Django ORM
**Bot:** Python, aiogram, FSM states
**Database:** PostgreSQL
**Web server:** nginx (reverse proxy, static files), gunicorn
**Infrastructure:** Docker, Docker Compose

## Project Structure

```
kerbez_finance/
├── config/                  # Django settings and urls
├── core/
│   ├── analytics.py         # Async functions for report calculation
│   ├── models.py            # Database models
│   ├── admin.py
│   ├── views.py
│   ├── tests.py
│   └── apps.py
├── bot/
│   ├── handlers.py          # Handlers and keyboards
│   ├── states.py            # FSM states
│   ├── configuration.py     # Bot configuration
│   └── main.py              # Entry point, polling
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
├── manage.py
└── .env.example
```

## Installation and Running

### Prerequisites

- Docker and Docker Compose installed on your server
- Git installed

### Steps

1. Clone the repository

```bash
git clone https://github.com/ladron711/kerbez_finance.git
cd kerbez_finance
```

2. Create a `.env` file based on `.env.example` and fill in all variables:

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from @BotFather |
| `USER_ID` | Telegram IDs of allowed users |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_HOST` | PostgreSQL host (use `db` for Docker) |
| `POSTGRES_PORT` | PostgreSQL port (default: 5432) |
| `DEBUG` | Set to `False` in production |
| `ALLOWED_HOSTS` | Server IP or domain |
| `DJANGO_SECRET_KEY` | Django secret key |
| `ADMIN_URL` | Path to the admin panel |

3. Build and start the containers

```bash
docker compose up --build -d
```

4. Apply database migrations

```bash
docker compose exec bot python manage.py migrate
```

5. Collect static files for the admin panel

```bash
docker compose exec bot python manage.py collectstatic --noinput
```

6. The bot is now running and ready to use

## How It Works

### Access control

Access is restricted to the Telegram IDs listed in `.env`. Messages from any other user are ignored by a middleware attached to `dp.update`, so the restriction covers every event type, not just text messages.

### Usage

1. **Income** — log an income entry by category
2. **Expenses** — log an expense entry by category
3. **Report** — generate a weekly or monthly summary
4. `/admin` — returns the URL of the admin panel

Transactions are entered through a multi-step FSM dialog: the user picks a category, then a worker, then enters the amount.

## Design Decisions

- **Transaction type is derived, not stored.** A transaction's type (income or expense) comes from its category rather than being duplicated on the transaction itself, which makes an inconsistent state impossible.
- **`PROTECT` instead of `CASCADE`** on foreign keys to categories and workers. Financial records carry historical meaning, so deleting a category must not silently erase the transactions attached to it.
- **`DecimalField` instead of `FloatField`** for monetary values, to avoid floating-point rounding errors.
- **Categories and workers live in the database**, not in the code, so the bot's keyboards are generated dynamically and new options can be added through the admin panel without a redeploy.
- **nginx serves static files, gunicorn handles dynamic requests.** gunicorn is exposed only to nginx inside the Docker network rather than published to the host.
