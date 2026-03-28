import sys
import os

# Ensure the backend root is on sys.path so `app` can be imported by pytest
sys.path.insert(0, os.path.dirname(__file__))
