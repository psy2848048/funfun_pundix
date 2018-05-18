import json

with open('../config/env.json') as f:
    DBINFO = json.load(f)
