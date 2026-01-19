from flask import Flask, render_template, request, Response
from scanner import scan
from functools import wraps
from waitress import serve  # Production-ready server
import os

app = Flask(__name__)

# -----------------------------
# 🔐 BASIC AUTH CREDENTIALS
# -----------------------------
USERNAME = "mendijd"
PASSWORD = "Mygit@dapada60"

def check_auth(u, p):
    return u == USERNAME and p == PASSWORD

def authenticate():
    return Response(
        'Could not verify access', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
# -----------------------------
# End of Auth Section
# -----------------------------

# 🔹 DASHBOARD ROUTE
@app.route("/")
@requires_auth
def dashboard():
    stocks = scan(interval="1d")
    return render_template("dashboard.html", stocks=stocks)

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    import os
    from waitress import serve

    # Use port from environment or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Start Waitress (production-ready) server
    print(f"Starting server on http://0.0.0.0:{port} ...")
    serve(app, host="0.0.0.0", port=port)
