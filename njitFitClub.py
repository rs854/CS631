from flask import Flask, request
from flask import render_template
from flaskext.mysql import MySQL
import flask
import json
import re
import os
from datetime import date, datetime
import logging, sys

# Flag to set if running on production
# server or local development
debug = False

# Initialize MySQL database connection
mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'n17s21o1'
app.config['MYSQL_DATABASE_DB'] = 'NJITFitnessClub'
app.config['MYSQL_DATABASE_HOST'] = 'nma.cqcaflzcpcei.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 33306
mysql.init_app(app)

if debug:
    # If in development mode, override MySQL
    # settings to point to local development server
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'n17s21o1'
    app.config['MYSQL_DATABASE_PORT'] = 3306
else:
    # If in production mode, redirect logs to 
    # Apache error log file
    logging.basicConfig(stream=sys.stderr)

# HOMEPAGE
@app.route("/")
def index():
    return app.send_static_file('index.html')


# HR AND PAYROLL PAGE
@app.route("/payroll")
def payroll():
    # Connect to database
    cnx = mysql.connect()
    cursor = cnx.cursor()
    # Query all instructors
    cursor.execute("SELECT * FROM Instructor")
    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    # Render HR and Payroll page with list of instructors
    return render_template('payroll.html', instructors=r)


# NEW EMPLOYEE FORMS
@app.route("/employees/<type>", methods=["GET"])
def new_employee_form(type):
    # Return either salaried or hourly new employee form
    if type == "salaried":
        return app.send_static_file('new_salaried_employee_form.html')
    else:
        return app.send_static_file('new_hourly_employee_form.html')


# NEW EMPLOYEE
@app.route("/employees", methods=["POST"])
def new_employee():
    # Connect to the database
    cnx = mysql.connect()
    cursor = cnx.cursor()

    # Get Employee info from POST data
    name = ""
    salary = ""
    wage = ""
    numberOfHoursTaught = ""
    try:
        name = request.form["Name"]
    except:
        name = None
    try:
        salary = request.form["Salary"]
    except:
        salary = None
    try:
        wage = request.form["Wage"]
    except:
        wage = None
    try:
        numberOfHoursTaught = request.form["NumberHoursTaught"]
    except:
        numberOfHoursTaught = None

    # Write employee data to database
    query = ""
    if salary:
        query = "INSERT INTO `Instructor` (`Name`, `Salary`) VALUES (%s, %s);"
        cursor.execute(query, (name, salary))
    else:
        query = "INSERT INTO `Instructor` (`Name`, `Wage`, `NumberHoursTaught`) VALUES (%s, %s, %s);"
        cursor.execute(query, (name, wage, numberOfHoursTaught))
    cnx.commit()
    # Close database connection
    cursor.close()
    cnx.close()

    # Report to user that the record was added and
    # provide link to go back to HR and Payroll page
    return 'Employee Added!<br><a href="/payroll">Go Back</a>'


# EDIT EMPLOYEES
@app.route("/employees/edit", methods=["GET", "POST"])
def edit_employee():
    if request.method == "GET":
        # If HTTP method is GET
        # Connect to database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Get employee name from HTTP GET data
        name = request.args["employeeName"]
        # Query employee data
        cursor.execute("SELECT * FROM Instructor WHERE Name=%s", name)
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        # Close database connection
        cursor.close()
        cnx.close()
        # Render Edit Employee form with employee data
        return render_template('edit_employee_form.html', instructor=r[0])
    else:
        # If HTTP method is POST
        # Connect to database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Get employee info from POST data
        name = request.form["Name"]
        salary = request.form["Salary"]
        wage = request.form["Wage"]
        numberOfHoursTaught = request.form["NumberHoursTaught"]

        if salary in ["", "None"]:
            salary = "NULL"

        if wage in ["", "None"]:
            wage = "NULL"

        if numberOfHoursTaught in ["", "None"]:
            numberOfHoursTaught = "NULL"

        # Update employee info in the database
        query = "UPDATE `Instructor` SET `Salary`=%s, `Wage`=%s, `NumberHoursTaught`=%s WHERE `Name` = %s"
        cursor.execute(query, (salary, wage, numberOfHoursTaught, name))
        cnx.commit()
        # Close the database connection
        cursor.close()
        cnx.close()
        # Report to user that the record was updated and
        # provide link to go back to HR and Payroll page
        return '{} Record Updated!<br><a href="/payroll">Go Back</a>'.format(name)


# REMOVE EMPLOYEE
@app.route("/employees/remove", methods=["GET"])
def remove_employee():

    # Connect to the database
    cnx = mysql.connect()
    cursor = cnx.cursor()

    # Get employee name from HTTP GET data
    name = request.args.get('employeeName', '')

    # Remove employee from the database
    query = "DELETE FROM `Instructor` WHERE `Name`=%s"
    cursor.execute(query, name)
    cnx.commit()

    # Close the database connection
    cursor.close()
    cnx.close()

    # Report to the user that the record was removed and
    # provide a link back to the HR and Payroll page
    return '{} Record Removed!<br><a href="/payroll">Go Back</a>'.format(name)


# EXERCISE MANAGEMENT
@app.route("/exercises", methods=["GET", "POST"])
def exercises():
    if request.method == "GET":
        # If HTTP GET
        # Connect to the database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Query all exercise types
        cursor.execute("SELECT * FROM ExerciseType")
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        # Close the connection to the database
        cursor.close()
        cnx.close()
        # Render the Exercise Management page with the 
        # list of exercise types
        return render_template('exercises.html', exercises=r)
    else:
        # If HTTP POST
        # Connect to the database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Get Exercise info from POST data
        name = request.form["Name"]
        description = request.form["Description"]
        if description == "":
            description = "NULL"

        # Add exercise to database
        query = "INSERT INTO `ExerciseType` (`Name`, `Description`) VALUES (%s, %s);"
        cursor.execute(query, (name, description))
        cnx.commit()

        # Close the database connection
        cursor.close()
        cnx.close()
        
        # Report to the user that the record was added and
        # provide a link back to the Exercise Management page
        return 'Exercise Added!<br><a href="/exercises">Go Back</a>'


# NEW EXERCISE FORM
@app.route("/exercises/new", methods=["GET"])
def new_exercise():
    return app.send_static_file('new_exercise_form.html')


# 
@app.route("/exercises/edit", methods=["GET", "POST"])
def edit_exercise():
    if request.method == "GET":
        # If HTTP GET
        # Connect to database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Get exercise type name from HTTP GET data
        name = request.args["exerciseName"]
        # Query Exercise Type data from database
        cursor.execute("SELECT * FROM ExerciseType WHERE Name=%s", name)
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        # Close connection to database
        cursor.close()
        cnx.close()
        # Render edit exercise form with exercise type data
        return render_template('edit_exercise_form.html', exercise=r[0])
    else:
        # If HTTP POST
        # Connect to database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Get exercise type info from HTTP POST data
        name = request.form["Name"]
        description = request.form["Description"]
        if description in ["", "None"]:
            description = "NULL"
        # Update exercise type record in the database
        query = "UPDATE `ExerciseType` SET `Description`=%s WHERE `Name` = %s"
        cursor.execute(query, (description, name))
        cnx.commit()
        # Close the connection to the database
        cursor.close()
        cnx.close()
        # Display text to user that record has been updated
        # and provide link to go back to Exercise Management page
        return '{} Record Updated!<br><a href="/exercises">Go Back</a>'.format(name)


# REMOVE EXERCISE TYPE
@app.route("/exercises/remove", methods=["GET"])
def remove_exercise():
    # Connect to the database
    cnx = mysql.connect()
    cursor = cnx.cursor()
    # Get exercise type name from HTTP GET data
    name = request.args.get('exerciseName', '')
    # Remove record from database
    query = "DELETE FROM `ExerciseType` WHERE `Name`=%s"
    cursor.execute(query, name)
    cnx.commit()
    # Close connection to the database
    cursor.close()
    cnx.close()
    # Display text to user that record has been removed
    # and provide link to go back to Exercise Management page
    return '{} Record Removed!<br><a href="/exercises">Go Back</a>'.format(name)


# EXERCISE CLASS MANAGEMENT
@app.route("/classes", methods=["GET", "POST"])
def classes():
    if request.method == "GET":
        # If HTTP GET
        # Connect to the database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Query Exercise Classes
        query = """
        SELECT es.ID AS 'ID', 
            es.Duration AS 'Duration', 
            es.StartTime AS 'StartTime', 
            r.BuildingName AS 'BuildingName',
            r.RoomNumber AS 'Room', 
            et.Name AS 'ExerciseType', 
            i.Name AS 'Instructor'
        FROM ExerciseSchedule es, Room r, ExerciseType et, Instructor i
        WHERE es.Room = r.ID AND
            es.ExerciseType = et.ID AND
            es.Instructor = i.ID
        """
        cursor.execute(query)
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        # Close connection to database
        cursor.close()
        cnx.close()
        # Render Exercise Class Management page with list of classes
        return render_template('classes.html', classes=r)
    else:
        # If HTTP POST
        # Connect to the database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Get class info from HTTP POST data
        duration = request.form["Duration"]
        start_time = request.form["StartDate"] + " " + request.form["StartTime"]
        room = request.form["Room"]
        exercise_type = request.form["ExerciseType"]
        instructor = request.form["Instructor"]
        # Add exercise class to the database
        query = "INSERT INTO `ExerciseSchedule` (`Duration`, `StartTime`, `Room`, `ExerciseType`, `Instructor`) VALUES (%s, %s, %s, %s, %s);"
        cursor.execute(query, (duration, start_time, room, exercise_type, instructor))
        cnx.commit()
        # Close the connection to the database
        cursor.close()
        cnx.close()
        # Display text to user that record has been added
        # and provide link to go back to Exercise Class Management page
        return 'Exercise Class Added!<br><a href="/classes">Go Back</a>'


# EXERCISE CLASS REGISTRATION
@app.route("/classes/register", methods=["GET", "POST"])
def class_registration():
    if request.method == "GET":
        # If HTTP GET
        # Connect to the database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Query available classes from the database
        query = """
        SELECT es.ID 'ClassID', et.Name 'ExerciseType', es.StartTime, es.Duration, 
            r.BuildingName, r.RoomNumber, i.Name 'Instructor', r.Capacity, COUNT(mes.Member) 'Registered'
        FROM ExerciseSchedule es
        LEFT JOIN Room r ON es.Room = r.ID
        LEFT JOIN MemberExerciseSchedule mes ON es.ID = mes.ExerciseSchedule
        LEFT JOIN ExerciseType et ON es.ExerciseType = et.ID
        LEFT JOIN Instructor i ON es.Instructor = i.ID
        WHERE es.StartTime > NOW() 
        GROUP BY es.ID, et.Name, es.StartTime, es.Duration,r.BuildingName, r.RoomNumber, i.Name, r.Capacity
        HAVING COUNT(mes.Member) < r.Capacity
        """
        cursor.execute(query)
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        # Query all members
        cursor.execute("SELECT * FROM Member")
        m = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        # Close connection to database
        cursor.close()
        cnx.close()
        # Render class registration page
        return render_template('class_registration.html', classes=r, members=m)
    else:
        # If HTTP POST
        # Connect to the database
        cnx = mysql.connect()
        cursor = cnx.cursor()  
        # Get class info from HTTP POST data
        classID = request.form["classID"]
        member = request.form["member"]
        # Add class registration to the database
        query = "INSERT INTO `MemberExerciseSchedule` (`Member`, `ExerciseSchedule`) VALUES (%s, %s);"
        cursor.execute(query, (member, classID))
        cnx.commit()      
        # Close the connection to the database
        cursor.close()
        cnx.close()
        # Display text to user that registration is completed
        # and provide link to go back to Exercise Class Registration page
        return 'Registration complete!<br><a href="/classes/register">Go Back</a>'


# NEW EXERCISE TYPE FORM
@app.route("/classes/new", methods=["GET"])
def new_class():
    # Connect to database
    cnx = mysql.connect()
    cursor = cnx.cursor()
    # Query room info
    cursor.execute("SELECT ID, RoomNumber, BuildingName FROM Room")
    rooms = cursor.fetchall()
    # Query Exercise Types
    cursor.execute("SELECT ID, Name FROM ExerciseType")
    exercises = cursor.fetchall()
    # Query Instructors
    cursor.execute("SELECT ID, Name FROM Instructor")
    instructors = cursor.fetchall()
    # Close connection to the database
    cursor.close()
    cnx.close()
    # Render new class form with room, exercise and instructor data
    return render_template('new_class_form.html', rooms=rooms, exercises=exercises, instructors=instructors)


# EDITING CLASSES
@app.route("/classes/edit", methods=["GET", "POST"])
def edit_class():
    if request.method == "GET":
        # If HTTP GET
        # Connect to the database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Get class ID from HTTP GET data
        classID = request.args["classID"]
        # Query Exercise Schedule
        cursor.execute("SELECT * FROM ExerciseSchedule WHERE ID=%s", classID)
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        exerciseClass = r[0]
        exerciseClass["StartDate"] = exerciseClass["StartTime"].strftime('%Y-%m-%d')
        exerciseClass["StartTime"] = exerciseClass["StartTime"].strftime('%H:%M')
        # Query Rooms
        cursor.execute("SELECT ID, RoomNumber, BuildingName FROM Room")
        rooms = cursor.fetchall()
        # Query Exercise Types
        cursor.execute("SELECT ID, Name FROM ExerciseType")
        exercises = cursor.fetchall()
        # Query Instructors
        cursor.execute("SELECT ID, Name FROM Instructor")
        instructors = cursor.fetchall()
        # Close connection to database
        cursor.close()
        cnx.close()
        # Render edit class form with exercise schedule, rooms, exercise, and instructors
        return render_template('edit_class_form.html', exerciseClass=exerciseClass, rooms=rooms, exercises=exercises, instructors=instructors)
    else:
        # If HTTP POST
        # Connect to database
        cnx = mysql.connect()
        cursor = cnx.cursor()
        # Get class info from HTTP POST data
        classID = request.form["classID"]
        duration = request.form["Duration"]
        start_date = request.form["StartDate"]
        start_time = request.form["StartTime"]
        start_datetime = start_date + ' ' + start_time
        room = request.form["Room"]
        exercise_type = request.form["ExerciseType"]
        instructor = request.form["Instructor"]
        # Edit exercise class schedule entry in the database
        query = "UPDATE `ExerciseSchedule` SET `Duration`=%s, `StartTime`=%s, `Room`=%s, `ExerciseType`=%s, `Instructor`=%s WHERE `ID` = %s"
        cursor.execute(query, (duration, start_datetime, room, exercise_type, instructor, classID))
        cnx.commit()
        # Close the connection to the database
        cursor.close()
        cnx.close()
        # Display to the user that the record has been updated
        # and provide link to go back to Exercise Class Management page
        return 'Record Updated!<br><a href="/classes">Go Back</a>'


# REMOVE EXERCISE CLASS
@app.route("/classes/remove", methods=["GET"])
def remove_class():
    # Connect to the database
    cnx = mysql.connect()
    cursor = cnx.cursor()
    # get Class ID from HTTP GET data
    classID = request.args["classID"]
    # Remove class from database
    query = "DELETE FROM `ExerciseSchedule` WHERE `ID`=%s"
    cursor.execute(query, classID)
    cnx.commit()
    # Close connection to the database
    cursor.close()
    cnx.close()
    # Display to the user that the record has been removed
    # and provide link to go back to Exercise Class Management page
    return 'Record Removed!<br><a href="/classes">Go Back</a>'


if __name__ == '__main__':
 app.run(host='0.0.0.0', port=5000)
