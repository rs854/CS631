from flask import Flask, request
from flask import render_template
from flaskext.mysql import MySQL
import flask
import json
import re
import os
from datetime import date, datetime
import logging, sys
logging.basicConfig(stream=sys.stderr)

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


@app.route("/employees", methods=["GET", "POST"])
def new_employee():
    if request.method == "GET":
        return app.send_static_file('new_employee_form.html')

    cnx = mysql.connect()
    cursor = cnx.cursor()

    if request.method == "POST":
        name = request.form["Name"]
        salary = request.form["Salary"]
        wage = request.form["Wage"]
        numberOfHoursTaught = request.form["NumberHoursTaught"]

        if salary == "":
            salary = "NULL"

        if wage == "":
            wage = "NULL"

        if numberOfHoursTaught == "":
            numberOfHoursTaught = "NULL"

        query = "INSERT INTO `Instructor` (`Name`, `Salary`, `Wage`, `NumberHoursTaught`) VALUES ('{}', {}, {}, {});".format(name, salary, wage, numberOfHoursTaught)

        cursor.execute(query)
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
        cursor.execute("SELECT * FROM NJITFitnessClub.Instructor WHERE Name='{}'".format(name))
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return render_template('edit_employee_form.html', instructor=r[0])

    cnx = mysql.connect()
    cursor = cnx.cursor()

    if request.method == "POST":
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

        query = "UPDATE `Instructor` SET `Salary`={}, `Wage`={}, `NumberHoursTaught`={} WHERE `Name` = '{}'".format(salary, wage, numberOfHoursTaught, name)

        cursor.execute(query)
        cnx.commit()

    cursor.close()
    cnx.close()

    return '{} Record Updated!<br><a href="/payroll">Go Back</a>'.format(name)


@app.route("/employees/remove", methods=["GET"])
def remove_employee():

    cnx = mysql.connect()
    cursor = cnx.cursor()

    name = request.args.get('employeeName', '')
    query = "DELETE FROM `Instructor` WHERE `Name`='{}'".format(name)
    cursor.execute(query)
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

        query = "INSERT INTO `ExerciseType` (`Name`, `Description`) VALUES ('{}', '{}');".format(name, description)

        cursor.execute(query)
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
        cursor.execute("SELECT * FROM NJITFitnessClub.ExerciseType WHERE Name='{}'".format(name))
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

        query = "UPDATE `ExerciseType` SET `Description`='{}' WHERE `Name` = '{}'".format(description, name)

        cursor.execute(query)
        cnx.commit()

    cursor.close()
    cnx.close()

    return '{} Record Updated!<br><a href="/exercises">Go Back</a>'.format(name)


@app.route("/exercises/remove", methods=["GET"])
def remove_exercise():

    cnx = mysql.connect()
    cursor = cnx.cursor()

    name = request.args.get('exerciseName', '')
    query = "DELETE FROM `ExerciseType` WHERE `Name`='{}'".format(name)
    cursor.execute(query)
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
        start_time = request.form["StartTime"]
        room = request.form["Room"]
        exercise_type = request.form["ExerciseType"]
        instructor = request.form["Instructor"]

        query = "INSERT INTO `ExerciseSchedule` (`Duration`, `StartTime`, `Room`, `ExerciseType`, `Instructor`) VALUES ({}, '{}', {}, {}, {});".format(duration, start_time, room, exercise_type, instructor)

        cursor.execute(query)
        cnx.commit()

    cursor.close()
    cnx.close()

    return 'Exercise Class Added!<br><a href="/classes">Go Back</a>'


@app.route("/classes/new", methods=["GET"])
def new_class():
    if request.method == "GET":
        return app.send_static_file('new_class_form.html')


@app.route("/classes/edit", methods=["GET", "POST"])
def edit_class():
    if request.method == "GET":
        cnx = mysql.connect()
        cursor = cnx.cursor()
        classID = request.args["classID"]
        cursor.execute("SELECT * FROM NJITFitnessClub.ExerciseSchedule WHERE ID={}".format(classID))
        r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return render_template('edit_class_form.html', exerciseClass=r[0])

    cnx = mysql.connect()
    cursor = cnx.cursor()

    if request.method == "POST":
        classID = request.form["ClassID"]
        duration = request.form["Duration"]
        start_time = request.form["StartTime"]
        logging.error(start_time)
        room = request.form["Room"]
        exercise_type = request.form["ExerciseType"]
        instructor = request.form["Instructor"]

        query = "UPDATE `ExerciseSchedule` SET `Duration`={}, `Room`={}, `ExerciseType`={}, `Instructor`={} WHERE `ID` = {}".format(duration, room, exercise_type, instructor, classID)

        cursor.execute(query)
        cnx.commit()

    cursor.close()
    cnx.close()

    return 'Record Updated!<br><a href="/classes">Go Back</a>'


@app.route("/classes/remove", methods=["GET"])
def remove_class():

    cnx = mysql.connect()
    cursor = cnx.cursor()

    classID = request.args["classID"]
    query = "DELETE FROM `ExerciseSchedule` WHERE `ID`={}".format(classID)
    cursor.execute(query)
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
