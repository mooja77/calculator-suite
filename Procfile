web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app
release: flask init-db && flask seed-global-data