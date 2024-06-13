from flask import Flask, send_from_directory, abort, session, jsonify,request, redirect, url_for, render_template
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'hack'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def connect_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='YSshalini@09',
            database='hackbuzz'
        )
        print("Database connected successfully")
        return conn
    except Exception as e:
        print("Error connecting to database:", str(e))
        raise


def get_user_by_email(email):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        conn.close()
        print("Fetched user:", user)  # Print fetched user data
        return user
    except Exception as e:
        print("Error fetching user:", e)
        return None

def get_user_skills_by_email(email):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT skills FROM users WHERE email = %s", (email,))
        skills = cur.fetchone()[0]
        conn.close()
        return skills
    except Exception as e:
        print("Error fetching user skills:", e)
        return None

upload_folder = 'C:\\projects\\Web development\\hackbuzz\\uploads'

@app.route('/view_resume/<filename>')
def view_resume(filename):
    try:
        # Check if the file exists in the uploads directory
        if os.path.exists(os.path.join(upload_folder, filename)):
            return send_from_directory(upload_folder, filename, as_attachment=True)
        else:
            abort(404)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        abort(500)    



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reg')
def reg():
    return render_template('register.html')


@app.route("/modify")
def modify():
    email = session.get('email')
    user = get_user_by_email(email)
    if user:
        return render_template("modify.html", user=user)
    else:
        return redirect(url_for("index"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_resume(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None



def add_user(fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range, resume_path):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range, resume_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range, resume_path))
        conn.commit()
        print("Data inserted successfully")
    except Exception as e:
        print("Error inserting data:", e)
        conn.rollback()
    finally:
        conn.close()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        contact_number = request.form.get("contact_number")
        address = request.form.get("address")
        city = request.form.get("city")
        zipcode = request.form.get("zipcode")
        job_title = request.form.get("job_title")
        industry = request.form.get("industry")
        experience = request.form.get("experience")
        education = request.form.get("education")
        skills = request.form.get("skills")
        employment_type = request.form.get("employment_type")
        salary_range = request.form.get("salary_range")
        print("Received Files:", request.files)  # Debug print to check received files

        resume_file = request.files.get("resume")
        print("Received Resume File:", resume_file)  # Debug print to check the received resume file
        
        resume_path = save_resume(resume_file)
        print("Saved Resume Path:", resume_path)
        


        if None in [fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range] or not resume_path:
            error_message = "One or more required fields are missing."
            return render_template("register.html", error=error_message)

        add_user(fullname, email, password, contact_number, address, city, zipcode, job_title, industry, experience, education, skills, employment_type, salary_range, resume_path)
        return redirect(url_for("index")) 

    return render_template("register.html")


@app.route('/modify_profile', methods=['POST'])
def modify_profile():
    if request.method == 'POST':
        # Existing form data
        email = session.get('email')
        fullname = request.form['fullname']
        password = request.form['password']
        contact_number = request.form['contact_number']
        address = request.form['address']
        city = request.form['city']
        zipcode = request.form['zipcode']
        job_title = request.form['job_title']
        industry = request.form['industry']
        experience = request.form['experience']
        education = request.form['education']
        skills = request.form['skills']
        employment_type = request.form['employment_type']
        salary_range = request.form['salary_range']

        # Handle file upload
        if 'resume' in request.files:
            resume = request.files['resume']
            if resume.filename != '':
                filename = secure_filename(resume.filename)
                resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                resume.save(resume_path)

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users 
            SET fullname=%s, password=%s, contact_number=%s, address=%s, city=%s, zipcode=%s, 
                job_title=%s, industry=%s, experience=%s, education=%s, skills=%s, 
                employment_type=%s, salary_range=%s, resume_path=%s
            WHERE email=%s
        """, (fullname, password, contact_number, address, city, zipcode, 
              job_title, industry, experience, education, skills, 
              employment_type, salary_range, filename, email))
        
        conn.commit()
        conn.close()

        return redirect(url_for('index'))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)
        if user:  
            session['email'] = user[2] 
            session['password'] = user[3]  
            return redirect(url_for("user"))

        else:
            error = "Invalid credentials. Please try again."
    return render_template("login.html", error=error)


@app.route("/user")
def user():
    email = session.get('email')
    print("Session email:", email)  # Print session email

    user = get_user_by_email(email)
    print("Fetched user:", user)  # Print fetched user data

    if user:
        skills = user[11].split(',')  # Assuming skills are comma-separated in the database
        return render_template("user.html", user=user, skills=skills)
    else:
        return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
