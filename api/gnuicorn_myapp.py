from main import app as flask_app

app = flask_app.aiohttp_app

# Run by doing
# gunicorn api:app -k aiohttp.worker.GunicornWebWorker -b localhost:8080
