For the first time, execute these commands:
```
python -m venv env
env\Scripts\activate # or source env/bin/activate on mac
pip install -r requirements.txt
python manange.py tailwind install
python manage.py migrate
python manage.py tailwind start # run tailwind
```

Do note that `python manage.py tailwind start` will "hog" your terminal. To run the development server, open a new terminal and run
```
python manage.py runserver
```
