import os
from collections import defaultdict
import re
import pdfkit
from flask import Blueprint,flash, jsonify, make_response,render_template, send_file,url_for,session,redirect,request
from werkzeug.security import generate_password_hash,check_password_hash
from weasyprint import CSS, HTML

from ..extensions import mongo
from ..helper import generate_token,verify_token,extract_questions,remove_duplicates,clean_reports
from ..send_email import send_email_admin
from bson.objectid import ObjectId
import string , random

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,FileField,IntegerField,SelectField
from wtforms.validators import DataRequired,InputRequired
from werkzeug.utils import secure_filename

import cv2
from datetime import datetime
from ..send_email import send_winner_email

admin = Blueprint("admin",__name__,url_prefix="/admin")

gen_testCode = ''.join(random.sample(string.ascii_uppercase+string.digits,k=8))

class AddAudioForm(FlaskForm):
    test_code = StringField(u"Test code",validators=[DataRequired(),InputRequired()])
    time = IntegerField(u"Time (in minutes)",validators=[DataRequired(),InputRequired()],render_kw={"step":"10"})
    lab_session = IntegerField(u"Lab Session",validators=[DataRequired(),InputRequired()])
    test_type = SelectField(u"Test Type",choices=[("lab test","Lab test"),("cie1","CIE1"),("cie2","CIE2"),("model exam","Model Exam"),("univ exam","University Exam"),("value added","Value added course")])
    audio_no = IntegerField(u"Audio number",validators=[DataRequired(),InputRequired()])
    audio_file = FileField(u"Audio File",validators=[InputRequired()])
    questions_file = FileField(u"Questions File",validators=[InputRequired()])
    submit = SubmitField("Submit")

class EditAudioForm(FlaskForm):
    test_code = StringField("Test code",validators=[DataRequired(),InputRequired()])
    new_audio_file = FileField("New Audio File",validators=[InputRequired()])
    update = SubmitField("Update")

class EditQuestionForm(FlaskForm):
    test_code = StringField("Test code",validators=[DataRequired(),InputRequired()])
    new_questions_file = FileField("New Questions File",validators=[InputRequired()])
    update = SubmitField("Update")

def check_login():
    try:
        if session["adminUsername"] is not None:
            return True
    except:
        return False

@admin.route("/",methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        session.permanent=True
        username,passwd = request.form["adminName"],request.form["adminPass"]
        if mongo.db.admin.find_one({"username":username}):
            storedPasswd = mongo.db.admin.find_one({"username":username})["passwd"]
            if check_password_hash(storedPasswd,passwd):
                session["adminUsername"] = username
                return redirect(url_for('admin.dashboard'))
            flash("Username or password incorrect")
        else:
            flash("Username or password doesn't exist!")
    return render_template("admin/index.html")

@admin.route("/signup",methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username,email,passwd,repasswd = request.form["adminName"],request.form['adminEmail'],request.form['adminPass'],request.form['adminRePass']
        user = mongo.db.users
        if not user.find_one({'username':username}) and not user.find_one({'email':email}):
            if not mongo.db.admin.find_one({"username":username}):
                if passwd == repasswd:
                    hased_value = generate_password_hash(passwd,method='scrypt')
                    try:
                        addAdmin = {"username":username,
                        "email":email,
                        "passwd":hased_value}
                        mongo.db.admin.insert_one(addAdmin)
                        flash("Registered successfully!")
                        return redirect(url_for('admin.login'))
                    except Exception as e:
                        flash(e)
                else:
                    flash("Password doesn't match!")
            else:
                flash("User is already exists")
        else:
            flash("You are a student, you can't be a admin!")
    return render_template("admin/signup.html")

@admin.route("/update_password",methods=['GET', 'POST'])
def change_passwd():
    if request.method == "POST":
        email,passwd,new_passwd = request.form['adminEmail'],request.form['adminPass'],request.form['adminNewPasswd']
        if mongo.db.admin.find_one({"email":email}):
            storedPasswd = mongo.db.admin.find_one({"email":email})["passwd"]
            if check_password_hash(storedPasswd,passwd):
                new_hashed_value = generate_password_hash(new_passwd,method="scrypt")
                try:
                    mongo.db.admin.update_one({"email":email},{"$set":{"passwd":new_hashed_value}})
                    flash("Password changed!")
                    session.pop("adminUsername")
                    return redirect(url_for("admin.login"))
                except:
                    flash(Exception)
                    flash("Error while updating the password")
            else:
                flash("Password doesn't match")
        else:
            flash("User not found")
    return render_template("admin/change_passwd.html")

@admin.route("/dashboard",methods=['GET', 'POST'])
def dashboard():
    if check_login():
        return render_template("admin/dashboard.html",name=session['adminUsername'])
    else:
        return redirect(url_for("admin.login"))


@admin.route('/reset_request',methods=['GET', 'POST'])
def reset_request():
    if request.method == "POST":
        email = request.form['resetEmail']
        user = mongo.db.admin.find_one({"email":email})
        forgot_users = mongo.db.forgot_users
        if user:
            token = generate_token(userId=str(user['_id']))
            send_email_admin(userEmail=email,token=token,username=user['username'])
            flash("A link has been send to your email for password reset! click that to reset your password")
            if not forgot_users.find_one({"token":token}):
                forgot_users.insert_one({"token":token,"userId":user['_id']})
    return render_template('admin/resetEmail.html')

@admin.route("/verify_admin_reset/<token>",methods=['GET', 'POST'])
def reset_admin_password_verify(token):
    userId = mongo.db.forgot_users.find_one({'token':token})['userId']
    if userId is not None:
        try:
            if verify_token(token=token,userId=userId):
                return redirect(url_for("admin.reset_password",userId=userId))
        except:
            return "<center><h1>Invalid or expired token</h1></center>"
    else:
        return "<center><h1>Invalid or expired token</h1></center>"

@admin.route("/password_reset/<userId>",methods=['GET', 'POST'])
def reset_password(userId):
    if request.method == "POST":
            passwd,repasswd = request.form['newPass'],request.form['newRePass']
            if passwd == repasswd:
                new_hashed_value = generate_password_hash(passwd,method='scrypt')
                try:
                    mongo.db.admin.update_one({'_id':ObjectId(userId)},{"$set":{"passwd":new_hashed_value}})
                    flash("Password Changed!")
                    mongo.db.forgot_users.delete_many({'userId':ObjectId(userId)})
                    return redirect(url_for("admin.login"))
                except Exception as e:
                    flash(e)
            else:
                flash("Password does not match!")
    return render_template("admin/resetPassword.html",userId=userId)

@admin.route("/get_testCode",methods=['GET', 'POST'])
def get_test_code():
    if check_login():
        testCode = gen_testCode
        form = AddAudioForm()
        if request.method == "POST":
            if form.validate_on_submit():
                test_code = str(form.test_code.data)
                test_time = str(form.time.data)
                lab_session = str(form.lab_session.data)
                audio_no = str(form.audio_no.data)
                test_type = dict(form.test_type.choices).get(form.test_type.data)
                # Saving the audio
                audio_file = request.files['audio_file']
                audio_filename = secure_filename(audio_file.filename)
                audio_file.save(os.path.join(os.path.abspath('Quiz-App/src/static/audios/'),audio_filename))
                # Saving the excel file
                questions_file = request.files['questions_file']
                questions_filename = secure_filename(questions_file.filename)
                questions_file.save(os.path.join(os.path.abspath('Quiz-App/src/static/questions/'),questions_filename))

                try:
                    if not mongo.db.testDetails.find_one({"test_code":test_code}):
                        mongo.db.testDetails.insert_one({
                    "test_code":test_code,
                    "audio_name":audio_filename,
                    "test_time": test_time,
                    "test_type":test_type,
                    "lab_session":lab_session,
                    "audio_no":audio_no,
                    "questions_filename":questions_filename,
                    "available":True
                    })

                    questions = extract_questions(os.path.join(os.path.abspath('Quiz-App/src/static/questions/'),questions_filename))
                    mongo.db[test_code].insert_many(questions)
                    flash("Uploaded Successfully!")
                except Exception as e:
                    flash(e)
        return render_template("admin/addQDb.html",testCode = testCode ,form=form)
    else:
        return redirect(url_for("admin.login"))


@admin.route("/download/<testCode>/<Class>")
def download(testCode,Class):
    path = os.path.join(os.path.abspath("Quiz-App/admin_reports/"),f"{Class}_{testCode}_(test-report).csv")
    return send_file(path,as_attachment=True)

@admin.route("/logout",methods=['GET', 'POST'])
def logout():
    session.pop('adminUsername')
    return redirect(url_for("admin.login"))

def create_report(test_codes,report_codes,results,dept,exam_date,exam_name,exam_session,exam_subject):
    import base64
    with open("src/static/VEC-logo.png", "rb") as img_file:
        base64_encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

    pdf_report_template = render_template("admin/report_t.html",test_codes=test_codes, report_codes = report_codes , results = results ,dept=dept,base64_encoded_image=base64_encoded_image,exam_date=exam_date,exam_name=exam_name,exam_session=exam_session,exam_subject=exam_subject)

    pdf = HTML(string=pdf_report_template)
    filename = f"University_report_{dept}.pdf"

    pdf.write_pdf(os.path.join(os.path.abspath("Quiz-App/admin_reports/",filename)))


@admin.route("/download_univ_reports",methods=['GET', 'POST'])
def download_univ_report():
    if check_login():
        univ_tests = list(mongo.db.testDetails.find({"test_type":"University Exam"}))
        univ_testcodes = [i["test_code"] for i in univ_tests]
        if request.method == "POST":
            try:
                user_test_codes = [request.form.get("first_code"),request.form.get("second_code"),request.form.get("third_code"),request.form.get("fourth_code")]
                test_codes = [f'{request.form.get("first_code")}-result',f'{request.form.get("second_code")}-result',f'{request.form.get("third_code")}-result',f'{request.form.get("fourth_code")}-result']
                dept = request.form.get("department")

                exam_name = request.form.get("exam_name")
                exam_date = request.form.get("exam_date")
                exam_session = request.form.get("exam_session")
                exam_subject = request.form.get("exam_subject")

                regex = re.compile("I-CSE(CS)-A") if dept == "CSE(CS)" else re.compile(f'^[A-Z]-{dept}-[A-Z]$')
                cleaned_reports_sorted = clean_reports(test_codes,dept,regex)
                
                import base64
                with open("Quiz-App/src/static/VEC-logo.png", "rb") as img_file:
                    base64_encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

                pdf_report_template = render_template("admin/report_t.html", title="University Report", test_codes=univ_testcodes, report_codes=user_test_codes, results=cleaned_reports_sorted, dept=dept, base64_encoded_image=base64_encoded_image, exam_date=exam_date, exam_name=exam_name, exam_session=exam_session, exam_subject=exam_subject)

                # Convert HTML to PDF
                pdf = pdfkit.from_string(pdf_report_template, False)

                # Send PDF as response
                filename = f"University_report_{dept}.pdf"
                response = make_response(pdf)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=univ_report.pdf'
                return response

            except Exception as e:
                flash(e)
                return redirect(url_for("admin.show_univ_report"))

        return render_template("admin/download_report.html",test_codes=univ_testcodes)
    else:
        return redirect(url_for("admin.login"))


@admin.route("/download_model_reports",methods=['GET', 'POST'])
def download_model_report():
    if check_login():
        model_tests = list(mongo.db.testDetails.find({"test_type":"Model Exam"}))
        model_testcodes = [i["test_code"] for i in model_tests]
        if request.method == "POST":
            try:
                user_test_codes = [request.form.get("first_code"),request.form.get("second_code"),request.form.get("third_code"),request.form.get("fourth_code")]
                test_codes = [f'{request.form.get("first_code")}-result',f'{request.form.get("second_code")}-result',f'{request.form.get("third_code")}-result',f'{request.form.get("fourth_code")}-result']
                dept = request.form.get("department")

                exam_name = request.form.get("exam_name")
                exam_date = request.form.get("exam_date")
                exam_session = request.form.get("exam_session")
                exam_subject = request.form.get("exam_subject")
                
                regex = re.compile("I-CSE(CS)-A") if dept == "CSE(CS)" else re.compile(f'^[A-Z]-{dept}-[A-Z]$')
                cleaned_reports_sorted = clean_reports(test_codes,dept,regex)

                import base64
                with open("Quiz-App/src/static/VEC-logo.png", "rb") as img_file:
                    base64_encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

                pdf_report_template = render_template("admin/report_t.html", title="Model Report", test_codes=model_testcodes, report_codes=user_test_codes, results=cleaned_reports_sorted, dept=dept, base64_encoded_image=base64_encoded_image, exam_date=exam_date, exam_name=exam_name, exam_session=exam_session, exam_subject=exam_subject)

                # Convert HTML to PDF
                pdf = pdfkit.from_string(pdf_report_template, False)

                # Send PDF as response
                filename = f"Model_report_{dept}.pdf"
                response = make_response(pdf)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=model_report.pdf'
                return response

            except Exception as e:
                flash(e)
                return redirect(url_for("admin.show_model_report"))

        return render_template("admin/download_report.html",test_codes=model_testcodes)
    else:
        return redirect(url_for("admin.login"))

@admin.route("/download_lab_reports",methods=['GET', 'POST'])
def download_lab_report():
    if check_login():
        lab_tests = list(mongo.db.testDetails.find({"test_type":"Lab Test"}))
        lab_testcodes = [i["test_code"] for i in lab_tests]
        if request.method == "POST":
            try:
                user_test_codes = [request.form.get("first_code"),request.form.get("second_code"),request.form.get("third_code"),request.form.get("fourth_code")]
                test_codes = [f'{request.form.get("first_code")}-result',f'{request.form.get("second_code")}-result',f'{request.form.get("third_code")}-result',f'{request.form.get("fourth_code")}-result']
                dept = request.form.get("department")

                exam_name = request.form.get("exam_name")
                exam_date = request.form.get("exam_date")
                exam_session = request.form.get("exam_session")
                exam_subject = request.form.get("exam_subject")
                
                regex = re.compile("I-CSE(CS)-A") if dept == "CSE(CS)" else re.compile(f'^[A-Z]-{dept}-[A-Z]$')
                cleaned_reports_sorted = clean_reports(test_codes,dept,regex)

                import base64
                with open("Quiz-App/src/static/VEC-logo.png", "rb") as img_file:
                    base64_encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

                pdf_report_template = render_template("admin/report_t.html", title="Lab Report", test_codes=lab_testcodes, report_codes=user_test_codes, results=cleaned_reports_sorted, dept=dept, base64_encoded_image=base64_encoded_image, exam_date=exam_date, exam_name=exam_name, exam_session=exam_session, exam_subject=exam_subject)

                # Convert HTML to PDF
                pdf = pdfkit.from_string(pdf_report_template, False)

                # Send PDF as response
                filename = f"lab_report_{dept}.pdf"
                response = make_response(pdf)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=lab_report.pdf'
                return response

            except Exception as e:
                flash(e)
                return redirect(url_for("admin.show_lab_report"))

        return render_template("admin/download_report.html",test_codes=lab_testcodes)
    else:
        return redirect(url_for("admin.login"))

@admin.route("/show_univ_reports",methods=['GET', 'POST'])
def show_univ_report():
    if check_login():
        univ_tests = list(mongo.db.testDetails.find({"test_type":"University Exam"}))
        univ_testcodes = [i["test_code"] for i in univ_tests]
        if request.method == "POST":
            try:
                user_test_codes = [request.form.get("first_code"),request.form.get("second_code"),request.form.get("third_code"),request.form.get("fourth_code")]
                test_codes = [f'{request.form.get("first_code")}-result',f'{request.form.get("second_code")}-result',f'{request.form.get("third_code")}-result',f'{request.form.get("fourth_code")}-result']
                dept = request.form.get("department")
                
                regex = re.compile("I-CSE(CS)-A") if dept == "CSE(CS)" else re.compile(f'^[A-Z]-{dept}-[A-Z]$')
                
                cleaned_reports_sorted = clean_reports(test_codes,dept,regex)

                return render_template("admin/show_univ_reports.html",test_codes=univ_testcodes, report_codes = user_test_codes , results = cleaned_reports_sorted ,dept=dept)
            except Exception as e:
                flash(e)
                return redirect(url_for("admin.show_univ_report"))

        return render_template("admin/show_univ_reports.html",test_codes=univ_testcodes)
    else:
        return redirect(url_for("admin.login"))

@admin.route("/show_model_reports",methods=['GET', 'POST'])
def show_model_report():
    if check_login():
        model_tests = list(mongo.db.testDetails.find({"test_type":"Model Exam"}))
        model_testcodes = [i["test_code"] for i in model_tests]
        if request.method == "POST":
            try:
                user_test_codes = [request.form.get("first_code"),request.form.get("second_code"),request.form.get("third_code"),request.form.get("fourth_code")]
                test_codes = [f'{request.form.get("first_code")}-result',f'{request.form.get("second_code")}-result',f'{request.form.get("third_code")}-result',f'{request.form.get("fourth_code")}-result']
                dept = request.form.get("department")
                regex = re.compile("I-CSE(CS)-A") if dept == "CSE(CS)" else re.compile(f'^[A-Z]-{dept}-[A-Z]$')
            except:
                flash("Please select testcodes and department!")
            cleaned_reports_sorted = clean_reports(test_codes,dept,regex)
            return render_template("admin/show_model_reports.html",test_codes=model_testcodes, report_codes = user_test_codes , results = cleaned_reports_sorted ,dept=dept)
        return render_template("admin/show_model_reports.html",test_codes=model_testcodes)
    else:
        return redirect(url_for("admin.login"))

@admin.route("/show_lab_reports",methods=['GET', 'POST'])
def show_lab_report():
    if check_login():
        lab_tests = list(mongo.db.testDetails.find({"test_type":"Lab Test"}))
        lab_testcodes = [i["test_code"] for i in lab_tests]
        if request.method == "POST":
            try:
                user_test_codes = [request.form.get("first_code"),request.form.get("second_code"),request.form.get("third_code"),request.form.get("fourth_code")]
                test_codes = [f'{request.form.get("first_code")}-result',f'{request.form.get("second_code")}-result',f'{request.form.get("third_code")}-result',f'{request.form.get("fourth_code")}-result']
                dept = request.form.get("department")
                regex = re.compile("I-CSE(CS)-A") if dept == "CSE(CS)" else re.compile(f'^[A-Z]-{dept}-[A-Z]$')
            except:
                flash("Please select testcodes and department!")
            cleaned_reports_sorted = clean_reports(test_codes,dept,regex)
            return render_template("admin/show_lab_reports.html",test_codes=lab_testcodes, report_codes = user_test_codes , results = cleaned_reports_sorted ,dept=dept)
        return render_template("admin/show_lab_reports.html",test_codes=lab_testcodes)
    else:
        return redirect(url_for("admin.login"))

@admin.route("/test_details/<testCode>",methods=['GET', 'POST'])
def fetch_test_details(testCode):
    if check_login():
        audio_form = EditAudioForm()
        question_form = EditQuestionForm()
        fetch_testcodes = list(mongo.db.testDetails.find({},{'_id':0,"test_time":0}))
        raw_available_testcodes=[i["test_code"] for i in fetch_testcodes]
        available_testcodes = remove_duplicates(raw_available_testcodes)
        if testCode in available_testcodes:
            test_details = list(mongo.db.testDetails.find({"test_code":testCode},{'_id':0,"test_time":0}))
            fetch_test_questions = list(mongo.db[testCode].find({},{"_id":0,"correct_ans":0}))
            return render_template("admin/show_questions.html",audio_form=audio_form,question_form=question_form,test_codes=available_testcodes,test_details=test_details,questions=fetch_test_questions)
        return jsonify({"resp":"TESTCODE NOT FOUND"})
    else:
        return redirect(url_for('admin.login'))

@admin.route("/show_questions",methods=['GET', 'POST'])
def show_questions():
    if check_login():
        audio_form = EditAudioForm()
        question_form = EditQuestionForm()
        fetch_testcodes = list(mongo.db.testDetails.find({},{'_id':0,"test_time":0}))
        raw_test_codes=[i["test_code"] for i in fetch_testcodes]
        test_codes = remove_duplicates(raw_test_codes)
        fetch_first_test = list(mongo.db.testDetails.find({"test_code":test_codes[0]},{'_id':0,"test_time":0}))
        fetch_test_questions = list(mongo.db[fetch_first_test[0]["test_code"]].find({},{"_id":0,"correct_ans":0}))
        return render_template("admin/show_questions.html",question_form=question_form,test_codes=test_codes,test_details=fetch_first_test,questions=fetch_test_questions,audio_form=audio_form)
    else:
        return redirect(url_for('admin.login'))

@admin.route("/edit_audio_file",methods=['GET', 'POST'])
def edit_test_audio():
    if check_login():
        if request.method == "POST":
            test_code = request.form["test_code"]
            audio_file = request.files['new_audio_file']
            audio_filename = secure_filename(audio_file.filename)
            audio_file.save(os.path.join(os.path.abspath('Quiz-App/src/static/audios/'),audio_filename))
            try:
                mongo.db.testDetails.update_one({"test_code":test_code},{"$set":{"audio_name": audio_filename}})
                flash("Audio updated successfully!")
                return redirect(url_for("admin.show_questions"))
            except Exception as e:
                flash(e)
        return redirect(url_for("admin.show_questions"))
    else:
        return redirect(url_for("admin.login"))

@admin.route("/edit_question_file",methods=['GET', 'POST'])
def edit_test_file():
    if check_login():
        if request.method == "POST":
            test_code = request.form["test_code"]
            new_question_file = request.files['new_questions_file']
            new_question_filename = secure_filename(new_question_file.filename)
            new_question_file.save(os.path.join(os.path.abspath('Quiz-App/src/static/questions/'),new_question_filename))
            try:
                # Dropping the testcode collection
                mongo.db[test_code].drop()
                # Extracting new questions
                questions = extract_questions(os.path.join(os.path.abspath('Quiz-App/src/static/questions/'),new_question_filename))
                mongo.db[test_code].insert_many(questions)
                # Updating testdetails in testDetails collection
                mongo.db.testDetails.update_one({"test_code":test_code},{"$set":{"questions_filename": new_question_filename}})
                flash("Questions updated successfully")

                return redirect(url_for("admin.show_questions"))
            except Exception as e:
                flash(e)
        return redirect(url_for("admin.show_questions"))
    else:
        return redirect(url_for("admin.login"))

@admin.route("/delete_testcode",methods=['GET', 'POST'])
def delete_testcode():
    if check_login():
        if request.method == "POST":
            test_code = request.form["test_code"]
            try:
                mongo.db[test_code].drop()
                mongo.db[f"{test_code}-result"].drop()
                mongo.db.testDetails.delete_one({"test_code":test_code})
                flash("Deleted successfully")
            except Exception as e:
                flash(e)
        return redirect(url_for("admin.show_questions"))
    else:
        return redirect(url_for("admin.login"))

@admin.route("/issues/<testCode>",methods=['GET', 'POST'])
def fetch_technical_issues(testCode):
    if check_login():
        fetch_testcodes = list(mongo.db.testDetails.find({},{"test_code":1}))
        raw_available_testcodes=[i["test_code"] for i in fetch_testcodes]
        available_testcodes = remove_duplicates(raw_available_testcodes)
        if testCode in available_testcodes:
            zero_results = list(mongo.db[f"{testCode}-result"].find({"score":0}))
            return render_template("admin/technical_issues.html",test_codes=available_testcodes,zero_results=zero_results)
        return jsonify({"resp":"TESTCODE NOT FOUND"})
    else:
        return redirect(url_for('admin.login'))

@admin.route("/technical_issues",methods=['GET', 'POST'])
def technical_issues():
    if check_login():
        fetch_testcodes = list(mongo.db.testDetails.find({},{"test_code":1}))
        raw_test_codes=[i["test_code"] for i in fetch_testcodes]
        test_codes = remove_duplicates(raw_test_codes)
        zero_results = list(mongo.db[f"{test_codes[0]}-result"].find({"score":0},{}))
        return render_template("admin/technical_issues.html",test_codes=test_codes,zero_results=zero_results)
    else:
        return redirect(url_for("admin.login"))


@admin.route("/delete_result",methods=['GET', 'POST'])
def delete_result():
    if check_login():
        if request.method == "POST":
            obj_id = request.json["obj_id"]
            test_code = request.json["test_code"]
            try:
                mongo.db[f"{test_code}-result"].delete_one({"_id":ObjectId(obj_id)})
                flash("Deleted successfully!")
                return jsonify({"url":f"/admin/issues/{test_code}"})
            except Exception as e:
                flash(e)
        return redirect(url_for("admin.technical_issues"))
    else:
        return redirect(url_for("admin.login"))
    
@admin.route("/change_course_name",methods=['GET', 'POST'])
def change_course_name():
    if check_login():
        current_course= list(mongo.db.courseDetails.find({}))[0]["course_name"]
        if request.method == "POST":
            course_name = request.form.get("course_name")
            mongo.db.courseDetails.update_one({},{"$set":{"course_name":course_name}})
        return render_template("admin/course_name.html",current_course=current_course)
    else:
        return redirect(url_for("admin.login"))
    
def winner_certificate(name,dept,event_name,regno,position,event_date):
    template_path = os.path.join(os.path.abspath("Quiz-App/src/static/"), "winners_certificate.png")
    template = cv2.imread(template_path)
    if template is None:
        raise FileNotFoundError(f"Template image not found at path: {template_path}")
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
    font_scale = 0.93
    thickness = 3
    color = (66, 154, 203)
    cv2.putText(template, position, (966,1010), font, font_scale, color, thickness, cv2.LINE_AA)
    # Event
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = 0.8
    thickness = 2
    color = (66, 154, 203)
    cv2.putText(template, event_name, (832,1070), font, font_scale, color, thickness, cv2.LINE_AA)
    # Date
    font_scale = 0.8
    thickness = 2
    date = event_date.strftime("%d-%m-%Y") if hasattr(event_date, "strftime") else str(event_date)
    cv2.putText(template, date, (1169, 1074), font, font_scale, color, thickness, cv2.LINE_AA)
    cv2.imwrite(os.path.join(os.path.abspath("Quiz-App/event_certificates/"),f"{event_name}_winner_{regno}.png"),template)

@admin.route("/generate_winner_certificate",methods=['GET', 'POST'])
def generate_winner_certificate():
    if check_login():
        events = [event["event_name"] for event in mongo.db.event_info.find()]
        if request.method == "POST":
            name,dept,regno,email = request.form["name"],request.form["dept"],request.form["regno"],request.form["email"]
            event_name = request.form.get("event")
            position = request.form.get("position")
            if not event_name in events:
                flash("Event does not exist")
            else:
                event_details = mongo.db.event_info.find_one({"event_name": event_name})
                event_date = event_details["event_date"]
                event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                winner_certificate(name,dept,event_name,regno,position,event_date)
                return redirect(url_for("admin.send_winner_certificate",email=email,name=name,regno=regno,event_name=event_name,event_date=event_date.strftime("%d-%m-%Y")))
        return render_template("admin/generate_winner_certificate.html",events=events)
    else:
        return redirect(url_for("admin.login"))
    
@admin.route("/send_winner_certificate/<email>/<name>/<regno>/<event_name>/<event_date>",methods=['GET', 'POST'])
def send_winner_certificate(email,name,regno,event_name,event_date):
    if check_login():
        event_date = datetime.strptime(event_date, "%d-%m-%Y").date()
        if os.path.isfile(os.path.join(os.path.abspath("Quiz-App/event_certificates/"),f"{event_name}_winner_{regno}.png")):
            send_winner_email(email,name,event_name,regno,event_date)
            flash("Email sent successfully")
        return "Email sent successfully"
    else:
        return redirect(url_for("admin.login"))
    
@admin.route("/add_event",methods=['GET', 'POST'])
def add_event():
    if check_login():
        if request.method == "POST":
            event_name = request.form.get("event_name")
            event_status = request.form.get("event_status")
            event_date = request.form.get("event_date")
            status = "active" if event_status=="on" else "inactive"
            if not mongo.db.event_info.find_one({"event_name":str(event_name)}):
                mongo.db.event_info.insert_one({"event_name":str(event_name),"event_status":str(status),"event_date":event_date})
                flash("Event added successfully")
            else:
                flash("Event already exists!")
        return render_template("admin/add_event.html")
    else:
        return redirect(url_for("admin.login"))
    
@admin.route("/revoke_event", methods=['GET', 'POST'])
def revoke_event():
    if check_login():
        events = [event["event_name"] for event in mongo.db.event_info.find({"event_status": "active"})]
        if request.method == "POST":
            event_name = request.form.get("event_name")
            event = mongo.db.event_info.find_one({"event_name": event_name, "event_status": "active"})
            if event:
                event_date = datetime.strptime(event["event_date"], "%Y-%m-%d").date()
                current_date = datetime.now().date()
                if event_date < current_date:
                    mongo.db.event_info.update_one({"event_name": event_name}, {"$set": {"event_status": "inactive"}})
                    flash("Event revoked successfully")
                else:
                    flash("Event not found or already inactive")
            else:
                flash("Event not found or already inactive.")
        return render_template("admin/revoke_event.html", events=events)
    else:
        return redirect(url_for("admin.login"))

@admin.route("/manage_teachers", methods=['GET', 'POST'])
def manage_teachers():
    if check_login():
        if request.method == "POST":
            action = request.form.get("action")
            
            if action == "add":
                teacher_name = request.form.get("teacher_name")
                if teacher_name and teacher_name.strip():
                    # Check if teacher already exists
                    if not mongo.db.approved_teachers.find_one({"name": teacher_name}):
                        mongo.db.approved_teachers.insert_one({"name": teacher_name, "created_at": datetime.now()})
                        flash(f"Teacher '{teacher_name}' added successfully!")
                    else:
                        flash(f"Teacher '{teacher_name}' already exists!")
                else:
                    flash("Please enter a valid teacher name!")
            
            elif action == "remove":
                teacher_id = request.form.get("teacher_id")
                if teacher_id:
                    result = mongo.db.approved_teachers.delete_one({"_id": ObjectId(teacher_id)})
                    if result.deleted_count > 0:
                        flash("Teacher removed successfully!")
                    else:
                        flash("Teacher not found!")
        
        # Get all approved teachers
        teachers = list(mongo.db.approved_teachers.find().sort("name", 1))
        return render_template("admin/manage_teachers.html", teachers=teachers)
    else:
        return redirect(url_for("admin.login"))