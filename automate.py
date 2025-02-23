import cv2
from datetime import datetime
import os

def winner_certificate(name,dept,event_name,regno,position):
    template = cv2.imread("winners_certificate.png")
    # Name
    text = name
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 2
    thickness = 5
    color = (66, 154, 203)
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    template_width = template.shape[1]
    x = (template_width - text_width) // 2
    y = 843
    cv2.putText(template, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
    # Department
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1.3
    thickness = 2
    color = (66, 154, 203)
    (text_width, text_height), baseline = cv2.getTextSize(dept, font, font_scale, thickness)
    x = (template_width - text_width) // 2
    y = 933
    cv2.putText(template, dept, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
    # Position
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1.3
    thickness = 2
    color = (66, 154, 203)
    (text_width, text_height), baseline = cv2.getTextSize(position, font, font_scale, thickness)
    x = (template_width - text_width) // 2
    y = 1010
    cv2.putText(template, position, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
    # Event
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 0.8
    thickness = 2
    color = (66, 154, 203)
    cv2.putText(template, event_name, (832,1070), font, font_scale, color, thickness, cv2.LINE_AA)
    # Date
    current_date = datetime.now().strftime("%d-%m-%Y")
    font_scale = 0.8
    thickness = 2
    cv2.putText(template, current_date, (1169, 1074), font, font_scale, color, thickness, cv2.LINE_AA)
    cv2.imwrite(f"{event_name}_winner_{regno}.png",template)

winner_certificate("John Doe", "Computer Science", "Coding Challenge", "12345", "1st")

print("Certificate generated successfully")