web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
release: flask init-db && flask seed-global-data