import os
from yaml import safe_load
from dotenv import load_dotenv


def load_conf() -> dict:
    load_dotenv(dotenv_path="./envsample")
    with open("./config/config.yml") as f:
        data = safe_load(os.path.expandvars(f.read()))
    return dict(data)


config = load_conf()
