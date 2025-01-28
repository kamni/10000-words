# 10,000 Words

This is a project for building vocabulary in foreign languages.
The user supplies their own texts, and the application helps them build word
lists and sentence lists, which they can then practice in the app.

**NOTE:** This app was initially developed with English, Dutch, and German in
mind. For this reason, the grammatical models probably aren't as diverse as
they need to be to accommodate other language families.

For example, Japanese has more than two politeness levels, but this app
currently only handles 'casual' and 'formal'. I sincerely encourage people
interested in studying other languages to fork this and improve on the word
models.


## Requirements

* Python >= 3.12


## Development

Install python requirements:

```sh
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

Run the django development server:

```sh
cd backend
python manage.py migrate
python manage.py runserver
```

Create an admin user:

```sh
python manage.py createsuperuser
```

You can visit the admin interface at
[localhost:8000/admin](http://localhost:8000/admin)
