import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cograder_clone.apps import create_app

app = create_app()
