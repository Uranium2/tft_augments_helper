import re
from tkinter import Canvas, Tk

import cv2
import pytesseract
from fuzzywuzzy import fuzz

from src.utils import (
    crop_screenshot,
    remove_punctuation_and_parentheses,
    take_screenshot,
)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TRANSPARENT_COLOR = "grey15"


def live_image_process(rectangle):
    x = rectangle[0]
    y = rectangle[1]
    h = rectangle[2]
    w = rectangle[3]

    img = take_screenshot(False)
    img = crop_screenshot(img, x, y, h, w)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return img


def find_approximate_key(dictionary, search_term):
    best_match = None
    best_score = 0
    search_term = search_term.lower()
    for key in dictionary.keys():
        score = fuzz.ratio(key.lower(), search_term)
        if score > best_score:
            best_match = key
            best_score = score

    return best_match, best_score


def is_augment_round(x, y):
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


def get_pick_rate(config, x, y):
    rectangle = (x - 300, y - 30, 70, 600)

    img = live_image_process(rectangle)

    cv2.imwrite(f"img/{x}.png", img)

    text = pytesseract.image_to_string(img, config="--psm 6").strip()

    text = remove_punctuation_and_parentheses(text)

    key_to_keep = None
    best_score = 0
    pick_rate = "0.0%"
    for i in range(1, 4):
        augment_dict = config[f"challenger_{i}"]
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


def show_pick_rate(root, canvas, x_positions, middle_x, middle_y, config):
    canvas.delete("all")
    timer = 3000

    if is_augment_round(middle_x - 300, 0):
        for x_position in x_positions:
            canvas.create_text(
                x_position,
                middle_y - 100,
                text=get_pick_rate(config, x_position, middle_y),
                font=("Helvetica", 33),
                fill="red",
            )
    else:
        timer = 5000

    root.after(
        timer,
        lambda: show_pick_rate(root, canvas, x_positions, middle_x, middle_y, config),
    )


def process(config):
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

    show_pick_rate(root, canvas, x_positions, middle_x, middle_y, config)
    root.mainloop()
