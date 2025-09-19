For the first time, execute these commands:
```
python -m venv env
env\Scripts\activate # or source env/bin/activate on mac
pip install -r requirements.txt
python manange.py tailwind install
python manage.py migrate
python manage.py tailwind dev # run dev server with tailwind
```

Do note that we use
```
python manage.py tailwind dev
```
to run development server instead of the conventional `python manage.py runserver` due to the usage of `django-tailwind` package.