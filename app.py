from flask import Flask, render_template, request, Response
from scanner import scan
import webbrowser
import threading
from functools import wraps

app = Flask(__name__)

# -----------------------------
# 🔐 BASIC AUTH CREDENTIALS
# -----------------------------
USERNAME = "mendijd"   # change this to your preferred username
PASSWORD = "Mygit@dapada60"   # change this to your preferred password

def check_auth(u, p):
    """Check if username and password are correct."""
    return u == USERNAME and p == PASSWORD

def authenticate():
    """Sends 401 response for unauthorized access."""
    return Response(
        'Could not verify access', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    """Decorator to require authentication on a route."""
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
@requires_auth   # protect your dashboard route
def dashboard():
    # Scan all tickers and get their MA signals + put suggestions
    stocks = scan(interval="1d")
    return render_template("dashboard.html", stocks=stocks)

# 🔹 AUTO OPEN BROWSER
def open_browser():
    """Open default browser after server starts."""
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Open browser in a separate thread so it doesn't block the server
    threading.Timer(1, open_browser).start()
    # Run Flask server
    app.run(host="127.0.0.1", port=5000, debug=False)
