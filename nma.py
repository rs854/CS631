from flask import Flask
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
app.config['MYSQL_DATABASE_DB'] = 'nma'
app.config['MYSQL_DATABASE_HOST'] = 'nma.cqcaflzcpcei.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_PORT'] = 33306
mysql.init_app(app)

static = '/var/www/nma/static/'
templates = '/var/www/nma/templates/'

@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route("/patients")
def patients():
    return app.send_static_file('patients.html')


@app.route("/patient/<name>")
def display_patient(name):
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from Patients WHERE Name='%s'".format(name))
    r = [dict((re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', cur.description[i][0]), value)
          for i, value in enumerate(row)) for row in cur.fetchall()]
    row = cursor.fetchone()
    return render_template('patient_list.html', patients=r)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


if __name__ == '__main__':
 app.run(host='0.0.0.0', port=5000)
