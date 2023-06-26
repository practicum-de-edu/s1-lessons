import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)).split('Тема')[0])

from run_checker import get_playground


get_playground()
