import cv2
from datetime import datetime

template = cv2.imread("Literary Club Certificate .png")

text = "Vishvaa K"
font = cv2.FONT_HERSHEY_COMPLEX
font_scale = 1.95
thickness = 5
color = (66, 154, 203)
(text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
template_width = template.shape[1]
x = (template_width - text_width) // 2
y = 840
cv2.putText(template, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)

dept = "II-CSE-B"
font = cv2.FONT_HERSHEY_COMPLEX
font_scale = 1.3
thickness = 2
color = (66, 154, 203)
(text_width, text_height), baseline = cv2.getTextSize(dept, font, font_scale, thickness)
x = (template_width - text_width) // 2
y = 950
cv2.putText(template, dept, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)

event = "Literary Club Event"
font = cv2.FONT_HERSHEY_COMPLEX
font_scale = 0.8
thickness = 2
color = (66, 154, 203)

cv2.putText(template, event, (968,1025), font, font_scale, color, thickness, cv2.LINE_AA)

current_date = datetime.now().strftime("%d-%m-%Y")
font_scale = 0.8
thickness = 2

cv2.putText(template, current_date, (1304, 1023), font, font_scale, color, thickness, cv2.LINE_AA)

cv2.imwrite("output.png", template)
print("Certificate generated successfully")