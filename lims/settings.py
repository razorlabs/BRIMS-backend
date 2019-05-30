# local settings to inject "local" as a data source model default

import os
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURE_DIRS = (
   os.path.join(PROJECT_DIR, 'fixtures'),
)
