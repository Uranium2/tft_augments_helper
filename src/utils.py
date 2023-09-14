import re

import numpy as np
import pyautogui
import requests
from bs4 import BeautifulSoup


def cleanse_text(text: str) -> str:
    """
    Remove punctuation (excluding parentheses) and text within parentheses from the given text.

    Args:
        text (str): The input text containing punctuation and parentheses.

    Returns:
        str: The input text with punctuation (excluding parentheses) and text within parentheses removed,
             and newline characters are removed.
    """
    # Remove punctuation (excluding parentheses)
    text_without_punctuation = re.sub(r"[^\w\s()]", "", text)

    # Remove text within parentheses and the parentheses themselves
    text_without_parentheses = re.sub(r"\([^)]*\)", "", text_without_punctuation)

    return text_without_parentheses.strip().replace("\n", "")


def cleanse_text_legend(text: str) -> str:
    """
    Removes the word '(Legend)' from the input text.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text with '(Legend)' removed.
    """
    cleaned_text = text.replace("(Legend)", "")
    return cleaned_text


def scrap_augments_stats(rank: str, tier: str) -> dict:
    """
    Scrapes augments stats from the Mobalytics website for a given rank and tier.

    Args:
        rank (str): The player's rank.
        tier (int): The player's tier.

    Returns:
        dict: A dictionary containing augments names as keys and stats as values.
    """
    url = f"https://app.mobalytics.gg/tft/tier-list/augments?rank={rank}&tier={tier}"
    print("Getting stats from", rank, tier)

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        augment_data = {}
        # Find the container that holds all augment data
        augment_containers = soup.find_all(class_="m-ub27pe")

        # Loop through each augment container and extract the data
        for container in augment_containers:
            augment_name = cleanse_text_legend(
                container.find(class_="m-po6via").text.strip()
            )
            m_virx81 = container.find_all(class_="m-virx8l")
            avg_place = m_virx81[0].text.strip()
            win_rate = m_virx81[1].text.strip()
            pick_rate = m_virx81[2].text.strip()

            augment_data[augment_name] = {}
            augment_data[augment_name]["pick_rate"] = pick_rate
            augment_data[augment_name]["avg_place"] = avg_place
            augment_data[augment_name]["win_rate"] = win_rate

        return augment_data

    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        response.raise_for_status()


def crop_screenshot(img: np.ndarray, x: int, y: int, h: int, w: int) -> np.ndarray:
    """
    Crop a screenshot image to the specified dimensions.

    Args:
        img (numpy.ndarray): The input screenshot image.
        x (int): The x-coordinate of the top-left corner of the region to be cropped.
        y (int): The y-coordinate of the top-left corner of the region to be cropped.
        h (int): The height of the region to be cropped.
        w (int): The width of the region to be cropped.

    Returns:
        numpy.ndarray: The cropped image.
    """
    return img[y : y + h, x : x + w]


def take_screenshot(pyautogui_default_color: bool) -> np.ndarray:
    """
    Capture a screenshot using PyAutoGUI.

    Args:
        pyautogui_default_color (bool): Whether to return the image in the default color format.

    Returns:
        numpy.ndarray: The captured screenshot.
    """
    img = np.array(pyautogui.screenshot())
    if pyautogui_default_color:
        return img
    return img[:, :, ::-1]


def translate_coordinates(old_x, old_y, new_resolution):
    """
    Translates coordinates from an old screen resolution (2560, 1440) to a new screen resolution.

    Args:
        old_x (int): The x-coordinate in the old resolution.
        old_y (int): The y-coordinate in the old resolution.
        new_resolution (tuple): The new screen resolution as a tuple (new_width, new_height).

    Returns:
        tuple: The translated coordinates as a tuple (new_x, new_y).
    """
    old_width, old_height = (2560, 1440)  # This is the resolution I work with
    (
        new_width,
        new_height,
    ) = new_resolution  # This is the resolution of other potential users

    new_x = (old_x / old_width) * new_width
    new_y = (old_y / old_height) * new_height

    return int(new_x), int(new_y)


def translate_distance(old_distance, new_resolution):
    """
    Translates a distance from an old screen resolution (2560, 1440) to a new screen resolution.

    Args:
        old_distance (float): The distance in the old resolution.
        new_resolution (tuple): The new screen resolution as a tuple (new_width, new_height).

    Returns:
        float: The translated distance in the new resolution.
    """
    old_width, old_height = (2560, 1440)  # This is the resolution I work with
    new_width, new_height = new_resolution

    # Calculate the scaling factors for width and height separately
    width_scale = new_width / old_width
    height_scale = new_height / old_height

    # Use the minimum scaling factor to ensure the aspect ratio is maintained
    scale_factor = min(width_scale, height_scale)

    # Translate the old distance to the new resolution
    new_distance = old_distance * scale_factor

    return int(new_distance)
