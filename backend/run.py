import sys
import os

# Add the project root to the Python path to import data_clean.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    # Get port from environment variable for deployment compatibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
