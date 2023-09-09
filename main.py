import datetime
from itertools import product
from multiprocessing import Process

import PySimpleGUI as sg

from src.config import edit_config, load_config
from src.core import process
from src.utils import scrap_augments_pick_rate

NB_AUGMENTS = 3
RANKS = [
    "iron",
    "bronze",
    "silver",
    "gold",
    "platinum",
    "diamond",
    "master",
    "grandmaster",
    "challenger",
]


def set_process_state(is_running, window):
    window.Element("F3").Update(
        ("PAUSED", "RUNNING")[is_running],
        button_color=(("white", ("red", "green")[is_running])),
    )
    return is_running


def make_layout():
    layout = [
        [
            [sg.Text("TFT Augments Helper")],
            [
                sg.Combo(
                    RANKS,
                    default_value="gold",
                    key="-OPTION-",
                    size=(20, 1),
                    readonly=True,
                )
            ],
            [sg.Button("Run", key="F3")],
        ]
    ]
    return layout


def make_window():
    window = sg.Window("TFT Augments Helper", make_layout(), finalize=True)
    window.bind("<Key-F3>", "F3")
    return window


def init_data(config):
    date_format = "%Y-%m-%d"
    date_key = "fetch_last_update"
    current_date = datetime.date.today()
    make_scrap = False

    if date_key in config:
        condif_date = datetime.datetime.strptime(config[date_key], date_format).date()

        date_difference = current_date - condif_date

        if date_difference.days >= 1:
            make_scrap = True
    else:
        make_scrap = True
    print(f"make_scrap = {make_scrap}")
    if make_scrap:
        # Get fresh data pick rate
        for rank, tier in product(RANKS, range(1, NB_AUGMENTS + 1)):
            augment_data = scrap_augments_pick_rate(rank, tier)
            edit_config(f"{rank}_{tier}", augment_data, config)

        edit_config(date_key, current_date.strftime(date_format), config)


def main_gui():
    config = load_config()

    init_data(config)
    # Create the window
    window = make_window()

    down_f3 = False
    p = None

    # Create an event loop
    while True:
        event, values = window.read()

        print(f"Event is : {event}")

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "F3":
            down_f3 = set_process_state(not down_f3, window)
        if down_f3:
            print("Starting process")
            p = Process(
                target=process,
                args=(config,),
            )
            p.start()
        else:
            if p:
                p.terminate()

    window.close()
    if p:
        p.terminate()


if __name__ == "__main__":
    main_gui()
