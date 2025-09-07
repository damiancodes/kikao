web: cd backend && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
worker: cd backend && celery -A config worker --loglevel=info
beat: cd backend && celery -A config beat --loglevel=info
