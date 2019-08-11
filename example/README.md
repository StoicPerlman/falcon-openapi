Example app to show proper folder structure

Run with:

```bash
pipenv shell
pipenv install

gunicorn --reload look.app # OR python look/app.py
curl http://127.0.0.1:8000/controller
```