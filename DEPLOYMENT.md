# Espaces Ouverts

A Django web application for discovering community spaces in Paris through care homes and organizations.

## Features

- Browse available community spaces
- View detailed information about each space
- Image carousel with navigation
- Responsive design with daisyUI and Tailwind CSS
- PostgreSQL database
- File storage with S3 support for production

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL
- pip or pipenv

### Setup

1. Clone the repository:
```bash
git clone https://github.com/arbitryum/espaces-ouverts.git
cd espaces-ouverts
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Update `.env` with your local database configuration:
```
DATABASE_URL=postgresql://postgres:password@localhost/espaces_ouverts
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

6. Create the database and run migrations:
```bash
python manage.py migrate
python manage.py seed_database  # Load seed data from Airtable
```

7. Collect static files:
```bash
python manage.py collectstatic
```

8. Run the development server:
```bash
python manage.py runserver
```

Visit `http://localhost:8000/spaces/` to see the application.

## Deployment to Scalingo

### Prerequisites

- Scalingo CLI installed
- GitHub repository connected to Scalingo

### Environment Setup

1. Create a Scalingo application:
```bash
scalingo create espaces-ouverts
```

2. Attach a PostgreSQL database:
```bash
scalingo --app espaces-ouverts addons-add postgresql-starter
```

3. Set environment variables:
```bash
scalingo --app espaces-ouverts env-set \
  SECRET_KEY="your-production-secret-key" \
  DEBUG=False \
  ALLOWED_HOSTS="espaces-ouverts.osc-fr1.scalingo.io"
```

### Deploy

1. Add Scalingo remote:
```bash
git remote add scalingo git@ssh.osc-fr1.scalingo.com:espaces-ouverts.git
```

2. Push to deploy:
```bash
git push scalingo main
```

The deployment will:
- Install dependencies from `requirements.txt`
- Collect static files
- Run database migrations (via `bin/post_deploy.sh`)
- Start the application with Gunicorn

### Monitoring

View logs:
```bash
scalingo --app espaces-ouverts logs
```

View running processes:
```bash
scalingo --app espaces-ouverts ps
```

## Database Seed

The project includes a management command to seed the database from Airtable:

```bash
python manage.py seed_database
```

This command:
- Fetches care home data
- Fetches space data
- Downloads images from Airtable
- Populates the database

## Project Structure

```
espaces-ouverts/
├── app/                    # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py
│   └── wsgi.py
├── spaces/                # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # Views
│   ├── templates/         # HTML templates
│   ├── static/            # CSS, JS, images
│   └── management/commands/
│       └── seed_database.py
├── static/                # Project-level static files
├── bin/                   # Deployment scripts
├── Procfile               # Process file for Scalingo
├── requirements.txt       # Python dependencies
├── runtime.txt            # Python version
└── .env.example           # Environment variables template
```

## Technologies

- **Backend**: Django 6.1
- **Database**: PostgreSQL
- **Frontend**: Tailwind CSS, daisyUI
- **Storage**: Local filesystem (development), AWS S3 (production)
- **Server**: Gunicorn
- **Static Files**: WhiteNoise

## Contributing

For local development, follow the "Local Development" section above.

## License

All rights reserved.
