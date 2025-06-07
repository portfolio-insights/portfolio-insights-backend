# EC2 Setup Guide for Portfolio Insights

This document outlines the standard setup for launching and configuring an EC2 instance to run the Portfolio Insights backend using Docker and NGINX on Amazon Linux 2023. After SSHing into your EC2 instance, execute steps 1-4.

---

## 🔧 1. Initial EC2 Setup

### System Update and Basic Tools

```bash
sudo dnf update -y
sudo dnf install -y git nginx docker python3-pip
```

### Docker Configuration

```bash
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
```

Log out and back in to apply Docker group permissions.

---

## 🧬 2. Clone the Project Repository

```bash
git clone https://github.com/jakubstetz/portfolio-insights-backend.git
```

Once the project is cloned onto the EC2 instance, running the "Deploy Backend to EC2" workflow (`backend.yaml`) in GitHub Actions will deploy the backend.

---

## 🌐 3. NGINX Reverse Proxy (Optional)

If you want to connect to the backend through a domain, execute the following steps.

1. Save the config file `.infra/nginx_portfolio-insights.conf` to:

```bash
/etc/nginx/conf.d/portfolio-insights.conf
```

> Note:
> To confirm that the above location is correct for the NGINX config file, run the command `sudo nginx -t`, which should output something like:
> `nginx: the configuration file /etc/nginx/nginx.conf syntax is ok`
> Then, run the command `cat /etc/nginx/nginx.conf | grep include`. If the output contains a line like the following, then the above location is correct:
> `include /etc/nginx/conf.d/*.conf;`

2. Enable automatic restart of NGINX on system reboot:

```bash
sudo systemctl enable nginx
```

2. Restart NGINX:

```bash
sudo systemctl restart nginx
```

You will also need to configure your DNS records to point your desired domain to your EC2 instance private IP address.

---

## 🔐 4. SSL with Certbot (Optional)

Execute the following commands if you want to allow an HTTPS connections to your backend.

```bash
sudo dnf install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.portfolio-insights.jakubstetz.dev
```

> Note:
> First-time use of Certbot requires manual input of your email for notifications, as well as acceptance of terms of service and agreement/disagreement to share address with the Electronic Frontier Foundation.

---

## 🗄️ 5. Database Setup

For the backend to run, you will need to create a new database with properly-formatted tables. This can be done either from your EC2 instance or from your local environment using the `psql` command line tool. After setting up an RDS instance on AWS, run the following SQL files in order to create the necessary tables:

```bash
psql -h <your-rds-endpoint> -U <your-username> -d <your-database-name> -f sql/create_users_table.sql
psql -h <your-rds-endpoint> -U <your-username> -d <your-database-name> -f sql/create_alerts_table.sql
```

> Note:
>
> - The order of these commands matters as `alerts` table has a foreign key dependency on `users` table.
> - `populate_users_table.sql` and `populate_alerts_table.sql` can be used to populate the new tables with dummy data if desired.

---

## 📂 `.infra` Folder Structure Overview

- `.infra/SETUP.md` — this setup guide.
- `.infra/nginx_portfolio-insights.conf` — template for NGINX reverse proxy (uses domain `api.portfolio-insights.jakubstetz.dev`).
- `.infra/user_data.sh` — optional EC2 user-data script to automate instance setup.
