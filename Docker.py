# CMD ["gunicorn", "-w", "4", "app:app"]
gunicorn -w 4 -b 0.0.0.0:5000 source.views:app

 # /Users/goyalpushkar/GitHub/factChecker/.venv/bin/python source/views.py