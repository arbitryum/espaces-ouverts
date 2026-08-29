# Open Spaces

Web application that allows care homes to publish spaces they make available
to nonprofit organizations, and allows those organizations to browse them.

The project is currently a Django prototype. The main models are:

- `CareHome`: a care home;
- `NonprofitOrganization`: a nonprofit organization;
- `Space`: a space offered by a care home.

## Requirements

- Python 3.14 or a version compatible with Django 6.1;
- PostgreSQL running locally;
- a terminal opened at the project root.

The current configuration uses the PostgreSQL database
`espaces_ouverts_development` on `localhost`, with the default local
PostgreSQL user. Adapt `app/settings.py` or your PostgreSQL configuration if
necessary.

## Installation

Create and activate the virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies listed in `requirements.txt`:

```sh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create the PostgreSQL database if it does not already exist:

```sh
createdb espaces_ouverts_development
```

Apply the migrations:

```sh
python manage.py migrate
```

## Start the project

Start the Django development server:

```sh
python manage.py runserver
```

The application is then available at `http://127.0.0.1:8000/`.

The admin interface is available at `http://127.0.0.1:8000/admin/`.

Create an administrator account:

```sh
python manage.py createsuperuser
```

## CSS development

The Tailwind CSS files are located in `static/css/`.

To generate the CSS and automatically regenerate it whenever `input.css` is
modified:

```sh
./static/css/tailwindcss \
	-i static/css/input.css \
	-o static/css/output.css \
	--watch
```

To generate the file once, for example in CI/CD:

```sh
./static/css/tailwindcss \
	-i static/css/input.css \
	-o static/css/output.css
```

During development, run Django and Tailwind in two separate terminals.

## Useful commands

Update `requirements.txt` from the currently active virtual environment:

```sh
python -m pip freeze > requirements.txt
```

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

The available routes are defined in `app/urls.py` and `spaces/urls.py`.

## Main structure

```text
app/            Django project configuration
spaces/         Application code and models
static/css/     Tailwind CSS source and output files
manage.py       Django administration command
```
