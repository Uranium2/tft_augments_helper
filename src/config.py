import json
import os.path

import pydirectinput


def load_json_save() -> dict:
    """
    Load or create a JSON configuration file and return its contents as a dictionary.

    This function checks if a JSON configuration file exists. If not, it creates one with default values.
    It then loads the JSON file and returns its contents as a dictionary.

    Returns:
        dict: The configuration data loaded from the JSON file.

    Example:
        >>> config = load_json_save()
    """
    path = "config\\config.json"
    if not os.path.isfile(path):
        with open(path, "w+") as outfile:
            json.dump(
                {"config_path": path},
                outfile,
                indent=4,
                sort_keys=True,
            )

    with open(path, "r") as f:
        config = json.load(f)
    return config


def save_config(config: dict) -> None:
    """
    Save a dictionary as JSON data to a specified configuration file path.

    This function takes a dictionary of configuration data and saves it as JSON data to the file path
    specified in the "config_path" key of the dictionary.

    Args:
        config (dict): The configuration data to save.

    Returns:
        None

    Example:
        >>> config = {"config_path": "config\\config.json", "setting1": "value1", "setting2": "value2"}
        >>> save_config(config)
    """
    with open(config["config_path"], "w+") as outfile:
        json.dump(config, outfile, indent=4, sort_keys=True)


def edit_config(key: str, value: any, config: dict) -> None:
    """
    Edit a specific key-value pair in the configuration dictionary and save the changes.

    This function allows you to modify a specific key-value pair in the configuration dictionary and
    then saves the updated dictionary to the configuration file.

    Args:
        key (str): The key to edit.
        value (any): The new value to set for the key.
        config (dict): The configuration dictionary to edit and save.

    Returns:
        None

    Example:
        >>> config = load_json_save()
        >>> edit_config("setting1", "new_value", config)
    """
    config[key] = value
    save_config(config)


def load_config() -> dict:
    """
    Load and return the configuration data from a JSON file.

    This function loads the configuration data from the JSON file specified in the "config_path" key of the
    configuration dictionary.

    Returns:
        dict: The configuration data loaded from the JSON file.

    Example:
        >>> config = load_config()
    """
    pydirectinput.PAUSE = False
    config = load_json_save()
    return config
