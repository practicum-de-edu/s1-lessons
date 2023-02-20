#!/usr/bin/env python3

import os

from run_checker import submit

DE_S1_TEST = 'de01032202'

submit(os.path.dirname(os.path.abspath(__file__)), DE_S1_TEST)
