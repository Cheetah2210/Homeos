"""
Homeos Automated Verification & Integration Test Suite
"""

import os
import sys

# Proactively ensure the parent directory is pinned in the path 
# so tests can always locate 'core' and 'config' regardless of execution context
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
