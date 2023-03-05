#!/usr/bin/env python3

import os

from run_checker import submit


submit(
    os.path.dirname(os.path.abspath(__file__)),
    'de01070301_select_max_date')
