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

Run the project:

```sh
python frontend/main.py
```

Your browser should open and take you to the landing page:
[localhost:8080](http://localhost:8080)


### Django ORM

The project currently uses the Django ORM for the backend,
without using the Django server components.

However, if you would like to manage the database with the Django backend
you can run the development server as follows:

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


## Tests

To run all tests:

```sh
pytest
```

### Credits for Test Data

Test data is used with permission from [Grimm Stories](https://www.grimmstories.com).
