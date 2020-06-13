from flask import Flask, request, render_template, session, redirect

import sqlite3
import math
import sys
import pygal
from pygal.style import Style
import time
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Regexp
import requests
import os



app = Flask(__name__)

class ClearHistory(FlaskForm):
    deletehistory = SubmitField("Clear Water Volume History")
    deletedb = SubmitField("Clear ALL Stored Data")
    
class ConfirmDelete(FlaskForm):
    confirm = SubmitField("Confirm")
    cancel = SubmitField("Cancel")
    
class Remote(FlaskForm):
    domain = StringField('Domain  ', validators=[Regexp(r'^[a-z]+\.duckdns\.org$', message="Must be *.duckdns.org")])
    token = StringField('Token  ', validators=[Regexp(r'^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$', message="Must be ********-****-****-****-********** (where * represents 0 to 9 or a to z)")])
    test = SubmitField("Test")
    submit = SubmitField("Use this domain and token")
    
class VertCylinder(FlaskForm):
    height = StringField('Height (A)  ', validators=[Regexp(r'^\d{1,3}(\.\d{1,2})?$', message="Must be a number from 1 to 999.99")])
    diameter = StringField('Diameter (B)  ', validators=[Regexp(r'^\d{1,3}(\.\d{1,2})?$', message="Must be a number from 1 to 999.99")])
    units = SelectField('Units  ', choices=[('metres', 'Metres'), ('inches', 'Inches')])
    calculate = SubmitField("Calculate Volume")
    submit = SubmitField("Use these dimesions")
    
class HorizCylinder(FlaskForm):
    length = StringField('Length (A)  ', validators=[Regexp(r'^\d{1,3}(\.\d{1,2})?$', message="Must be a number from 1 to 999.99")])
    diameter = StringField('Diameter (B)  ', validators=[Regexp(r'^\d{1,3}(\.\d{1,2})?$', message="Must be a number from 1 to 999.99")])
    units = SelectField('Units  ', choices=[('metres', 'Metres'), ('inches', 'Inches')])
    calculate = SubmitField("Calculate Volume")
    submit = SubmitField("Use these dimesions")
    
class Rectangular(FlaskForm):
    height = StringField('Height (A)  ', validators=[Regexp(r'^\d{1,3}(\.\d{1,2})?$', message="Must be a number from 1 to 999.99")])
    length = StringField('Length (B)  ', validators=[Regexp(r'^\d{1,3}(\.\d{1,2})?$', message="Must be a number from 1 to 999.99")])
    width = StringField('Width (C)  ', validators=[Regexp(r'^\d{1,3}(\.\d{1,2})?$', message="Must be a number from 1 to 999.99")])
    units = SelectField('Units  ', choices=[('metres', 'Metres'), ('inches', 'Inches')])
    calculate = SubmitField("Calculate Volume")
    submit = SubmitField("Use these dimesions")
    
@app.route('/ClearHistory', methods=['GET', 'POST'])
def clear_history():
    form = ClearHistory()
    if form.validate_on_submit():
        if form.deletehistory.data:
            return redirect('/ConfirmHistory')
        else: # get the data from db
            return redirect('/ConfirmDbDelete')
    return render_template('ClearHistory.html', form=form)

@app.route('/ConfirmHistory', methods=['GET', 'POST'])
def confirm_history():
    form = ConfirmDelete()
    if form.validate_on_submit():
        if form.confirm.data:
            db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
            cursor = db.cursor()
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Water_Volume_minute' ''')
            if cursor.fetchone()[0]==1 : 
                cursor.execute('''DELETE FROM Water_Volume_minute''')
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Water_Volume_hour' ''')
            if cursor.fetchone()[0]==1 : 
                cursor.execute('''DELETE FROM Water_Volume_hour''')
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Water_Volume_day' ''')
            if cursor.fetchone()[0]==1 : 
                cursor.execute('''DELETE FROM Water_Volume_day''')
            db.commit()
            db.close()
            return redirect('/CurrentVolume')
        else: # get the data from db
            return redirect('/CurrentVolume')
    return render_template('ConfirmHistory.html', form=form)

@app.route('/ConfirmDbDelete', methods=['GET', 'POST'])
def confirm_db_delete():
    form = ConfirmDelete()
    if form.validate_on_submit():
        if form.confirm.data:
            db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
            cursor = db.cursor()
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Water_Volume_minute' ''')
            if cursor.fetchone()[0]==1 : 
                cursor.execute('''DELETE FROM Water_Volume_minute''')
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Water_Volume_hour' ''')
            if cursor.fetchone()[0]==1 : 
                cursor.execute('''DELETE FROM Water_Volume_hour''')
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Water_Volume_day' ''')
            if cursor.fetchone()[0]==1 : 
                cursor.execute('''DELETE FROM Water_Volume_day''')
            cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Water_Volume_params' ''')
            if cursor.fetchone()[0]==1 : 
                cursor.execute('''DELETE FROM Water_Volume_params''')
            db.commit()
            db.close()
            return redirect('/CurrentVolume')
        else: # get the data from db
            return redirect('/CurrentVolume')
    return render_template('ConfirmDbDelete.html', form=form)


@app.route('/Remote', methods=['GET', 'POST'])
def show_remote():
    form = Remote()
    testresult=""
    if form.validate_on_submit():
        domain=form.domain.data
        token=form.token.data
        if form.test.data:
            params = {
            "domains": domain,
            "token": token
            }
            r = requests.get("https://www.duckdns.org/update", params)
            if r.text=="OK":
                testresult="Success"
            else:
                testresult="Failed"
            pass
        elif form.submit.data:
            db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
            cursor = db.cursor()
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('domain', domain))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('token', token)) #everything in cm
            db.commit()
            db.close()
            return redirect('/CurrentVolume')
    else: # get the data from db
        db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "domain"''')
        data=cursor.fetchone()
        if data is None:
            dummy=3
        else:
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "domain"''') 
            form.domain.data=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "token"''')
            form.token.data=cursor.fetchone()[0]
        db.close()
    return render_template('Remote.html', form=form, testresult=testresult)

@app.route('/VertCyl', methods=['GET', 'POST'])
def show_vert():
    form = VertCylinder()
    if form.validate_on_submit():
        shape='VertCyl'
        diameter=float(form.diameter.data)
        height=float(form.height.data) 
        units=form.units.data
        if units=="metres":
            volumeunits="litres"
        else:
            volumeunits="gallons"
        calculatedevolume=int(height * (math.pi * (diameter / 2) * (diameter / 2)) * 1000) #multiply by 1000 to convert cubic metres to litres
        if form.calculate.data:
            pass
        elif form.submit.data:
            db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
            cursor = db.cursor()
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('shape', shape))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('max_water_height', height)) #everything in cm
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('diameter', diameter))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('volume', calculatedevolume))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('units', volumeunits))
            db.commit()
            db.close()
            return redirect('/CurrentVolume')
    else:
        db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "shape"''')
        data=cursor.fetchone()
        if data is None:
            calculatedevolume = ""  #These should be taken from the database
            volumeunits = ""
        elif data[0] == 'VertCyl':
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "max_water_height"''') 
            form.height.data=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "diameter"''')
            form.diameter.data=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "volume"''')
            calculatedevolume=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "units"''')
            volumeunits=cursor.fetchone()[0]
        else:
            calculatedevolume = ""  #These should be taken from the database
            volumeunits = ""
        db.close()
    return render_template('VertCyl.html', form=form, calculatedevolume=calculatedevolume, volumeunits=volumeunits)

@app.route('/HorizCyl', methods=['GET', 'POST'])
def show_horiz():
    form = HorizCylinder()
    if form.validate_on_submit():
        shape='HorizCyl'
        diameter=float(form.diameter.data)
        length=float(form.length.data) 
        units=form.units.data
        if units=="metres":
            volumeunits="litres"
        else:
            volumeunits="gallons"
        L=length
        d=diameter
        Pcyl=((d/2)**2*math.acos(((d/2)-d)/(d/2))-((d/2)-d)*(2*(d/2)*d-d**2)**(0.5))*L
        Pelipt=math.pi/6*d**2*(1.5*d-d)
        calculatedevolume=int((Pcyl+Pelipt) * 1000) #multiply by 1000 to convert cubic metres to litres
        if form.calculate.data:
            pass
        elif form.submit.data:
            db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
            cursor = db.cursor()
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('shape', shape))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('max_water_height', diameter)) #everything in cm
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('length', length))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('volume', calculatedevolume))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('units', volumeunits))
            db.commit()
            db.close()
            return redirect('/CurrentVolume')
    else:
        db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "shape"''')
        data=cursor.fetchone()
        if data is None:
            calculatedevolume = ""  #These should be taken from the database
            volumeunits = ""
        elif data[0] == 'HorizCyl':
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "max_water_height"''') 
            form.diameter .data=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "length"''')
            form.length.data=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "volume"''')
            calculatedevolume=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "units"''')
            volumeunits=cursor.fetchone()[0]
        else:
            calculatedevolume = ""  #These should be taken from the database
            volumeunits = ""
        db.close()
    return render_template('HorizCyl.html', form=form, calculatedevolume=calculatedevolume, volumeunits=volumeunits)
   
    
@app.route('/Rectangle', methods=['GET', 'POST'])
def show_rectangle():
    form = Rectangular()
    if form.validate_on_submit():
        shape='Rectangle'
        height=float(form.height.data) 
        length=float(form.length.data) 
        width=float(form.width.data) 
        units=form.units.data
        if units=="metres":
            volumeunits="litres"
        else:
            volumeunits="gallons"
        calculatedevolume=int(height * length * width * 1000) #multiply by 1000 to convert cubic metres to litres
        if form.calculate.data:
            pass
        elif form.submit.data:
            db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
            cursor = db.cursor()
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('shape', shape))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('max_water_height', height)) #everything in cm
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('length', length))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('width', width))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('volume', calculatedevolume))
            cursor.execute('''REPLACE INTO Water_Volume_params (name, value) VALUES (?,?)''',('units', volumeunits))
            db.commit()
            db.close()
            return redirect('/CurrentVolume')
    else:
        db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "shape"''')
        data=cursor.fetchone()
        if data is None:
            calculatedevolume = ""  #These should be taken from the database
            volumeunits = ""
        elif data[0] == 'Rectangle':
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "max_water_height"''') 
            form.height.data=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "length"''')
            form.length.data=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "width"''')
            form.width.data=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "volume"''')
            calculatedevolume=cursor.fetchone()[0]
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "units"''')
            volumeunits=cursor.fetchone()[0]
        else:
            calculatedevolume = ""  #These should be taken from the database
            volumeunits = ""
        db.close()
    return render_template('Rectangle.html',  form=form, calculatedevolume=calculatedevolume, volumeunits=volumeunits)


@app.route("/", methods=['GET', 'POST'])
@app.route("/CurrentVolume", methods=['GET', 'POST'])
def show_current():
    if session.get('Zoomed') is None:
        session['Zoomed'] = False
        session['Graph']= 'Hour'
        session['ZoomText']="<button type='submit' class='btn btn-primary btn-lg' name='submit_button' value='Zoom in'>Zoom In</button>"
    db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
    cursor = db.cursor()
    cursor.execute("select * from Water_Volume_minute ORDER BY timestamp DESC LIMIT 1")
    volume_data = cursor.fetchone()
    if volume_data is None:
        Volume=0 #default value to use if water tank has not yet been specified
    else:
        Volume=int(volume_data[1])
    cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "units"''') 
    units = cursor.fetchone()
    if units is None:
        displayunits="- (Please define the water cylinder)" #default value to use if water tank has not yet been specified
    else:
        displayunits=units[0]
    db.close()
    return render_template('CurrentVolume.html', CurrentVolume=Volume, Units=displayunits )

@app.route("/Graphs", methods=['GET', 'POST'])
def plot_chart():
    if session.get('Zoomed') is None:
        session['Zoomed'] = False
        session['Graph']= 'Hour'
        session['ZoomText']="<button type='submit' class='btn btn-primary btn-lg' name='submit_button' value='Zoom in'>Zoom In</button>"
    custom_style = Style( title_font_size=26, legend_font_size=26, major_label_font_size=20, label_font_size=20) # was 26
    mychart=pygal.Line(style=custom_style, x_labels_major_every=2, show_minor_x_labels=False, x_label_rotation=25, stroke_style={'width': 5})
    if request.method == 'POST':
        if (request.form['submit_button'] == "Zoom in"):
            session['ZoomText']="<button type='submit' class='btn btn-primary btn-lg' name='submit_button' value='Zoom out'>Zoom Out</button>"
            session['Zoomed'] = True
        elif (request.form['submit_button'] == "Zoom out"):
            session['ZoomText']="<button type='submit' class='btn btn-primary btn-lg' name='submit_button' value='Zoom in'>Zoom In</button>"
            session['Zoomed'] = False
        elif (request.form['submit_button'] == "Last 60 Minutes"):
            session['Graph']= 'Hour'
        elif (request.form['submit_button'] == "Last 24 hours"):
            session['Graph']= 'Day'
        elif (request.form['submit_button'] == "Last 30 days"):
            session['Graph']= 'Month'
    if (session['Zoomed']):            
        mychart.config.range=()
        mychart.title=" (Zoomed in)"
    else:
        db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "shape"''')
        data=cursor.fetchone()
        if data is None:
            range=3000  #default value to store if water tank has not yet been specified
        else:
            cursor.execute('''SELECT value FROM Water_Volume_params WHERE name = "volume"''')
            range=cursor.fetchone()[0]
        db.close()
        mychart.config.range=(0,range)
        mychart.title=""
    if (session['Graph']== 'Hour'):
        recorded_date=[]
        recorded_value=[]
        db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        cursor.execute("select * from Water_Volume_minute")
        chart_data = cursor.fetchall()
        db.close()
        for row in chart_data:
            recorded_date.append(row[0][14:16])
            recorded_value.append(int(row[1]))
        mychart.title="Water Volume During Last 60 Minutes" + mychart.title
        mychart.add('Volume',recorded_value)
        mychart.x_labels = recorded_date
    elif (session['Graph']== 'Day'):
        recorded_date=[]
        recorded_value=[]
        db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        cursor.execute("select * from Water_Volume_hour")
        chart_data = cursor.fetchall()
        db.close()
        for row in chart_data:
            recorded_date.append(row[0][11:13])
            recorded_value.append(int(row[1]))
        mychart.title="Water Volume During Last 24 Hours" + mychart.title
        mychart.add('Volume',recorded_value)
        mychart.x_labels = recorded_date
    else:
        recorded_date=[]
        recorded_value=[]
        db = sqlite3.connect('/home/pi/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        cursor.execute("select * from Water_Volume_day")
        chart_data = cursor.fetchall()
        db.close()
        for row in chart_data:
            recorded_date.append(row[0][0:10])
            recorded_value.append(int(row[1]))
        mychart.title="Water Volume During Last 30 Days" + mychart.title
        mychart.add('Volume',recorded_value)
        mychart.x_labels = recorded_date
    mychart.height=600  #was 600
    mychart.width=1400   #was 1400
    mychart.y_title='Litres'
    mychart.x_title='Time'
    mychart.explicit_size=True
    chart = mychart.render_data_uri()
    return render_template('Graphs.html', ZoomText=session['ZoomText'], chart=chart )

if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run (host='0.0.0.0', port=1445, threaded=True)

