from flask import Flask, request, render_template, session

import sqlite3
import sys
sys.path.insert(1,"/usr/lib/python2.7/dist-packages")
import pygal
from pygal.style import Style

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def plot_chart():
    if request.method == 'GET':
        session['Zoomed'] = False
        session['Graph']= 'Hour'
        session['ZoomText']="<button type='submit' class='btn btn-primary btn-lg' name='submit_button' value='Zoom in'>Zoom In</button>"
        return render_template("main.html", ZoomText=session['ZoomText'], title=None)
    if request.method == 'POST':
        db = sqlite3.connect('/home/pi/web-server/volume.db')      #open database - create it if it doesn't exist
        cursor = db.cursor()
        custom_style = Style(title_font_size=26, legend_font_size=26, lable_font_size=26)
        mychart=pygal.Line(style=custom_style, stroke_style={'width': 5})
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
            mychart.config.range=(0,3000)
            mychart.title=""
        if (session['Graph']== 'Hour'):
            recorded_date=[]
            recorded_value=[]
            cursor.execute("select * from Water_Volume_minute")
            chart_data = cursor.fetchall()
            for row in chart_data:
                recorded_date.append(row[0][14:16])
                recorded_value.append(int(row[1]))
            mychart.title="Water Volume During Last 60 Minutes" + mychart.title
            mychart.add('Volume',recorded_value)
            mychart.x_labels = recorded_date
        elif (session['Graph']== 'Day'):
            recorded_date=[]
            recorded_value=[]
            cursor.execute("select * from Water_Volume_hour")
            chart_data = cursor.fetchall()
            for row in chart_data:
                recorded_date.append(row[0][11:16])
                recorded_value.append(int(row[1]))
            mychart.title="Water Volume During Last 24 Hours" + mychart.title
            mychart.add('Volume',recorded_value)
            mychart.x_labels = recorded_date
        else:
            recorded_date=[]
            recorded_value=[]
            cursor.execute("select * from Water_Volume_day")
            chart_data = cursor.fetchall()
            for row in chart_data:
                recorded_date.append(row[0][0:10])
                recorded_value.append(int(row[1]))
            mychart.title="Water Volume During Last 30 Days" + mychart.title
            mychart.add('Volume',recorded_value)
            mychart.x_labels = recorded_date
        mychart.height=600
        mychart.width=1400
        mychart.y_title='Litres'
        mychart.x_title='Time'
        mychart.explicit_size=True
        chart = mychart.render(is_unicode=True)
        return render_template('main.html', ZoomText=session['ZoomText'], chart=chart )

if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run (host='10.0.0.60', port=1445)

