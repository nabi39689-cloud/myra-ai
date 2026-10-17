import traceback
try:
    from app import app as flask_app
    flask_app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
except Exception:
    traceback.print_exc()
