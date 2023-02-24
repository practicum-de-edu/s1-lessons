#!/usr/bin/env python3

import os

from run_checker import submit

submit(
    os.path.dirname(os.path.abspath(__file__)),
    'de01040402_user_contacts_client_id_not_null')
