# Finance Bot
A Telegram bot for tracking incomes/expenses.
Generates income/expense reports for the past week or month on demand.

## Stack
**Backend:** Python, Django ORM
**Bot:** Python, aiogram, FSM 
**Database:** PostgreSQL
**Infrastructure:** Docker, Docker Compose
**Web server:** nginx, gunicorn

## Project Structure
```
kerbez_finance/
├── config/                 # Django settings and urls        
├── core/
│   ├── analytics.py        # async function for report calculation      
│   ├── models.py           # Models of DB
│   ├── admin.py
│   ├── views.py
│   ├── test.py
│   └── apps.py
├── bot/
│   ├── handlers.py          # File with handlers and keyboards
│   ├── states.py            # States for FSM
│   ├── configuration.py     # File with bot main configuration      
│   └── main.py              # Main file for bot starting and polling
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
2. Create `.env` file based on `.env.example` and fill in all variables
│---│---│
│ `BOT_TOKEN` │ Telegram bot token from @BotFather │
│ `USER_ID` │ telegram id of users │
│ `POSTGRES_DB` │ PostgreSQL database name │
│ `POSTGRES_USER` │ PostgreSQL username │
│ `POSTGRES_PASSWORD` │ PostgreSQL password │
│ `POSTGRES_HOST` │ PostgreSQL host (use `db` for Docker) │
│ `POSTGRES_PORT` │ PostgreSQL port (default: 5432) │
│ `DEBUG` │ False │
│ `ALLOWED_HOSTS` │ server IP │
│ `DJANGO_SECRET_KEY` │ Secret key │
│ `ADMIN_URL` │ url of admin page │
│---│---│
3. Build and start containers
```bash
docker compose up --build -d
```
4. Apply database migrations 
```bash
docker compose exec bot python manage.py migrate
```
5. The bot is now running and ready to use

## How It Works

### User Registration
- Access is restricted to Telegram IDs listed in .env; all other users are ignored

### Using bot
- There are categories for entries:
  1. **Incomes** — log incomes by categories
  2. **Expenses** — log outcomes by categories
  3. **Report** — write weekly or monthly reports
  4. Command /admin gives url of admin panel 
