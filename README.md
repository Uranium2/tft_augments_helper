# TFT Augments Helper

TFT Augments Helper is a Python-based project that automates the collection and display of stats over augments in Teamfight Tactics (TFT) based on player ranks. It scrapes data from a designated website daily and, when launched during augments rounds, uses Optical Character Recognition (OCR) via Tesseract to identify the augments in the game and display their stats according to the selected player rank.

**Please note that TFT Augments Helper may have some bugs; please read the `Disclaimer` section!**

## Disclaimer

1. This project should manage every screen resolution with a 16:9 ratio. Note that image cropping for the OCR was originally designed for a WQHD screen (2560 x 1440). It has also been tested on:

- FHD (1920 x 1080)
- HD Ready (1280 x 720)

Using this application with a different ratio (21:9 or 4:3) may result in inaccurate results. Additionally, you must install the required dependencies, including Tesseract, before using the application.

2. This project does not support the `Hyper roll` mode. The augments rounds are not at ("2-1", "3-2", "4-2").
3. This project does not work in WSL.
4. This project might not work in Linux-based OS (I never installed LoL on Linux).
5. This project was only tested with Python 3.10 and Windows 10.

## Features

- Daily web scraping to collect data on the most picked, average position and win rate on augments ranks (Iron, Bronze, Silver, Gold, Platinum, Diamond, Master, Grandmaster, Challenger)
- OCR-based augmentation detection during TFT rounds. ("2-1", "3-2", "4-2") Does not support `Hyper roll` mode at the moment.
- Display of stats for augments based on the selected player rank.

## Prerequisites

Before using TFT Augments Helper, make sure you have the following prerequisites installed:

- Python (3.7 or higher)
- Tesseract OCR (local installation)
- Required Python packages in `requirements.txt`

## Usage

1. Clone this repository to your local machine.

```console
git clone https://github.com/uranium2/tft_augments_helper.git
cd tft_augments_helper
```

2. Install the required Python packages.

```console
py -m venv .venv
.venv/Scripts/activate.bat
pip install -r requirements.txt
```

Ensure that Tesseract OCR is installed and configured correctly on your system. You can download it from the official [Tesseract GitHub repository](https://github.com/UB-Mannheim/tesseract).

https://tesseract-ocr.github.io/tessdoc/Installation.html

Make sure your binary for tesseract is at `C:\Program Files\Tesseract-OCR\tesseract.exe`

4. Launch GUI

```console
py main.py
```
Select on the GUI the rank you want to check the stats of the augments.

5. Run

Press `Run` on the GUI and play your TfT game. It should print stuff in console every 2-5 seconds to get the round number and if needed the augments names on screen.

## Demo

- Launch code.

```console
(.venv) tft_augments_helper>py main.py
```
- Select the rank to check stats from drop down menu. And click `Run` before or during a TFT game.

![plot](./img/demo_0.png)

- The button must show `Running`. Press on `Running` to stop round detection and augments stats search.

![plot](./img/demo_1.png)

- In red are the stats of the augments from the rank you selected. You can change the rank at any time, even during augment rounds.

![plot](./img/demo_2.png)

- Overlay display is refreshed every 3 seconds. So you can reroll your augments and wait for new stats.

![plot](./img/demo_3.png)


## TODO

- Clean code, make more constants
- `Hyper roll` mode, make interface select box, save it, load at startup + change constant values for rounds. Make rounds constant in a dict
- More decision making? Eco? Roll? Level up?
- change scrapping for https://tactics.tools/augments/gm ?
- Use riotwatcher for tft api? https://github.com/pseudonym117/Riot-Watcher/blob/10bf58ebd6a4a2f543367551e710609e3255e74d/src/riotwatcher/_apis/team_fight_tactics/MatchApi.py#L10


## License

This project is licensed under the MIT License - see the LICENSE file for details.
