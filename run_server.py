import sys, os
# Ensure the project directory is first in sys.path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Now import and run the Flask app
from app import app

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
