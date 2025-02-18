from flask import Flask ,redirect,render_template,request,url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask import Flask, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from .forms import *
import numpy as np
import os
from sqlalchemy import update
from flask import jsonify
import numpy as np
import pandas as pd
from flask import send_file, send_from_directory
from .model import User
import datetime
from . import app
from . import db


basedir = os.path.abspath(os.path.dirname(__file__))


context = {"name": None, "email": None, "ppms": None, "pdb": None, "docking_type": None, "pocket_size": None, "smiles": None, "random": None, 'extra': False,  'filename': False}






def randomString():
        ALPHABET = np.array(list('abcdefghijklmnopqrstuvwxyz0123456789'))
        stringArray = np.random.choice(ALPHABET, size=10)
        outString = ""
        return outString.join(stringArray)



@app.route('/', methods=['POST', 'GET'])
def home_page():
    form = ItemForm()
    if form.validate_on_submit():
        name = request.form['name']
        email = request.form['email']
        ppms = request.form['ppms']
        docking_type = request.form['docking_type']
        smiles = request.form["smiles"]
        uniquestr1 = randomString()
        path_folder = os.path.join(app.config['UPLOADS'], uniquestr1)
        os.mkdir(path_folder)
        path_file = os.path.join(path_folder, "smiles.txt")
        f = open(path_file, "a")
        f.write(smiles)
        f.close()
        pocket_size = request.form['pocket_size']
        ppms = request.form['ppms']
        f = form.pdb.data
        filename = secure_filename(f.filename)
        path_file = os.path.join(path_folder, filename)
        f.save(path_file)
        message = flash(f"The data for user {name} has been submitted.")
        context["email"] = email
        context["name"] = name
        context["ppms"] = ppms
        context["docking_type"] = docking_type
        context["pdb"] = filename
        context["smiles"] = smiles
        context["pocket_size"] = pocket_size
        now = datetime.datetime.now()
        now = str(now)
        db.create_all()
        record = User(name, email, ppms, docking_type, filename, uniquestr1, pocket_size, now)
        # Flask-SQLAlchemy magic adds record to database
        db.session.add(record)
        db.session.commit()
        kk = os.system("python3 /home/sangeetakumari/grapes/grapes/alphaapp/alpha/alpha/mailtry.py")

        message = flash(f"The data for user {name} for analysis has been submitted.")
        return render_template('last.html', context = context)
    return render_template('home.html', form= form)



@app.route('/input/<string:uniquestr>')
def inputload_page(uniquestr):
    path1 = os.path.join(basedir, "uploads", uniquestr)
    path2 = os.path.join(basedir, "uploads")
    from shutil import make_archive
    make_archive(path1, 'zip', path1)
    return send_file(os.path.join(path2, f"{uniquestr}.zip"),
                            as_attachment=True)



@app.route('/docking/database')
def database():
    trick = User.query.all()
    email= [u.email for u in trick]
    name = [u.name for u in trick]
    ppms = [u.ppms for u in trick]
    docking_type = [u.docking_type for u in trick]
    pdb = [u.pdb for u in trick]
    pocket_size = [u.pocket_size for u in trick]
    uniquestr= [u.uniquestr for u in trick]
    name= [u.name for u in trick]
    table= {"email": email, "name": name, "ppms": ppms, "docking_type": docking_type, "pdb": pdb, "pocket_size": pocket_size, "uniquestr": uniquestr}
    return jsonify(table)




def unzip(path2):
    from zipfile import ZipFile
    path3 = os.path.join(path, "upload", "file")
    with ZipFile(path2, 'r') as zObject:
        zObject.extractall(path=path3)
    return path3


def analysis(filename):
    import os
    from shutil import make_archive
    kk = os.system(f'sudo docker run -it --rm -v /home/sangeeta/Documents/docking_amazon-main/dock:/app/parser sangeeta97/parser Rscript /app/parser/Freestyle_parser.R -r /app/parser/uploads/{filename} -a /app/parser/uploads/annotation_db.csv -c /app/parser/uploads/config_file.csv -o /app/parser/res_toy')
    if not kk:

        path4 = os.path.join(basedir, "res_toy")
        make_archive("result", 'zip', path4)



@app.route('/parser', methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        name = request.form['name']
        tolerance_value = request.form['tolerance_value']
        mass_range = request.form['mass_range']
        modification_name = request.form['modification_mass']
        modification_mass = request.form['modification_mass']
        IgG = request.form['IgG']
        IgM_site1 = request.form['IgM_site1']
        IgM_site4 = request.form['IgM_site4']
        Aflibercept_site1 = request.form['Aflibercept_site1']
        IgGFc = request.form['IgGFc']
        file2 = request.files['file2']
        file2name = "annotation_db.csv"
        file2.save(file2name)
        file = request.files['file']
        filename = file.filename
        print(filename)
        last = filename.split(".")[-1]
        first = filename.split(".")[0]
        first = first.replace(" ", "_")
        file.save(os.path.join(basedir, "uploads", f"{first}.{last}"))
        filename = first + "." + last
        import csv
        data = [['tolerance_value', tolerance_value],
            ['mass_range', mass_range],
            ['modification_name', modification_name],
            ['modification_mass', modification_mass],
            ['IgG', IgG],
            ['IgM_site1', IgM_site1],
            ['IgM_site4', IgM_site4],
            ['Aflibercept_site1', Aflibercept_site1],
            ['IgGFc', IgGFc],

            ]
        # Writing data to a CSV file
        with open('config_file.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        path3 = os.path.join(basedir, "uploads", f"{first}.{last}")
        print(path3)
        if last == "zip":
            print("yes")
            import shutil
            if not os.path.exists(os.path.join(basedir, "uploads", f'{first}')):
                os.mkdir(os.path.join(basedir, "uploads", f'{first}'))
            path_zip = os.path.join(basedir, "uploads", filename)
            path3 = os.path.join(basedir, "uploads", f'{first}')
            print(path_zip)
            shutil.unpack_archive(path_zip, path3)
        else:
            os.rename(path3, os.path.join(basedir, "uploads", f'{first}.{last}'))
            path3 = os.path.join(basedir, "uploads", f'{first}.{last}')
        analysis(filename)
        context["filename"] = "yes"
        context["extra"] = name
        return render_template("button2.html", filename= context['filename'],  extra= context['extra'])
    return render_template("button2.html", context= context)





@app.route('/parser/download', methods=['GET'])
def download():
    # path = os.path.join(os.getcwd(), "result.zip")
    return send_from_directory(basedir, path = "result.zip", as_attachment=True)
