from flask import Blueprint,flash, jsonify, make_response,render_template, send_file,url_for,session,redirect,request
from werkzeug.security import generate_password_hash,check_password_hash
from ..extensions import mongo
import cv2
from datetime import datetime
import os

events = Blueprint("events",__name__,url_prefix="/events")


def generate_certificate(name,dept,event_name,regno):
    template = cv2.imread("./static/participation_certificate.png")
    # Name
    text = name
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1.95
    thickness = 5
    color = (66, 154, 203)
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    template_width = template.shape[1]
    x = (template_width - text_width) // 2
    y = 840
    cv2.putText(template, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
    # Department
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 1.3
    thickness = 2
    color = (66, 154, 203)
    (text_width, text_height), baseline = cv2.getTextSize(dept, font, font_scale, thickness)
    x = (template_width - text_width) // 2
    y = 950
    cv2.putText(template, dept, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
    # Event
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 0.8
    thickness = 2
    color = (66, 154, 203)
    cv2.putText(template, event_name, (968,1025), font, font_scale, color, thickness, cv2.LINE_AA)
    # Date
    current_date = datetime.now().strftime("%d-%m-%Y")
    font_scale = 0.8
    thickness = 2
    cv2.putText(template, current_date, (1304, 1023), font, font_scale, color, thickness, cv2.LINE_AA)
    cv2.imwrite(f"./static/certificates/{regno}.png", template)


@events.route("/",methods=["GET","POST"])
def events_home():
    if request.method == "POST":
        name,dept,regno = request.form["name"],request.form["dept"],request.form["regno"]
        event_name = request.form.get("event")
        print(event_name)
        if not mongo.db.event_info.find_one({"event_name":event_name}):
            flash("Event does not exist")
        else:
            generate_certificate(name,dept,event_name,regno)
            return redirect(url_for("events.get_certificate",regno=regno))
    return render_template("events/index.html")

@events.route("/get_certificate/<regno>")
def get_certificate(regno):
    path = os.path.join(os.path.abspath("Quiz-App/event_certificates/"),f"{regno}.png")
    return send_file(path,as_attachment=True)