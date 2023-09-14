import re
from tkinter import Canvas, Tk
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pytesseract
from fuzzywuzzy import fuzz

from src.config import load_config
from src.utils import cleanse_text, crop_screenshot, take_screenshot, translate_distance

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TRANSPARENT_COLOR = "grey15"


def live_image_process(rectangle: List[int]) -> np.ndarray:
    """
    Perform real-time image processing on a screenshot within a specified rectangle.

    This function captures a screenshot and performs the following operations within the specified
    rectangle:

    1. Capture a screenshot.
    2. Crop the screenshot to the specified rectangle (x, y, height, width).
    3. Convert the cropped image to grayscale.
    4. Apply binary inversion and Otsu's thresholding to create a binary image.

    Args:
        rectangle (List[int]): A rectangle defined as [x, y, height, width] where:
            - x (int): The x-coordinate of the top-left corner of the rectangle.
            - y (int): The y-coordinate of the top-left corner of the rectangle.
            - height (int): The height of the rectangle.
            - width (int): The width of the rectangle.

    Returns:
        np.ndarray: The processed binary image.
    """
    x = rectangle[0]
    y = rectangle[1]
    h = rectangle[2]
    w = rectangle[3]

    img = take_screenshot(False)
    img = crop_screenshot(img, x, y, h, w)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return img


def find_approximate_key(
    dictionary: Dict[str, str], search_term: str
) -> Tuple[Optional[str], int]:
    """
    Find the key in a dictionary that best matches a search term using fuzzy string matching.

    This function searches for the dictionary key that best matches the given search term using fuzzy string matching.
    It returns both the best-matching key and the matching score.

    Args:
        dictionary (Dict[str, str]): A dictionary with string keys.
        search_term (str): The search term to match against dictionary keys.

    Returns:
        Tuple[Optional[str], int]: A tuple containing the best-matching key (or None if no match is found)
        and the matching score.
    """
    best_match = None
    best_score = 0
    search_term = search_term.lower()
    for key in dictionary.keys():
        score = fuzz.ratio(key.lower(), search_term)
        if score > best_score:
            best_match = key
            best_score = score

    return best_match, best_score


def is_augment_round(x: int, y: int, screen_resolution: Tuple[int, int]) -> bool:
    """
    Determine if a screenshot of a game round is an 'augment' round based on OCR text analysis.

    This function captures a screenshot of a game round within a specified rectangle and performs OCR text
    analysis to determine if the round is an 'augment' round. An 'augment' round is detected if the text
    extracted from the screenshot matches specific patterns.

    Args:
        x (int): The x-coordinate of the top-left corner of the rectangle.
        y (int): The y-coordinate of the top-left corner of the rectangle.
        screen_resolution (Tuple[int, int]): The screen resolution as a tuple (width, height).

    Returns:
        bool: True if the round is an 'augment' round, False otherwise.
    """
    # Distance to change 70, 300
    height = translate_distance(70, screen_resolution)
    width = translate_distance(300, screen_resolution)
    rectangle = (x, y, height, width)
    img = live_image_process(rectangle)
    cv2.imwrite(f"img/round.png", img)
    is_aug_round = False

    # Try multiple presets of pytesseract, preset 6 should detect most of it.
    for i in range(13, 5, -1):
        text = (
            pytesseract.image_to_string(img, config=f"--psm {i}")
            .strip()
            .replace("\n", "")
        )
        pattern = r"\d+-?\d+"
        matches = re.findall(pattern, text)
        if not matches:
            round_number = None
        else:
            round_number = matches[0]
        # Format round with `-` and also concat, low res OCR does not get the `-`
        if round_number in ["2-1", "3-2", "4-2", "21", "32", "42"]:
            is_aug_round = True
            break

    if round_number:
        print(f"Round {round_number}: '{text}'")
    else:
        print(f"Not an augment Round: '{text}'")
    return is_aug_round


def get_augment_stats(
    config: Dict[str, Dict[str, str]],
    x: int,
    y: int,
    screen_resolution: Tuple[int, int],
) -> Tuple[str, Dict[str, any]]:
    """
    Get the stats of an augment based on OCR text analysis and a configuration dictionary.

    This function captures a screenshot of an augment's stats from a specified rectangle
    and matches the extracted text against a configuration dictionary to determine the augment's stats.

    Args:
        config (Dict[str, str]): A dictionary containing augment stats data.
        x (int): The x-coordinate of the top-left corner of the rectangle.
        y (int): The y-coordinate of the top-left corner of the rectangle.
        screen_resolution (Tuple[int, int]): The screen resolution as a tuple (width, height).

    Returns:
        str: The name of the augment chosen.
        dict: The stats of the augment as a dict
    """
    # Distance 300, distance 30, distance 70, distance 600
    x_padding = translate_distance(300, screen_resolution)
    y_padding = translate_distance(30, screen_resolution)
    width = translate_distance(70, screen_resolution)
    height = translate_distance(600, screen_resolution)
    rectangle = (x - x_padding, y - y_padding, width, height)

    img = live_image_process(rectangle)

    cv2.imwrite(f"img/{x}.png", img)

    text = pytesseract.image_to_string(img, config="--psm 6")

    text = cleanse_text(text)

    key_to_keep = None
    best_score = 0
    stats = {}
    for i in range(1, 4):
        augment_dict = config[f"""{config["rank"]}_{i}"""]
        if text in augment_dict:
            key_to_keep = text
            stats = augment_dict[key_to_keep]
            best_score = 100
            break
        key, score = find_approximate_key(augment_dict, text)

        if score > best_score:
            best_score = score
            key_to_keep = key
            stats = augment_dict[key_to_keep]

    print(
        f"OCR : {text}, nearest key: {key_to_keep}, stats: {stats}, best_score: {best_score}"
    )

    return key_to_keep, stats


def display_stats(
    root: Tk,
    canvas: Canvas,
    x_positions: List[int],
    middle_x: int,
    middle_y: int,
    screen_resolution: Tuple[int, int],
) -> None:
    """
    Display the stats of augments on a canvas within a specified region.

    This function updates the canvas to display the stats of augments at the specified
    x positions within a rectangular region. The display is updated based on the result of the
    `is_augment_round` function, and it periodically reschedules itself using `root.after`.

    Args:
        root (Tk): The Tkinter root window.
        canvas (Canvas): The Tkinter canvas to display stats on.
        x_positions (List[int]): A list of x-coordinates where augment stats should be displayed.
        middle_x (int): The x-coordinate of the center of the canvas.
        middle_y (int): The y-coordinate of the center of the canvas.
        screen_resolution (Tuple[int, int]): The screen resolution as a tuple (width, height).
    """
    canvas.delete("all")
    timer = 3000

    stats_buffer = []
    # distance to change 300
    x_padding = translate_distance(300, screen_resolution)
    y_padding = translate_distance(100, screen_resolution)
    if is_augment_round(middle_x - x_padding, 0, screen_resolution):
        config = load_config()
        for x_position in x_positions:
            augment_name, stats = get_augment_stats(
                config, x_position, middle_y, screen_resolution
            )
            stats_buffer.append((augment_name, stats, x_position))
    else:
        timer = 5000

    if not any(item[0] is None for item in stats_buffer):
        for augment_name, stats, x_position in stats_buffer:
            text_to_display = f"""pick_rate : {stats["pick_rate"]}\navg_place : {stats["avg_place"]}\nwin_rate : {stats["win_rate"]}"""

            # Distance to change 100
            canvas.create_text(
                x_position,
                middle_y - y_padding,
                text=text_to_display,
                font=("Helvetica", 20),
                fill="red",
            )

    root.after(
        timer,
        lambda: display_stats(
            root, canvas, x_positions, middle_x, middle_y, screen_resolution
        ),
    )


def process() -> None:
    """
    Process and display game augment stats on a full-screen Tkinter window.

    This function initializes a full-screen Tkinter window, captures screen dimensions, and calculates
    positions for displaying augment stats using OCR. It then creates and displays a canvas for
    rendering the stats based on the provided configuration.
    """
    root = Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    screen_resolution = (screen_width, screen_height)

    middle_x = screen_width // 2  # Good value for any screen
    middle_y = screen_height // 2  # Good value for any screen

    # Get X values for OCR and display
    distance_to_border = min(middle_x, middle_y)  # Good value for any screen
    left_position = middle_x - distance_to_border  # Good value for any screen
    right_position = middle_x + distance_to_border  # Good value for any screen
    distance_to_border_2 = min(left_position, middle_y)  # Good value for any screen
    left_position = middle_x - distance_to_border_2  # Good value for any screen
    right_position = middle_x + distance_to_border_2  # Good value for any screen

    x_positions = [left_position, middle_x, right_position]  # Good value for any screen

    root.config(bg=TRANSPARENT_COLOR)
    root.attributes("-transparentcolor", TRANSPARENT_COLOR)
    root.attributes("-topmost", True)
    root.attributes("-fullscreen", True)

    canvas = Canvas(root, bg=TRANSPARENT_COLOR, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    display_stats(root, canvas, x_positions, middle_x, middle_y, screen_resolution)
    root.mainloop()
