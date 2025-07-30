# Minimal test deployment
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Test deployment working! Calculator Suite coming soon."

@app.route('/health')
def health():
    return {"status": "healthy", "message": "Test deployment is running"}

if __name__ == '__main__':
    app.run(debug=True)