# Open Spaces

Web application that allows care homes to publish spaces they make available
to nonprofit organizations, and allows those organizations to browse them.

The project is currently a Django prototype. The main models are:

- `CareHome`: a care home;
- `NonprofitOrganization`: a nonprofit organization;
- `Space`: a space offered by a care home.

## Requirements

- Python 3.13+ (managed via [mise](https://mise.jdx.dev/) if available)
- Node.js 20+ (managed via mise)
- PostgreSQL running locally

The current configuration uses the PostgreSQL database
`espaces_ouverts_development` on `localhost`, with the default local
PostgreSQL user. Adapt `app/settings.py` or your PostgreSQL configuration if
necessary.

## Installation

### Using mise (recommended)

If you have [mise](https://mise.jdx.dev/) installed, it will automatically install the correct Python and Node.js versions:

```sh
mise install
```

### Using uv for Python dependencies

Install Python dependencies using [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

This creates a virtual environment and installs all dependencies from `pyproject.toml` and `uv.lock`.

Activate the virtual environment:

```sh
source .venv/bin/activate
```

### Setup the database

Create the PostgreSQL database if it does not already exist:

```sh
createdb espaces_ouverts_development
```

Apply the migrations:

```sh
python manage.py migrate
```

Seed the database with example data:

```sh
python manage.py seed_database
```

## Start the project

### Terminal 1: Django development server

```sh
python manage.py runserver
```

The application is then available at `http://127.0.0.1:8000/`.

The admin interface is available at `http://127.0.0.1:8000/admin/`.

Create an administrator account:

```sh
python manage.py createsuperuser
```

### Terminal 2: Tailwind CSS development watcher

```sh
cd theme/static_src
npm run dev
```

This watches for changes in `src/styles.css` and automatically regenerates the CSS.

## Deployment to Scalingo

The application is deployed to Scalingo using:
- Node.js buildpack (for Tailwind CSS compilation)
- Python buildpack (for Django application)

Deployment automatically:
1. Installs Node.js dependencies and builds Tailwind CSS
2. Installs Python dependencies using uv
3. Runs database migrations
4. Collects static files

## Useful commands

Check the Django configuration:

```sh
python manage.py check
```

Create a migration after changing the models:

```sh
python manage.py makemigrations
python manage.py migrate
```

Run the tests:

```sh
python manage.py test
```

Open a Django shell:

```sh
python manage.py shell
```

Update Python dependencies (after changing `pyproject.toml`):

```sh
uv lock
```

## Main structure

```text
app/                  Django project configuration
spaces/               Application code and models
theme/static_src/     Tailwind CSS source (Node.js + npm)
static/               Generated CSS and static files
bin/                  Deployment scripts
manage.py             Django administration command
pyproject.toml        Python project configuration and dependencies
uv.lock               Lockfile for reproducible Python dependency resolution
```

