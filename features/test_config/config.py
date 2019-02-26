# This code was adopted from https://github.com/Rhoynar/python-selenium-bdd
import os
import json

settings = None


def load_settings():
    global settings
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../framework/settings.json')) as f:
        settings = json.load(f)
load_settings()