# 📡 Portfolio Insights Backend

A scalable FastAPI backend powering the Portfolio Insights platform. It manages user authentication, alert creation, and database persistence, while delegating real-time stock data to a Go-based market microservice.

## ⚙️ Features

* RESTful API with FastAPI
* User authentication via JWT
* Create/search/delete stock price alerts
* PostgreSQL database connection for persistent alert storage and alert management
* Asynchronous integration with Go microservice for real-time market data retrieval
* Health checks (`/health`, `/health/deep`)

## 🏗️ Project Structure

```
portfolio-insights-backend/
├── src/
│   ├── server.py         # FastAPI entrypoint
│   ├── alerts.py         # Alert CRUD and logic
│   ├── users.py          # User auth and JWT handling
│   ├── database.py       # PostgreSQL connection lifecycle
│   ├── schemas.py        # Pydantic models
│   └── logging.py        # App-wide logger config
├── scripts/
│   ├── docker-deploy.sh
│   ├── docker-teardown.sh
│   ├── local-deploy.sh
│   └── local-dev-setup.sh
├── sql/
│   ├── create_users_table.sql
│   ├── create_alerts_table.sql
│   ├── populate_users_table.sql
│   └── populate_alerts_table.sql
├── .infra/
│   ├── EC2_RDS_SETUP.md
│   ├── nginx_portfolio-insights.conf
│   └── user_data.sh
├── .husky/
│   └── pre-commit       # Git hooks for pre-commit linting
├── .dockerignore
├── .env.example
├── .env.docker.example
├── .gitignore
├── .prettierignore
├── .lintstagedrc        # Pre-commit file filtering config
├── Dockerfile
├── LICENSE.txt
├── package.json
├── package-lock.json
├── pyproject.toml
├── README.md
└── requirements.txt
```

## 🧪 API Endpoints (Selected)

### Health

* `GET /health` — Simple uptime ping
* `GET /health/deep` — DB + market microservice connectivity

### Market Data (via Go microservice)

* `GET /stocks?ticker=...&startDate=...&interval=...` — Fetch historical stock price data for charting
* `GET /check-alert?ticker=...&price=...&direction=...` — Check validity of proposed alert

### Alerts

* `GET /alerts?user_id=...&search_term=...` — Retrieve all alerts (optionally filtered by a ticker search term)
* `POST /alerts` — Create a new stock price alert using submitted form data
* `DELETE /alerts?id=...` — Delete an alert by its ID

### Auth

* `POST /register` — Register a user
* `POST /login` — Login a user in and retrieve a JWT 

## 🚀 Local Development

```bash
bash scripts/local-dev-setup.sh     # Sets up environment + dependencies
bash scripts/local-deploy.sh        # Starts local FastAPI server on :8001
```

You can then test API endpoints via `http://localhost:8001/docs`. Environment variables are set in `.env`.

## 📦 Docker Deployment

```bash
bash scripts/docker-deploy.sh       # Build and launch container
bash scripts/docker-teardown.sh     # Stop and clean environment
```

Environment variables are set in `.env.docker`. Container exposes port `8001` by default.

## 🧾 SQL Integration

The backend connects to a PostgreSQL database (in the demo deployment, this is hosted on AWS RDS). Connection parameters are loaded from environment variables.

The `sql/` directory includes:

* Table creation scripts (`create_users_table.sql`, `create_alerts_table.sql`), which can be run with the `psql` CLI tool to initialize the databases.
* Table population scripts (`populate_users_table.sql`, `populate_alerts_table.sql`), which can be used to populate the tables with dummy data for development or testing.

## ☁️ AWS Deployment

The backend is deployed on an EC2 instance using Docker and proxied with NGINX. SSL support can be added using Certbot. Tools for  EC2 + RDS deployment and DNS/HTTPS setup can be found in the `.infra/` directory:

* Environment provisioning on a new EC2 instance can be automated via `user_data.sh`.
* Manual environment provisioning, database setup, domain routing, and HTTPS setup are explained in `EC2_RDS_SETUP.md`.
* NGINX proxy configuration is found in `nginx_portfolio-insights.conf`.

The API is exposed publicly at  [https://api.portfolio-insights.jakubstetz.dev/](https://api.portfolio-insights.jakubstetz.dev/).

## 🧹 Tooling

* Python `black` formatter
* `prettier` for `.md`, `.toml`, `.yaml`, and other applicable files
* `lint-staged` pre-commit integration
* `.env`-driven config management

## 🔐 Auth Model

This MVP uses plaintext passwords and simple JWT authentication for demonstration purposes. In production, add salting + hashing + secure storage.

## 📄 License

MIT License
