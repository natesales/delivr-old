import yaml

with open("config.yml", "r") as config_file:
    configuration = yaml.safe_load(config_file.read())