import re
from tkinter import Canvas, Tk
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pytesseract
from fuzzywuzzy import fuzz

from src.config import load_config
from src.utils import (
    crop_screenshot,
    remove_punctuation_and_parentheses,
    take_screenshot,
)

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

    Example:
        >>> rectangle = [100, 100, 200, 200]  # Define a rectangle
        >>> processed_image = live_image_process(rectangle)  # Process the image
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

    Example:
        >>> my_dict = {'apple': 'fruit', 'banana': 'fruit', 'carrot': 'vegetable'}
        >>> key, score = find_approximate_key(my_dict, 'bananna')
        >>> key
        'banana'
        >>> score
        86
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


def is_augment_round(x: int, y: int) -> bool:
    """
    Determine if a screenshot of a game round is an 'augment' round based on OCR text analysis.

    This function captures a screenshot of a game round within a specified rectangle and performs OCR text
    analysis to determine if the round is an 'augment' round. An 'augment' round is detected if the text
    extracted from the screenshot matches specific patterns.

    Args:
        x (int): The x-coordinate of the top-left corner of the rectangle.
        y (int): The y-coordinate of the top-left corner of the rectangle.

    Returns:
        bool: True if the round is an 'augment' round, False otherwise.

    Example:
        >>> is_augment_round(100, 100)
        True
    """
    rectangle = (x, y, 70, 300)
    img = live_image_process(rectangle)
    cv2.imwrite(f"img/round.png", img)
    is_aug_round = False

    for i in range(13, 5, -1):
        text = pytesseract.image_to_string(img, config=f"--psm {i}").strip()
        pattern = r"\d+-\d+"
        matches = re.findall(pattern, text)
        if not matches:
            round = 0
        else:
            round = matches[0]
        if round in ["2-1", "3-2", "4-2"]:
            is_aug_round = True
            break
    print(f"round {round} from text '{text}'")
    return is_aug_round


def get_augment_pick_rate(config: Dict[str, str], x: int, y: int) -> str:
    """
    Get the pick rate of an agument based on OCR text analysis and a configuration dictionary.

    This function captures a screenshot of an agument's pick rate from a specified rectangle
    and matches the extracted text against a configuration dictionary to determine the augment's pick rate.

    Args:
        config (Dict[str, str]): A dictionary containing augment pick rate data.
        x (int): The x-coordinate of the top-left corner of the rectangle.
        y (int): The y-coordinate of the top-left corner of the rectangle.

    Returns:
        str: The pick rate of the agument as a string, e.g., "0.0%".

    Example:
        >>> config = {
        ...     "challenger_1": {
        ...         "augment_1": "0.5%",
        ...         "augment_2": "0.3%",
        ...     },
        ...     "challenger_2": {
        ...         "augment_3": "0.1%",
        ...         "augment_4": "0.2%",
        ...     },
        ... }
        >>> get_augment_pick_rate(config, 100, 100)
        '0.5%'
    """
    rectangle = (x - 300, y - 30, 70, 600)

    img = live_image_process(rectangle)

    cv2.imwrite(f"img/{x}.png", img)

    text = pytesseract.image_to_string(img, config="--psm 6").strip()

    text = remove_punctuation_and_parentheses(text)

    key_to_keep = None
    best_score = 0
    pick_rate = "0.0%"
    for i in range(1, 4):
        augment_dict = config[f"""{config["rank"]}_{i}"""]
        if text in augment_dict:
            key_to_keep = text
            pick_rate = augment_dict[key_to_keep]
            break
        key, score = find_approximate_key(augment_dict, text)

        if score > best_score:
            best_score = score
            key_to_keep = key
            pick_rate = augment_dict[key_to_keep]

    print(f"OCR : {text}, nearest key: {key_to_keep}, pick rate: {pick_rate}")

    return pick_rate


def display_pick_rate(
    root: Tk, canvas: Canvas, x_positions: List[int], middle_x: int, middle_y: int
):
    """
    Display the pick rates of augments on a canvas within a specified region.

    This function updates the canvas to display the pick rates of augments at the specified
    x positions within a rectangular region. The display is updated based on the result of the
    `is_augment_round` function, and it periodically reschedules itself using `root.after`.

    Args:
        root (Tk): The Tkinter root window.
        canvas (Canvas): The Tkinter canvas to display pick rates on.
        x_positions (List[int]): A list of x-coordinates where augment pick rates should be displayed.
        middle_x (int): The x-coordinate of the center of the canvas.
        middle_y (int): The y-coordinate of the center of the canvas.
        config (Dict[str, Dict[str, str]]): A dictionary containing augment pick rate data.

    Returns:
        None
    """
    canvas.delete("all")
    timer = 3000

    if is_augment_round(middle_x - 300, 0):
        config = load_config()
        for x_position in x_positions:
            canvas.create_text(
                x_position,
                middle_y - 100,
                text=get_augment_pick_rate(config, x_position, middle_y),
                font=("Helvetica", 33),
                fill="red",
            )
    else:
        timer = 5000

    root.after(
        timer,
        lambda: display_pick_rate(root, canvas, x_positions, middle_x, middle_y),
    )


def process():
    """
    Process and display game augment pick rates on a full-screen Tkinter window.

    This function initializes a full-screen Tkinter window, captures screen dimensions, and calculates
    positions for displaying augment pick rates using OCR. It then creates and displays a canvas for
    rendering the pick rates based on the provided configuration.

    Args:
        config (Dict[str, Dict[str, str]]): A dictionary containing augment pick rate data.

    Returns:
        None
    """
    root = Tk()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    middle_x = sw // 2
    middle_y = sh // 2

    # Get X values for OCR and display
    distance_to_border = min(middle_x, middle_y)
    left_position = middle_x - distance_to_border
    right_position = middle_x + distance_to_border
    distance_to_border_2 = min(left_position, middle_y)
    left_position = middle_x - distance_to_border_2
    right_position = middle_x + distance_to_border_2

    x_positions = [left_position, middle_x, right_position]

    root.config(bg=TRANSPARENT_COLOR)
    root.attributes("-transparentcolor", TRANSPARENT_COLOR)
    root.attributes("-topmost", True)
    root.attributes("-fullscreen", True)

    canvas = Canvas(root, bg=TRANSPARENT_COLOR, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    display_pick_rate(root, canvas, x_positions, middle_x, middle_y)
    root.mainloop()
