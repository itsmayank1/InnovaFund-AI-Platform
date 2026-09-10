"""
Innovation Scoring API Controller (Member 4 Integration)
Mounts seamlessly into the main InnovaFund-AI backend platform.
"""

import os
import sys

# Ensure innovation-scoring-service is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "innovation-scoring-service"))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

from app.api.routes_scoring import router
