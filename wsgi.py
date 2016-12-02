import app as weibo

app = weibo.configured_app()

# gunicorn appcorn:app
# nohup gunicorn -b '0.0.0.0:80' appcorn:app &

# wsgi
