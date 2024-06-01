import time
import pyautogui
import configparser
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Read settings from the INI file
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), "ReconnectionMacroSettings.ini")
config.read(config_file)

# Load position map
position_map = {}
for name, value in config.items("PositionMap"):
    x, y = map(int, value.split("|"))
    position_map[name.lower()] = (x, y)  # Convert keys to lowercase for consistency

# Load toggles map
toggles_map = {}
for name, value in config.items("ToggleSetting"):
    toggles_map[name.lower()] = config.getboolean("ToggleSetting", name)

# Load number value map
number_value_map = {}
for name, value in config.items("NumberSetting"):
    number_value_map[name.lower()] = config.getint("NumberSetting", name)

def space_out_positions(position, space_by):
    x, y = position
    higher = (x - space_by, y - space_by)
    lower = (x + space_by, y + space_by)
    spread = [(x - space_by, y - space_by), (x + space_by, y + space_by)]
    return higher, lower, spread

def enable_autofarm():
    if toggles_map["userownsautofarm"]:
        auto_farm_tl = position_map["autofarmtl"]
        auto_farm_br = position_map["autofarmbr"]
        auto_farm = position_map["autofarm"]

        pixel_color = pyautogui.pixel(auto_farm_tl[0], auto_farm_tl[1])
        if pixel_color == (0xFF, 0x10, 0x55):
            pyautogui.click(auto_farm[0], auto_farm[1])
            time.sleep(0.2)
        elif pixel_color == (0x82, 0xF6, 0x0F):
            pyautogui.click(auto_farm[0], auto_farm[1])
            time.sleep(0.5)
            pyautogui.click(auto_farm[0], auto_farm[1])
            time.sleep(0.2)

def disconnected_check():
    logging.debug("Checking for disconnect box")
    logging.debug(position_map)
    
    dcbls = space_out_positions(position_map["disconnectedbackgroundleftside"], 5)[-1]
    dcbrs = space_out_positions(position_map["disconnectedbackgroundrightside"], 5)[-1]
    rcb = space_out_positions(position_map["reconnectbutton"], 10)[-1]

    # Colors you captured
    left_side_color1 = (39, 40, 35)
    left_side_color2 = (39, 40, 35)
    right_side_color1 = (62, 61, 51)
    right_side_color2 = (62, 61, 51)
    reconnect_button_color1 = (39, 40, 35)
    reconnect_button_color2 = (39, 40, 35)

    actual_left_color1 = pyautogui.pixel(dcbls[0][0], dcbls[0][1])
    actual_left_color2 = pyautogui.pixel(dcbls[1][0], dcbls[1][1])
    actual_right_color1 = pyautogui.pixel(dcbrs[0][0], dcbrs[0][1])
    actual_right_color2 = pyautogui.pixel(dcbrs[1][0], dcbrs[1][1])
    actual_reconnect_color1 = pyautogui.pixel(rcb[0][0], rcb[0][1])
    actual_reconnect_color2 = pyautogui.pixel(rcb[1][0], rcb[1][1])

    logging.debug(f"Left side actual colors: {actual_left_color1} {actual_left_color2}")
    logging.debug(f"Right side actual colors: {actual_right_color1} {actual_right_color2}")
    logging.debug(f"Reconnect button actual colors: {actual_reconnect_color1} {actual_reconnect_color2}")

    left_side_pixel = (pyautogui.pixelMatchesColor(dcbls[0][0], dcbls[0][1], left_side_color1, tolerance=100) and
                       pyautogui.pixelMatchesColor(dcbls[1][0], dcbls[1][1], left_side_color2, tolerance=100))
    right_side_pixel = (pyautogui.pixelMatchesColor(dcbrs[0][0], dcbrs[0][1], right_side_color1, tolerance=100) and
                        pyautogui.pixelMatchesColor(dcbrs[1][0], dcbrs[1][1], right_side_color2, tolerance=100))
    reconnect_button_pixel = (pyautogui.pixelMatchesColor(rcb[0][0], rcb[0][1], reconnect_button_color1, tolerance=100) and
                              pyautogui.pixelMatchesColor(rcb[1][0], rcb[1][1], reconnect_button_color2, tolerance=100))

    logging.debug(f"Left side pixel match: {left_side_pixel}")
    logging.debug(f"Right side pixel match: {right_side_pixel}")
    logging.debug(f"Reconnect button pixel match: {reconnect_button_pixel}")

    return left_side_pixel and right_side_pixel and reconnect_button_pixel


def teleport_to_zone(zone_name):
    tp_button = position_map["tpbutton"]
    xbr = position_map["xbr"]
    xtl = position_map["xtl"]
    search_bar = position_map["searchbar"]
    tp_middle = position_map["tpuimiddle"]

    time.sleep(0.4)
    pyautogui.click(tp_button[0], tp_button[1])
    time.sleep(0.4)

    break_time = time.time()
    secondary_break_time = time.time()

    while True:
        if pyautogui.pixelMatchesColor(xtl[0], xtl[1], (0xEC, 0x0D, 0x3A), tolerance=10):
            break

        if time.time() - break_time >= 6:
            pyautogui.click(tp_button[0], tp_button[1])
            break_time = time.time()

        if time.time() - secondary_break_time >= 20:
            logging.info("Yikes")
            break

        time.sleep(0.1)

    time.sleep(0.3)
    pyautogui.click(search_bar[0], search_bar[1])
    time.sleep(0.1)
    pyautogui.write(zone_name)

    for _ in range(3):
        time.sleep(0.25)
        pyautogui.click(tp_middle[0], tp_middle[1])

    time.sleep(number_value_map["tpwaittime"] / 1000)

def main():
    # Initial delay to allow for manual interruption
    logging.info("Starting in 5 seconds... Press Ctrl+C to stop.")
    time.sleep(5)

    while True:
        logging.debug("Checking for disconnect box")
        if disconnected_check():
            break_time = time.time()
            while True:
                pyautogui.click(position_map["reconnectbutton"][0], position_map["reconnectbutton"][1])
                time.sleep(0.1)

                tp_button_tl = position_map["tpbuttontl"]
                tp_button_br = position_map["tpbuttonbr"]
                if pyautogui.pixelMatchesColor(tp_button_tl[0], tp_button_tl[1], (0xEC, 0x0D, 0x3A), tolerance=12):
                    break

                time.sleep(0.1)
                if time.time() - break_time >= 45:
                    break

            time.sleep(1)
            teleport_to_zone("Prison HQ")
            pyautogui.keyDown("d")
            time.sleep(number_value_map["distanceintozone"] / 1000)
            pyautogui.keyUp("d")
            enable_autofarm()

        time.sleep(9)
        pyautogui.click(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
        logging.info("Clicked in the middle of the screen")

if __name__ == "__main__":
    main()
