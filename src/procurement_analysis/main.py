"""
Main entry point for the Procurement Accessibility Analysis application.
"""

import uvicorn
from .api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

