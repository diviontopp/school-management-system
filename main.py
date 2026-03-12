from app import app

# This allows 'gunicorn main:app' to work as a fail-safe
# even if Railway's Railpack takes over.
if __name__ == "__main__":
    app.run()
