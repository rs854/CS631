from flask import Flask, request
from flask import render_template
from flaskext.mysql import MySQL
import flask
import json
import re
import os
from datetime import date, datetime
import logging, sys

debug = False

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'n17s21o1'
app.config['MYSQL_DATABASE_DB'] = 'NJITFitnessClub'
app.config['MYSQL_DATABASE_HOST'] = 'nma.cqcaflzcpcei.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 33306
mysql.init_app(app)

static = '/var/www/njitFitClub/static/'
templates = '/var/www/njitFitClub/templates/'

if debug:
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'n17s21o1'
    app.config['MYSQL_DATABASE_PORT'] = 3306
    static = './static/'
    templates = './templates/'
else:
    logging.basicConfig(stream=sys.stderr)

@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route("/payroll")
def payroll():
    cnx = mysql.connect()
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM NJITFitnessClub.Instructor")
    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return render_template('payroll.html', instructors=r)


@app.route("/employees/<type>", methods=["GET"])
def new_employee_form(type):
    if type == "salaried":
        return app.send_static_file('new_salaried_employee_form.html')
    else:
        return app.send_static_file('new_hourly_employee_form.html')


@app.route("/employees", methods=["POST"])
def new_employee():
    cnx = mysql.connect()
    cursor = cnx.cursor()

    if request.method == "POST":
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

        query = ""
        if salary:
            query = "INSERT INTO `Instructor` (`Name`, `Salary`) VALUES (%s, %s);"
            cursor.execute(query, (name, salary))
        else:
            query = "INSERT INTO `Instructor` (`Name`, `Wage`, `NumberHoursTaught`) VALUES (%s, %s, %s);"
            cursor.execute(query, (name, wage, numberOfHoursTaught))

        cnx.commit()

    cursor.close()
    cnx.close()

    return 'Employee Added!<br><a href="/payroll">Go Back</a>'


@app.route("/employees/edit", methods=["GET", "POST"])
def edit_employee():
    if request.method == "GET":
        cnx = mysql.connect()
        cursor = cnx.cursor()
        name = request.args["employeeName"]
        cursor.execute("SELECT * FROM NJITFitnessClub.Instructor WHERE Name=%s", name)
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return render_template('edit_employee_form.html', instructor=r[0])
    else:
        cnx = mysql.connect()
        cursor = cnx.cursor()
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

        query = "UPDATE `Instructor` SET `Salary`=%s, `Wage`=%s, `NumberHoursTaught`=%s WHERE `Name` = %s"

        cursor.execute(query, (salary, wage, numberOfHoursTaught, name))
        cnx.commit()
        cursor.close()
        cnx.close()
        return '{} Record Updated!<br><a href="/payroll">Go Back</a>'.format(name)


@app.route("/employees/remove", methods=["GET"])
def remove_employee():

    cnx = mysql.connect()
    cursor = cnx.cursor()

    name = request.args.get('employeeName', '')
    query = "DELETE FROM `Instructor` WHERE `Name`=%s"
    cursor.execute(query, name)
    cnx.commit()

    cursor.close()
    cnx.close()

    return '{} Record Removed!<br><a href="/payroll">Go Back</a>'.format(name)



@app.route("/exercises", methods=["GET", "POST"])
def exercises():
    if request.method == "GET":
        cnx = mysql.connect()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM NJITFitnessClub.ExerciseType")
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return render_template('exercises.html', exercises=r)

    cnx = mysql.connect()
    cursor = cnx.cursor()

    if request.method == "POST":
        name = request.form["Name"]
        description = request.form["Description"]

        if description == "":
            description = "NULL"

        query = "INSERT INTO `ExerciseType` (`Name`, `Description`) VALUES (%s, %s);"

        cursor.execute(query, (name, description))
        cnx.commit()

    cursor.close()
    cnx.close()

    return 'Exercise Added!<br><a href="/exercises">Go Back</a>'


@app.route("/exercises/new", methods=["GET"])
def new_exercise():
    if request.method == "GET":
        return app.send_static_file('new_exercise_form.html')


@app.route("/exercises/edit", methods=["GET", "POST"])
def edit_exercise():
    if request.method == "GET":
        cnx = mysql.connect()
        cursor = cnx.cursor()
        name = request.args["exerciseName"]
        cursor.execute("SELECT * FROM NJITFitnessClub.ExerciseType WHERE Name=%s", name)
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return render_template('edit_exercise_form.html', exercise=r[0])

    cnx = mysql.connect()
    cursor = cnx.cursor()

    if request.method == "POST":
        name = request.form["Name"]
        description = request.form["Description"]

        if description in ["", "None"]:
            description = "NULL"

        query = "UPDATE `ExerciseType` SET `Description`=%s WHERE `Name` = %s"

        cursor.execute(query, (description, name))
        cnx.commit()

    cursor.close()
    cnx.close()

    return '{} Record Updated!<br><a href="/exercises">Go Back</a>'.format(name)


@app.route("/exercises/remove", methods=["GET"])
def remove_exercise():

    cnx = mysql.connect()
    cursor = cnx.cursor()

    name = request.args.get('exerciseName', '')
    query = "DELETE FROM `ExerciseType` WHERE `Name`=%s"
    cursor.execute(query, name)
    cnx.commit()

    cursor.close()
    cnx.close()

    return '{} Record Removed!<br><a href="/exercises">Go Back</a>'.format(name)



@app.route("/classes", methods=["GET", "POST"])
def classes():
    if request.method == "GET":
        cnx = mysql.connect()
        cursor = cnx.cursor()
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
        cursor.close()
        cnx.close()
        return render_template('classes.html', classes=r)

    cnx = mysql.connect()
    cursor = cnx.cursor()

    if request.method == "POST":
        duration = request.form["Duration"]
        start_time = request.form["StartDate"] + " " + request.form["StartTime"]
        room = request.form["Room"]
        exercise_type = request.form["ExerciseType"]
        instructor = request.form["Instructor"]

        query = "INSERT INTO `ExerciseSchedule` (`Duration`, `StartTime`, `Room`, `ExerciseType`, `Instructor`) VALUES (%s, %s, %s, %s, %s);"

        cursor.execute(query, (duration, start_time, room, exercise_type, instructor))
        cnx.commit()

    cursor.close()
    cnx.close()

    return 'Exercise Class Added!<br><a href="/classes">Go Back</a>'

@app.route("/classes/register", methods=["GET", "POST"])
def class_registration():
    if request.method == "GET":
        cnx = mysql.connect()
        cursor = cnx.cursor()
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
        cursor.execute("SELECT * FROM Member")
        m = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return render_template('class_registration.html', classes=r, members=m)
    if request.method == "POST":
        classID = request.form["classID"]
        member = request.form["member"]
        cnx = mysql.connect()
        cursor = cnx.cursor()  
        query = "INSERT INTO `MemberExerciseSchedule` (`Member`, `ExerciseSchedule`) VALUES (%s, %s);"
        cursor.execute(query, (member, classID))
        cnx.commit()      
        cursor.close()
        cnx.close()
        return 'Registration complete!<br><a href="/classes/register">Go Back</a>'


@app.route("/classes/new", methods=["GET"])
def new_class():
    if request.method == "GET":
        cnx = mysql.connect()
        cursor = cnx.cursor()
        cursor.execute("SELECT ID, RoomNumber, BuildingName FROM Room")
        rooms = cursor.fetchall()
        cursor.execute("SELECT ID, Name FROM ExerciseType")
        exercises = cursor.fetchall()
        cursor.execute("SELECT ID, Name FROM Instructor")
        instructors = cursor.fetchall()
        cursor.close()
        cnx.close()
        return render_template('new_class_form.html', rooms=rooms, exercises=exercises, instructors=instructors)


@app.route("/classes/edit", methods=["GET", "POST"])
def edit_class():
    if request.method == "GET":
        cnx = mysql.connect()
        cursor = cnx.cursor()
        classID = request.args["classID"]
        cursor.execute("SELECT * FROM NJITFitnessClub.ExerciseSchedule WHERE ID=%s", classID)
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        exerciseClass = r[0]
        exerciseClass["StartDate"] = exerciseClass["StartTime"].strftime('%Y-%m-%d')
        exerciseClass["StartTime"] = exerciseClass["StartTime"].strftime('%H:%M')
        # start_date = date(start_datetime.year, start_datetime.month, start_datetime.day)
        # start_time = 
        cursor.execute("SELECT ID, RoomNumber, BuildingName FROM Room")
        rooms = cursor.fetchall()
        cursor.execute("SELECT ID, Name FROM ExerciseType")
        exercises = cursor.fetchall()
        cursor.execute("SELECT ID, Name FROM Instructor")
        instructors = cursor.fetchall()
        cursor.close()
        cnx.close()
        return render_template('edit_class_form.html', exerciseClass=exerciseClass, rooms=rooms, exercises=exercises, instructors=instructors)

    cnx = mysql.connect()
    cursor = cnx.cursor()

    if request.method == "POST":
        classID = request.form["classID"]
        duration = request.form["Duration"]
        start_date = request.form["StartDate"]
        start_time = request.form["StartTime"]
        start_datetime = start_date + ' ' + start_time
        room = request.form["Room"]
        exercise_type = request.form["ExerciseType"]
        instructor = request.form["Instructor"]

        query = "UPDATE `ExerciseSchedule` SET `Duration`=%s, `StartTime`=%s, `Room`=%s, `ExerciseType`=%s, `Instructor`=%s WHERE `ID` = %s"

        cursor.execute(query, (duration, start_datetime, room, exercise_type, instructor, classID))
        cnx.commit()

    cursor.close()
    cnx.close()

    return 'Record Updated!<br><a href="/classes">Go Back</a>'


@app.route("/classes/remove", methods=["GET"])
def remove_class():

    cnx = mysql.connect()
    cursor = cnx.cursor()

    classID = request.args["classID"]
    query = "DELETE FROM `ExerciseSchedule` WHERE `ID`=%s"
    cursor.execute(query, classID)
    cnx.commit()

    cursor.close()
    cnx.close()

    return 'Record Removed!<br><a href="/classes">Go Back</a>'





def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


if __name__ == '__main__':
 app.run(host='0.0.0.0', port=5000)
