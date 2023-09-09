import datetime
from itertools import product
from multiprocessing import Process
from typing import Dict, List

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


def set_process_state(is_running: bool, window: sg.Window) -> bool:
    """
    Update the process state displayed on a PySimpleGUI window.

    This function updates a PySimpleGUI window element ("F3") to display the current process state
    (either "PAUSED" or "RUNNING") and changes the button color accordingly.

    Args:
        is_running (bool): A boolean indicating whether the process is running.
        window (sg.Window): The PySimpleGUI window to update.

    Returns:
        bool: The updated process state (is_running).

    Example:
        >>> window = sg.Window("My App", layout)
        >>> is_running = True
        >>> set_process_state(is_running, window)
    """
    window.Element("F3").Update(
        ("PAUSED", "RUNNING")[is_running],
        button_color=(("white", ("red", "green")[is_running])),
    )
    return is_running


def make_layout() -> List[List[sg.Element]]:
    """
    Create the layout for a TFT Augments Helper GUI.

    This function generates a layout for a graphical user interface (GUI) that assists with TFT Augments.
    The layout includes a title, a combo box for selecting ranks, and a "Run" button.

    Returns:
        List[List[sg.Element]]: The PySimpleGUI layout for the TFT Augments Helper GUI.

    Example:
        >>> layout = make_layout()
    """
    layout = [
        [
            [sg.Text("TFT Augments Helper")],
            [
                sg.Combo(
                    RANKS,
                    default_value=RANKS[-1],
                    key="rank",
                    size=(20, 1),
                    readonly=True,
                    enable_events=True,
                )
            ],
            [sg.Button("Run", key="F3")],
        ]
    ]
    return layout


def make_window() -> sg.Window:
    """
    Create and initialize the TFT Augments Helper window.

    This function creates a PySimpleGUI window for the TFT Augments Helper application.
    It sets the window title, layout using the `make_layout` function, and initializes it.

    Returns:
        sg.Window: The initialized TFT Augments Helper window.

    Example:
        >>> window = make_window()
    """
    window = sg.Window("TFT Augments Helper", make_layout(), finalize=True)
    window.bind("<Key-F3>", "F3")
    return window


def init_data(config: Dict[str, str]):
    """
    Initialize data for TFT Augments Helper.

    This function checks the last update date in the configuration and decides whether to update
    the augment pick rate data. If the last update is more than one day ago or if no update date
    is found, it scrapes fresh data for all ranks and tiers and updates the configuration.

    Args:
        config (Dict[str, str]): A dictionary containing the application configuration.

    Returns:
        None
    """
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


def kill_process(p: Process) -> None:
    """
    Terminate a Process if it is running.

    This function terminates a Process represented by a `Process` object if it is running.

    Args:
        p (Process): The Process to terminate, if running.

    Returns:
        None
    """
    if p:
        p.terminate()


def main_gui():
    """
    Run the TFT Augments Helper GUI application.

    This function initializes the TFT Augments Helper GUI, including loading configuration,
    initializing data, and creating the main window. It also handles user interactions and
    manages the state of the application.

    Returns:
        None
    """
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
        print(f"Values are : {values}")

        if event in (sg.WIN_CLOSED, "Exit", None):
            kill_process(p)
            window.close()
            break
        if event == "rank":
            kill_process(p)
            edit_config("rank", values["rank"], config)
        if event == "F3":
            down_f3 = set_process_state(not down_f3, window)
        if down_f3:
            print("Starting process")
            p = Process(
                target=process,
            )
            p.start()
        else:
            kill_process(p)


if __name__ == "__main__":
    main_gui()