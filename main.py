from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import cx_Oracle
from dotenv import load_dotenv
import os

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basedir, 'templates')

app = Flask(__name__, template_folder = template_dir)
app.secret_key = os.getenv('FLASK_SECRET_KEY')


# Set secret key from environment variable
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Oracle client path from environment variable
oracle_client_path = os.getenv('ORACLE_CLIENT_PATH')

# Initialize Oracle client
cx_Oracle.init_oracle_client(lib_dir=oracle_client_path)

# Connection parameters from environment variables
username = os.getenv('ORACLE_USERNAME')
password = os.getenv('ORACLE_PASSWORD')
dsn = os.getenv('ORACLE_DSN')


# Your Oracle connection details
connection_string = f"{username}/{password}@{dns}"
conn = cx_Oracle.connect(connection_string)
cursor = conn.cursor()

# Flask routes
@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        try:
          # Call PL/SQL function to check login credentials
            login_success = cursor.var(cx_Oracle.NUMBER)
            cursor.callproc("check_login", [username, login_success])

            # Access the output parameter value
            login_status = login_success.getvalue()

            if login_status == 1:
                session['username'] = username
                return redirect(url_for('login_welcome'))
            else:
                return jsonify({"message": "Login failed. Invalid username"})
        except Exception as e:
            return jsonify({"error": str(e)})
    return render_template('login.html')

@app.route('/login_welcome')
def login_welcome():
    if 'username' in session:
        return render_template('login_welcome.html', username=session['username'])
    else:
        return redirect(url_for('login'))

    
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        data = data = request.form
        username = data['username']
        name = data['name']
        address = data['address']
        telephone_number = data['telephone_number']

        try:
        # Call PL/SQL procedure to register user
            cursor.callproc("register_user", [username, name, address, telephone_number])
            conn.commit()
            return jsonify({"message": "User registered successfully"})
            
        except Exception as e:
            return jsonify({"error": str(e)})
    return render_template('register.html')

@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/find_theatres', methods=['GET', 'POST'])
def find_theatres():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            movie_name = request.form.get('movie_name', '')
            theatres, performance_ids, available_seats = get_theaters_and_performance_ids(movie_name)
            print(theatres, performance_ids, available_seats)
            return redirect(url_for('display_theatres', theatres=theatres, performance_ids=performance_ids, available_seats=available_seats))

        except Exception as e:
            return jsonify({"error": str(e)})

    return render_template('find_theatres_form.html')

@app.route('/display_theatres')
def display_theatres():
    theatres = request.args.getlist('theatres')
    performance_ids = request.args.getlist('performance_ids')
    available_seats = request.args.getlist('available_seats')

    return render_template('display_theatres.html', theatres=theatres, performance_ids=performance_ids, available_seats=available_seats)

            
def get_theaters_and_performance_ids(movie_name):
    try:
        # Call the PL/SQL procedure to get theaters and performance IDs
        results = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc("find_theatres_for_movie", [movie_name, results])

        # Fetch the results from the cursor
        cursor_results = results.getvalue()

        # Process the results
        theatres = []
        performance_ids = []
        available_seats = []
        for row in cursor_results:
            theatre_name, performance_id, available_seat = row
            print(theatre_name, performance_id, available_seat)
            theatres.append(theatre_name)
            performance_ids.append(performance_id)
            available_seats.append(available_seat)
        return theatres, performance_ids, available_seats
    except Exception as e:
            return jsonify({"error": str(e)})


@app.route('/reserve', methods=['GET', 'POST'])
def make_reservation():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            
            username = request.form.get('username')
            performance_id = int(request.form.get('performance_id'))

            # Call PL/SQL procedure to make reservation
            reservation_number = cursor.var(cx_Oracle.NUMBER)
            cursor.callproc("make_reservation", [username, performance_id, reservation_number])

            # Access the value of the OUT parameter
            reservation_number_value = reservation_number.getvalue()

            # Commit the transaction
            conn.commit()

            # Check the value of reservation_number
            if reservation_number_value > 0:
                return render_template('make_reservation.html', reservation_number=reservation_number_value)
            else:
                return jsonify({"message": "No available seats for the selected performance"})
        except Exception as e:
            return jsonify({"error": str(e)})

    # Render a form to input the reservation details
    return render_template('reserve_form.html')

if __name__ == '__main__':
    app.run(debug=True)