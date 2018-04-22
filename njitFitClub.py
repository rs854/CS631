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
    logging.info(query)

    cursor.execute(query)
    cnx.commit()
    cursor.close()
    cnx.close()

    return "Employee Added"


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


if __name__ == '__main__':
 app.run(host='0.0.0.0', port=5000)
