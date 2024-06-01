import pyautogui

# Coordinates for left side, right side, and reconnect button
left_coords = (1379, 538)
right_coords = (1761, 538)
reconnect_button_coords = (1661, 602)

# Capture colors at these coordinates
left_color1 = pyautogui.pixel(left_coords[0] - 5, left_coords[1] - 5)
left_color2 = pyautogui.pixel(left_coords[0] + 5, left_coords[1] + 5)
right_color1 = pyautogui.pixel(right_coords[0] - 5, right_coords[1] - 5)
right_color2 = pyautogui.pixel(right_coords[0] + 5, right_coords[1] + 5)
reconnect_color1 = pyautogui.pixel(reconnect_button_coords[0] - 10, reconnect_button_coords[1] - 10)
reconnect_color2 = pyautogui.pixel(reconnect_button_coords[0] + 10, reconnect_button_coords[1] + 10)

print("Left side colors:", left_color1, left_color2)
print("Right side colors:", right_color1, right_color2)
print("Reconnect button colors:", reconnect_color1, reconnect_color2)
