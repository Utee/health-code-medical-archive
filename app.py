# app.py

from flask import Flask, flash, render_template, request, redirect, session, url_for
import json
import qrcode
from twilio.rest import Client
from flask import request

app = Flask(__name__, template_folder='templates')
app.secret_key = 'kingtest_TIMES'

users = []
doctors = []
patients = []

# Load existing data from the JSON file
with open('data.json', 'r') as file:
    data = json.load(file)

# Update the 'users' list
users = data.get('users', [])


SESSION_KEY = 'logged_in_user'




# Helper function to save data to the JSON file
# Helper function to save data to the JSON file
def save_data():
    data['users'] = users
    data['doctors'] = doctors
    data['patients'] = patients

    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)


# Landing page
@app.route('/')
def landing_page():
    return render_template('landing_page.html')


admin_username = 'admin'
admin_password = 'admin_password'

# Login credentials for doctors
doctor_logins = [
    {'username': 'doctor1', 'password': 'doctor1_password'},
    {'username': 'doctor2', 'password': 'doctor2_password'}
]

# Login credentials for patients
patient_logins = [
    {'username': 'patient1', 'password': 'patient1_password'},
    {'username': 'patient2', 'password': 'patient2_password'},
    {'username': 'patient3', 'password': 'patient3_password'},
    {'username': 'patient4', 'password': 'patient4_password'}
]

@app.route('/dashboard_admin')
def admin_dashboard():
    if 'is_admin' in session and session['is_admin']:
        return render_template('admin_dashboard.html', users=data.get('users', []))
    else:
        flash('Unauthorized access. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))

# Admin dashboard functionalities
@app.route('/admin/user/add', methods=['GET', 'POST'])
def admin_add_user():
    if request.method == 'POST':
        # Process user registration form data
        # Update data dictionary and save_data() function
        flash('User added successfully!', 'success')

    return render_template('admin_add_user.html')

@app.route('/admin/user/edit/<username>', methods=['GET', 'POST'])
def admin_edit_user(username):
    user = next((user for user in users if user['username'] == username), None)
    if user:
        if request.method == 'POST':
            # Process user edit form data
            # Update data dictionary and save_data() function
            flash('User edited successfully!', 'success')

        return render_template('admin_edit_user.html', user=user)
    else:
        flash(f'User with username {username} not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/delete/<username>')
def admin_delete_user(username):
    global users
    users = [user for user in users if user['username'] != username]
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


# Login route
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Extract login credentials from the login form
        username = request.form['username']
        password = request.form['password']

        if username == admin_username and password == admin_password:
            # Use a fixed OTP for admin
            otp = '000001'

            # Store the OTP in the session
            session['otp'] = otp

            # Flash success message
            flash(f'Admin login successful! Please enter the OTP sent to your device.', 'success')

            # Store admin status in session
            session['is_admin'] = True

            # Redirect to the OTP verification page for admin
            return redirect(url_for('verify_otp', user_type='admin'))

        # Check if the user is a doctor
        is_doctor = 'is_doctor' in request.form

        # Check if the credentials match a doctor login
        if is_doctor:
            doctor = next((doc for doc in doctor_logins if doc['username'] == username and doc['password'] == password), None)
            if doctor:
                # Use a fixed OTP for doctors
                otp = '321456'

                # Store the OTP in the session
                session['otp'] = otp

                # Flash success message
                flash(f'Doctor login successful! Please enter the OTP sent to your device.', 'success')

                # Store user type in session
                # session['is_doctor'] = True
                session[SESSION_KEY] = {'username': username, 'is_doctor': True}
                

                # Redirect to the OTP verification page for doctors
                return redirect(url_for('verify_otp', user_type='doctor'))

    # Redirect back to the login page
    return render_template('login.html')

# OTP verification route
@app.route('/verify_otp/<user_type>', methods=['POST', 'GET'])
def verify_otp(user_type):
    if request.method == 'POST':
        # Extract OTP entered by the user
        entered_otp = request.form['otp']

        # Retrieve the stored OTP from the session
        stored_otp = session.get('otp')

        # Check if the entered OTP matches the stored OTP
        if entered_otp == stored_otp:
            # Clear the stored OTP from the session
            session.pop('otp', None)

            # Redirect to the respective dashboard based on user type
            if user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user_type == 'doctor':
                return redirect(url_for('doctor_dashboard'))
        else:
            flash('Incorrect OTP. Please try again.', 'danger')

    # Render the OTP verification page
    return render_template('verify_otp.html', user_type=user_type)



@app.route('/register', methods=['POST'])
def register():
    # Extract user data from the registration form
    username = request.form['username']
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']

    # Check if the user is a doctor
    is_doctor = 'is_doctor' in request.form

    # Add user or doctor to the respective list
    if is_doctor:
        doctors.append({'username': username, 'email': email, 'name': name, 'password': password})
    else:
        users.append({'username': username, 'email': email, 'name': name, 'password': password})

    # Flash success message
    flash('Account created successfully!', 'success')

    return redirect(url_for('login'))

# Doctor registration
@app.route('/registration_doctor', methods=['GET', 'POST'])
def registration_doctor():
    if request.method == 'POST':
        # Process doctor registration form data
        # Update data dictionary and save_data() function
        return render_template('registration_doctor.html')
    

# Function to get the logged-in doctor's username
def get_logged_in_doctor_username():
    # Check if the user is logged in
    if SESSION_KEY in session and session[SESSION_KEY]['is_doctor']:
        return session[SESSION_KEY]['username']
    else:
        return None
    
# Doctor dashboard
@app.route('/doctor_dashboard')
def doctor_dashboard():
    # if 'is_doctor' in session and session['is_doctor']:
    if SESSION_KEY in session and session[SESSION_KEY]['is_doctor']:
    
        return render_template('dashboard_doctor.html', users=users)
    else:
        flash('Unauthorized access. Please log in as a doctor.', 'danger')
        return redirect(url_for('login'))

# Doctor dashboard functionalities
@app.route('/doctor/user/create', methods=['GET', 'POST'])
def doctor_create_user():
    if request.method == 'POST':
        # Extract patient data from the registration form
        username = request.form['username']
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        next_of_kin = request.form['next_of_kin']
        next_appointment = request.form['next_appointment']
        prescription = request.form['prescription']

        # Add patient to the patients list
        patients.append({
            'username': username,
            'email': email,
            'name': name,
            'password': password,
            'age': age,
            'gender': gender,
            'next_of_kin': next_of_kin,
            'next_appointment': next_appointment,
            'prescription': prescription
        })

        save_data()

        # Flash success message
        flash('Patient created successfully!', 'success')

    return render_template('registration_patient.html')

# ...

# Doctor dashboard functionalities
@app.route('/doctor/view_qrcode', methods=['GET', 'POST'])
def doctor_view_qrcode():
    if request.method == 'POST':
        # Extract username entered by the user
        username = request.form['username']

        # Find the user in the list
        user = next((u for u in users if u['username'] == username), None)

        if user:
            # Render the page to view the QR code
            return render_template('view_qrcode.html', user=user)
        else:
            flash(f'User with username {username} not found.', 'danger')

    return render_template('view_qrcode_input.html')

# ...




@app.route('/generate_qrcode/<username>', methods=['GET', 'POST'])
def generate_qrcode(username):
    user = next((user for user in users if user['username'] == username), None)

    if user:
        # Check if the request method is POST
        if request.method == 'POST':
            # Generate the QR code without checking the password
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(str(user))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(f"static/qrcodes/{username}.png")

        flash('QR Code generated successfully!', 'success')

        return render_template('generate_qrcode.html', username=username)
    else:
        flash(f'User with username {username} not found.', 'danger')
        return redirect(url_for('dashboard_doctor'))
    



# Registration route for patients
@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        # Extract patient data from the registration form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Add patient to the patients list with minimal information
        patients.append({
            'username': username,
            'email': email,
            'password': password,
        })

        # Flash success message
        flash('Account created successfully! Please fill out your profile.', 'success')

        # Redirect to the patient profile filling page
        return redirect(url_for('fill_patient_profile', username=username))

    return render_template('register_patient.html')

# Patient profile filling route
@app.route('/fill_patient_profile/<username>', methods=['GET', 'POST'])
def fill_patient_profile(username):
    # Find the patient in the list
    patient = next((p for p in patients if p['username'] == username), None)

    if patient:
        if request.method == 'POST':
            # Extract patient profile data from the form
            patient['name'] = request.form['name']
            patient['age'] = request.form['age']
            patient['gender'] = request.form['gender']
            patient['address'] = request.form['address']
            patient['next_of_kin'] = request.form['next_of_kin']
            # Add other profile details as needed

            save_data()

            # Flash success message
            flash('Patient profile filled successfully!', 'success')

            # Redirect to the patient dashboard
            return redirect(url_for('patient_dashboard'))

        return render_template('fill_patient_profile.html', patient=patient)
    else:
        flash(f'Patient with username {username} not found.', 'danger')
        return redirect(url_for('landing_page'))

# Patient registration route
@app.route('/patient_registration', methods=['GET', 'POST'])
def patient_registration():
    if request.method == 'POST':
        # Process patient registration form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Add your logic for patient registration here
        # For example, add the patient to the 'patients' list
        patients.append({
            'username': username,
            'email': email,
            'password': password,
            # Add more fields as needed
        })

        # Flash success message
        flash('Patient registration successful!', 'success')

        return redirect(url_for('login'))  # Redirect to the login page after registration

    return render_template('register_patient.html')

# ...

# Login route for patients
@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        # Extract login credentials from the login form
        username = request.form['username']
        password = request.form['password']

        # Check if the credentials match a patient login
        patient = next((pat for pat in patient_logins if pat['username'] == username and pat['password'] == password), None)
        if patient:
            # Flash success message
            flash(f'Patient login successful!', 'success')

            # Store user type in session
            session[SESSION_KEY] = {'username': username, 'is_doctor': False}

            # Redirect to the patient dashboard or another appropriate page
            return redirect(url_for('patient_dashboard'))
    
    # Redirect back to the login page
    return render_template('patient_login.html')

# Patient dashboard
@app.route('/patient_dashboard')
def patient_dashboard():
    if SESSION_KEY in session and not session[SESSION_KEY]['is_doctor']:
        return render_template('dashboard_patient.html', patients=patients)
    else:
        flash('Unauthorized access. Please log in as a patient.', 'danger')
        return redirect(url_for('login'))







@app.route('/create_appointment_form')
def create_appointment_form():
    return render_template('create_appointment_form.html')







# SMS notification
@app.route('/send_sms/<user_id>')
def send_sms(user_id):
    # user = data['patients'][user_id]  # Assuming patients are stored in data dictionary

    # Your Twilio credentials and SMS sending logic here

    return redirect(url_for('dashboard_doctor'))

if __name__ == '__main__':
    app.run(debug=True)
