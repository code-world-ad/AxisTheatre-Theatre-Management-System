import cx_Oracle
from dotenv import load_dotenv
import os

load_dotenv()

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
userquery = '''create table users (
    user_id int primary key, 
    username varchar(50) unique not null,
    name varchar(100) not null,
    address varchar(255), 
    telephone_number varchar(10))'''

theatre_table_query = '''CREATE TABLE theatres (
    theatre_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location varchar(20),
    total_seats INT NOT NULL
)'''

movies_table_query = '''CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    release_date DATE,
    genre VARCHAR(50))'''

performance_table_query = '''CREATE TABLE performances (
    performance_id INT PRIMARY KEY,
    theatre_id INT,
    movie_id INT,
    show_date DATE,
    show_time TIMESTAMP,
    available_seats INT, 
    FOREIGN KEY (theatre_id) REFERENCES theatres(theatre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
)'''


reservation_table_query = '''CREATE TABLE reservations (
    reservation_id INT PRIMARY KEY,
    user_id INT,
    performance_id INT,
    reservation_number INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (performance_id) REFERENCES performances(performance_id)
)'''

user_sequence_query = '''CREATE SEQUENCE user_sequence
START WITH 1000'''

register_user_proc = '''CREATE OR REPLACE PROCEDURE register_user(
    p_username IN VARCHAR2,
    p_name IN VARCHAR2,
    p_address IN VARCHAR2,
    p_telephone_number IN VARCHAR2
) AS
BEGIN
    INSERT INTO users (user_id, username, name, address, telephone_number)
    VALUES (user_sequence.nextval, p_username, p_name, p_address, p_telephone_number);
    COMMIT;
END;
'''

reservation_sequence_query = '''CREATE SEQUENCE reservation_sequence
START WITH 1
INCREMENT BY 1
MINVALUE 1
MAXVALUE 999999999999999999999999999
'''

make_reservation_proc = '''CREATE OR REPLACE PROCEDURE make_reservation(
    p_username IN VARCHAR2,
    p_performance_id INT,
    p_reservation_number OUT NUMBER
) AS
    v_user_id NUMBER;
    v_available_seats NUMBER;
BEGIN
    -- Get user ID based on username
    SELECT user_id INTO v_user_id FROM users WHERE username = p_username;

    v_available_seats := 0;
    BEGIN
        SELECT available_seats INTO v_available_seats
        FROM performances
        WHERE performance_id = p_performance_id;

    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            -- Handle the case where no data is found
            v_available_seats := 0;
    END;

    IF v_available_seats > 0 THEN
        -- Decrement available seats
        UPDATE performances
        SET available_seats = available_seats - 1
        WHERE performance_id = p_performance_id;

        -- Generate reservation number
        SELECT reservation_sequence.nextval INTO p_reservation_number FROM dual;

        -- Make reservation
        INSERT INTO reservations (reservation_id, user_id, performance_id, reservation_number)
        VALUES (reservation_sequence.nextval, v_user_id, p_performance_id, p_reservation_number);
        COMMIT;
    ELSE
        -- Handle no available seats
        p_reservation_number := -1;
    END IF;
END;
'''

check_login_proc = '''CREATE OR REPLACE PROCEDURE check_login(
    p_username IN VARCHAR2,
    p_login_success OUT NUMBER
)
AS
    v_user_count NUMBER;
BEGIN
    -- Check if the username exists in the users table
    SELECT COUNT(*)
    INTO v_user_count
    FROM users
    WHERE username = p_username;

    -- Set the login success status
    IF v_user_count > 0 THEN
        p_login_success := 1; -- User found, login successful
    ELSE
        p_login_success := 0; -- User not found, login failed
    END IF;
END check_login;

'''

find_theatre_proc = '''CREATE OR REPLACE PROCEDURE find_theatres_for_movie(
    p_movie_name IN VARCHAR2,
    p_results OUT SYS_REFCURSOR
)
AS
BEGIN
    OPEN p_results FOR
    SELECT t.name AS theatre_name, p.performance_id, p.available_seats
    FROM performances p
    JOIN movies m ON p.movie_id = m.movie_id
    JOIN theatres t ON p.theatre_id = t.theatre_id
    WHERE m.name = p_movie_name;
END find_theatres_for_movie;
'''

#print(userquery)
cursor.execute('Drop table reservations')
cursor.execute('Drop table performances')
cursor.execute('Drop table movies')
cursor.execute('Drop table theatres')
cursor.execute('Drop table users')
cursor.execute('Drop sequence user_sequence')
cursor.execute('Drop sequence reservation_sequence')
cursor.execute('Drop procedure register_user')
cursor.execute('Drop procedure make_reservation')
cursor.execute('Drop procedure check_login')
cursor.execute('Drop procedure find_theatres_for_movie')
conn.commit()

cursor.execute(userquery)
cursor.execute(theatre_table_query)
cursor.execute(movies_table_query)
cursor.execute(performance_table_query)
cursor.execute(reservation_table_query)
cursor.execute(register_user_proc)
cursor.execute(make_reservation_proc)
cursor.execute(check_login_proc)
cursor.execute(find_theatre_proc)
cursor.execute(user_sequence_query)
cursor.execute(reservation_sequence_query)
conn.commit()

movie_insertions = ["""INSERT INTO movies(movie_id, name, release_date, genre) VALUES(1, 'Inception', TO_DATE('2010-07-16','YYYY-MM-DD'), 'Sci-Fi')""",
                    """INSERT INTO movies(movie_id, name, release_date, genre) VALUES(2, 'The Dark Knight', TO_DATE('2008-07-18','YYYY-MM-DD'), 'Action')""",
                    """INSERT INTO movies(movie_id, name, release_date, genre) VALUES(3, 'Titanic', TO_DATE('1997-12-19', 'YYYY-MM-DD'), 'Romance')""",
                    """INSERT INTO movies(movie_id, name, release_date, genre) VALUES(4, 'Ice Age', TO_DATE('2000-12-19', 'YYYY-MM-DD'), 'Fantasy')""",
                    """INSERT INTO movies(movie_id, name, release_date, genre) VALUES(5, 'Harry Potter', TO_DATE('2001-12-19', 'YYYY-MM-DD'), 'Sci-Fi')"""]
for i in movie_insertions:
    cursor.execute(i)
    conn.commit()

theatre_insertions = ["""INSERT INTO theatres (theatre_id, name, location, total_seats) VALUES(101, 'PVR', 'City Center', 100)""",
                      """INSERT INTO theatres (theatre_id, name, location, total_seats) VALUES(102, 'INOX SUPER', 'Downtown Plaza', 200)""",
                      """INSERT INTO theatres (theatre_id, name, location, total_seats) VALUES(103, 'LUXE Cinemas', 'Suburb Square', 250)"""]
for i in theatre_insertions:
    cursor.execute(i)
    conn.commit()

performances_insertion = ["""INSERT INTO performances (performance_id, movie_id, theatre_id, show_date, show_time, available_seats) VALUES(1001, 1, 101,TO_DATE('2023-01-01', 'YYYY-MM-DD'), TO_TIMESTAMP( '18:00', 'HH24:MI'), 100)""",
                         """INSERT INTO performances (performance_id, movie_id, theatre_id, show_date, show_time, available_seats) VALUES(1002, 2, 102,TO_DATE('2023-01-02', 'YYYY-MM-DD'), TO_TIMESTAMP('15:30', 'HH24:MI'), 200)""",
                          """INSERT INTO performances (performance_id, movie_id, theatre_id, show_date, show_time, available_seats) VALUES(1003, 3, 103,TO_DATE('2023-01-03', 'YYYY-MM-DD'), TO_TIMESTAMP('20:00', 'HH24:MI'),250)""",
                          """INSERT INTO performances (performance_id, movie_id, theatre_id, show_date, show_time, available_seats) VALUES(1004, 2, 101,TO_DATE('2023-01-03', 'YYYY-MM-DD'), TO_TIMESTAMP('15:30', 'HH24:MI'),100)""",
                          """INSERT INTO performances (performance_id, movie_id, theatre_id, show_date, show_time, available_seats) VALUES(1005, 4, 103,TO_DATE('2023-01-03', 'YYYY-MM-DD'), TO_TIMESTAMP('18:00', 'HH24:MI'),200)""",
                          """INSERT INTO performances (performance_id, movie_id, theatre_id, show_date, show_time, available_seats) VALUES(1006, 1, 102,TO_DATE('2023-01-03', 'YYYY-MM-DD'), TO_TIMESTAMP('20:00', 'HH24:MI'),200)""",
                          """INSERT INTO performances (performance_id, movie_id, theatre_id, show_date, show_time, available_seats) VALUES(1007, 5, 101,TO_DATE('2023-01-03', 'YYYY-MM-DD'), TO_TIMESTAMP('21:00', 'HH24:MI'),200)"""]
                          

for i in performances_insertion:
    cursor.execute(i)
    conn.commit()