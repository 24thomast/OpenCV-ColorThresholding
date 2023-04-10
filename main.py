import cv2
import numpy as np
import csv
from datetime import datetime

def nothing(x):
    pass

area_max = 10000

csv_empty = False

low_default = [0, 0, 0]
high_default = [180, 255, 255]
area_threshold_default = 2000

with open("colors.csv", 'r') as file:
    reader = csv.reader(file)
    read_data = list(reader)
    if len(read_data) == 0:
        csv_empty = True
    else:
        low_default = [read_data[-1][2], read_data[-1][3], read_data[-1][4]]
        high_default = [read_data[-1][5], read_data[-1][6], read_data[-1][7]]
        area_threshold_default = read_data[-1][8]

if csv_empty:
    now = datetime.now()
    date = now.strftime("%m/%d/%Y")
    time = now.strftime("%H:%M:%S")
    with open('colors.csv', 'w', newline='') as file:
        header = ["Date", "Time", "H Min", "S Min", "V Min", "H Max", "S Max", "V Max", "Area"]
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
    with open('colors.csv', 'a', newline='') as file:
        data = [date, time, low_default[0], low_default[1], low_default[2], high_default[0], high_default[1], high_default[2], area_threshold_default]
        writer = csv.writer(file)
        writer.writerow(data)
        
if int(area_threshold_default) > area_max:
    area_max = int(area_threshold_default)

capture = cv2.VideoCapture(0)

cv2.namedWindow('Frame', cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow("Frame", 320, 240)

cv2.namedWindow('Control', cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow('Control', 400, 375)

cv2.createTrackbar('H Min', 'Control', int(low_default[0]), 180, nothing)
cv2.createTrackbar('H Max', 'Control', int(high_default[0]), 180, nothing)
cv2.createTrackbar('S Min', 'Control', int(low_default[1]), 255, nothing)
cv2.createTrackbar('S Max', 'Control', int(high_default[1]), 255, nothing)
cv2.createTrackbar('V Min', 'Control', int(low_default[2]), 255, nothing)
cv2.createTrackbar('V Max', 'Control', int(high_default[2]), 255, nothing)
cv2.createTrackbar('Area', 'Control', int(area_threshold_default), area_max, nothing)
cv2.createTrackbar('Area On', 'Control', 0, 1, nothing)
cv2.createTrackbar('Auto Save', 'Control', 0, 1, nothing)

while (1):
    ret, rgb_frame = capture.read()
    hsv_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2HSV)

    h_max = cv2.getTrackbarPos('H Max', 'Control')
    h_min = cv2.getTrackbarPos('H Min', 'Control')
    s_max = cv2.getTrackbarPos('S Max', 'Control')
    s_min = cv2.getTrackbarPos('S Min', 'Control')
    v_max = cv2.getTrackbarPos('V Max', 'Control')
    v_min = cv2.getTrackbarPos('V Min', 'Control')
    area_threshold = cv2.getTrackbarPos('Area', 'Control')
    area_enable = cv2.getTrackbarPos('Area On', 'Control')
    save = cv2.getTrackbarPos('Auto Save', 'Control')

    lower_threshold = np.array([h_min, s_min, v_min], dtype='uint8')
    upper_threshold = np.array([h_max, s_max, v_max], dtype='uint8')

    threshold = cv2.inRange(hsv_frame, lower_threshold, upper_threshold)
    (contours, _) = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if area_enable == 1:
        large_contours = []
        output = np.zeros(rgb_frame.shape, np.uint8)
        for contour in contours:
            contour_area = cv2.contourArea(contour)
            if contour_area > area_threshold:
                large_contours.append(contour)
        cv2.drawContours(output, tuple(large_contours), -1, cv2.mean(rgb_frame, mask=threshold), -1)
    else:
        output = cv2.bitwise_and(rgb_frame, rgb_frame, mask=threshold)

    cv2.imshow('Frame', output)

    key = cv2.waitKey(1) & 0xff
    
    if key == ord('q'): # Quit Program
        if save == 1:
            now = datetime.now()
            date = now.strftime("%m/%d/%Y")
            time = now.strftime("%H:%M:%S")
            data = [date, time, h_min, s_min, v_min, h_max, s_max, v_max, area_threshold]
            with open('colors.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(data)
        print([h_min, s_min, v_min])
        print([h_max, s_max, v_max])
        print(area_threshold)
        break
        
    elif key == ord('r'): # Reset to Original Threshold 
        cv2.setTrackbarPos('H Min', 'Control', 0)
        cv2.setTrackbarPos('H Max', 'Control', 180)
        cv2.setTrackbarPos('S Min', 'Control', 0)
        cv2.setTrackbarPos('S Max', 'Control', 255)
        cv2.setTrackbarPos('V Min', 'Control', 0)
        cv2.setTrackbarPos('V Max', 'Control', 255)
        cv2.setTrackbarPos('Area', 'Control', 2000)
        cv2.setTrackbarPos('Area On', 'Control', 0)
        cv2.setTrackbarPos('Auto Save', 'Control', 0)
        
    elif key == ord('t'): # Reset to Saved Threshold
        cv2.setTrackbarPos('H Min', 'Control', int(low_default[0]))
        cv2.setTrackbarPos('H Max', 'Control', int(high_default[0]))
        cv2.setTrackbarPos('S Min', 'Control', int(low_default[1]))
        cv2.setTrackbarPos('S Max', 'Control', int(high_default[1]))
        cv2.setTrackbarPos('V Min', 'Control', int(low_default[2]))
        cv2.setTrackbarPos('V Max', 'Control', int(high_default[2]))
        cv2.setTrackbarPos('Area', 'Control', area_threshold_default)
        cv2.setTrackbarPos('Area On', 'Control', 0)
        cv2.setTrackbarPos('Auto Save', 'Control', 0)
        
    elif key == ord('s'): # Save Threshold
        low_default = [h_min, s_min, v_min]
        high_default = [h_max, s_max, v_max]
        area_threshold_default = read_data[-1][8]
        now = datetime.now()
        date = now.strftime("%m/%d/%Y")
        time = now.strftime("%H:%M:%S")
        data = [date, time, h_min, s_min, v_min, h_max, s_max, v_max, area_threshold]
        with open('colors.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            
    elif key == ord('p'): # Print Threshold
        print([h_min, s_min, v_min])
        print([h_max, s_max, v_max])
        print(area_threshold)

cv2.destroyAllWindows()
