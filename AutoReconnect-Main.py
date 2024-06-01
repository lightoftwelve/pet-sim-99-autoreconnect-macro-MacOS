import pyautogui
import configparser
import time
import os

# Read settings from Da INI file
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), "ReconnectionMacroSettings.ini")
config.read(config_file)

# Load position map
position_map = {}
for name, value in config.items("PositionMap"):
    x, y = map(int, value.split("|"))
    position_map[name.lower()] = (x, y)  # Convert keys to lowercase for consistency (just incase shouldn't be needed)

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
    print(position_map)
    dcbls = space_out_positions(position_map["disconnectedbackgroundleftside"], 5)[-1]
    dcbrs = space_out_positions(position_map["disconnectedbackgroundrightside"], 5)[-1]
    rcb = space_out_positions(position_map["reconnectbutton"], 10)[-1]

    left_side_pixel = pyautogui.pixelMatchesColor(dcbls[0][0], dcbls[0][1], (0x39, 0x3B, 0x3D), tolerance=2) and \
                      pyautogui.pixelMatchesColor(dcbls[1][0], dcbls[1][1], (0x39, 0x3B, 0x3D), tolerance=2)
    right_side_pixel = pyautogui.pixelMatchesColor(dcbrs[0][0], dcbrs[0][1], (0x39, 0x3B, 0x3D), tolerance=2) and \
                       pyautogui.pixelMatchesColor(dcbrs[1][0], dcbrs[1][1], (0x39, 0x3B, 0x3D), tolerance=2)
    reconnect_button_pixel = pyautogui.pixelMatchesColor(rcb[0][0] , rcb[0][1], (0xFF, 0xFF, 0xFF), tolerance=0) and \
                             pyautogui.pixelMatchesColor(rcb[1][0], rcb[1][1], (0xFF, 0xFF, 0xFF), tolerance=0)

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
            print("Yikes")
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
    while True:
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

if __name__ == "__main__":
    main()
