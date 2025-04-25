# LSRW Skill Assessment Platform

A robust web-based platform for conducting, managing, and reporting English language skill assessments (Listening, Speaking, Reading, Writing) for students at Velammal Engineering College. The system supports university, model, and lab exams, provides automated report generation, and includes event management and certificate generation for club activities.

---

## 🚀 Project Overview

This platform streamlines the process of English language skill assessment by providing:

- **Student, Teacher, and Admin Portals**: Role-based access for students, teachers, and administrators.
- **Online Test Management**: Create, edit, and manage tests with audio and question uploads.
- **Automated Evaluation**: Instant scoring and result calculation.
- **Report Generation**: Downloadable and emailable PDF reports for students and batch-wise reports for departments.
- **Event & Certificate Management**: Manage club events and generate winner certificates.
- **Technical Issue Tracking**: Identify and resolve test-related technical issues.
- **Password Reset & Security**: Secure authentication and password reset via email.

---

## 🏗️ Features

### For Students
- **Signup/Login**: Register and access personalized dashboard.
- **Take Tests**: Enter test codes to attempt university, model, or lab exams.
- **Instant Results**: View and download detailed performance reports.
- **Edit Profile**: Update personal and academic details.
- **Event Certificates**: Download certificates for club events.

### For Teachers
- **Login/Signup**: Secure access for faculty.
- **Test Management**: View test codes, questions, and handle technical issues.
- **Result Analysis**: View and download results for their handling classes.
- **Class Management**: Add or remove handling classes.

### For Admins
- **Test Creation**: Add new tests with audio and question files.
- **Batch Report Generation**: Generate and download department-wise reports (University, Model, Lab).
- **Technical Issue Review**: View and resolve zero-score/technical issue cases.
- **Event Management**: Add/revoke events, generate and send winner certificates.
- **User Management**: Admin signup, password reset, and security controls.

---

## 🗂️ Project Structure

```
src/
  routes/           # Flask Blueprints for main, admin, teacher, events
  templates/        # Jinja2 HTML templates for all roles and features
  static/           # CSS, JS, images (e.g., VEC-logo.png)
  extensions.py     # MongoDB and other Flask extensions
  helper.py         # Utility functions (token, report generation, etc.)
  send_email.py     # Email sending logic for reports, resets, certificates
Quiz-App/
  reports/          # Generated student PDF reports
  admin_reports/    # Generated batch PDF/CSV reports
  event_certificates/ # Generated event certificates
```

---

## ⚙️ Technology Stack

- **Backend**: Python, Flask, Flask-WTF, MongoDB (PyMongo)
- **Frontend**: HTML (Jinja2), CSS (Bootstrap), JavaScript (jQuery)
- **PDF Generation**: pdfkit, WeasyPrint
- **Email**: SMTP (send_email.py)
- **Authentication**: Session-based, secure password hashing
- **Image Processing**: OpenCV (for certificate generation)

---

## 📝 Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/LSRW-Skill-Assessment-Platform.git
   cd LSRW-Skill-Assessment-Platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB**
   - Ensure MongoDB is running and accessible.
   - Update connection details in `src/extensions.py` if needed.

4. **Configure Email**
   - Set up SMTP credentials in `src/send_email.py`.

5. **Environment Variables (`.env` Management)**
   - Create a `.env` file in the project root (same directory as `src/`).
   - Add all sensitive configuration here, such as:
     ```
     SECRET_KEY=your_secret_key
     MONGO_URI=mongodb://localhost:27017/your_db
     MAIL_USERNAME=your_email@example.com
     MAIL_PASSWORD=your_email_password
     TOKEN_SECRET_KEY=your_token_secret
     ```
   - The application loads these variables automatically using `python-dotenv` (see `src/config.py` and `src/helper.py`).

6. **Run the application**
   ```bash
   export FLASK_APP=src
   flask run
   ```
   The app will be available at `http://localhost:5000/`.

---

## 📄 Usage Guide

- **Students**: Register, log in, and use the dashboard to take tests or download reports/certificates.
- **Teachers**: Log in to manage classes, view results, and resolve technical issues.
- **Admins**: Use the dashboard to create tests, manage reports, events, and handle user management.

---

## 📊 Reports & Certificates

- **Student Reports**: Automatically generated as PDF after each test; sent via email and available for download.
- **Batch Reports**: Admins can generate department-wise reports for university, model, or lab exams.
- **Event Certificates**: Generated for event winners and participants, with email delivery.

---

## 🛠️ Customization

- **Add/Remove Departments, Classes, Events**: Update the relevant dropdowns and MongoDB collections.
- **Change Branding**: Replace `VEC-logo.png` in `src/static/`.
- **Email Templates**: Edit HTML files in `src/templates/`.

---

## 🧑‍💻 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📬 Contact

For queries or support, contact the Communicative English Team at Velammal Engineering College.

---

## 📜 License

This project is for educational and institutional use at Velammal Engineering College.