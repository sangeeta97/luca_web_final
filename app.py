from flask import Flask
from flask import request
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import os
import json
import time
from flask import render_template
import pandas as pd
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
import sys


context= {'extra': False,  'filename': False}




app = Flask(__name__)
bootstrap = Bootstrap(app)


def unzip(path2):
    from zipfile import ZipFile
    path3 = os.path.join(path, "upload", "file")
    with ZipFile(path2, 'r') as zObject:
        zObject.extractall(path=path3)
    return path3


def analysis(path3, name):
    import os
    from shutil import make_archive
    if name:
        kk = os.system(f'Rscript Freestyle_parser.R -r {path3} -a annotation_db.csv -c config_file_adducts.csv -o res_toy')
        if not kk:
            current_dir = os.getcwd()
            path4 = os.path.join(current_dir, "res_toy")
            make_archive("result", 'zip', path4)
    if not name:
        print(f'Rscript Freestyle_parser.R -r {path3} -a annotation_db.csv -c config_file.csv -o res_toy')
        kk = os.system(f'Rscript Freestyle_parser.R -r {path3} -a ./annotation_db.csv -c ./config_file.csv -o ./res_toy')
        if not kk:
            current_dir = os.getcwd()
            path4 = os.path.join(current_dir, "res_toy")
            make_archive("result", 'zip', path4)




@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        name = request.form['name']
        file = request.files['file']
        filename = file.filename
        print(filename)
        file.save(f"upload/{filename}")
        path3 = os.path.join(os.getcwd(), "upload", filename)
        print(path3)
        last = filename.split(".")[-1]
        first = filename.split(".")[0]
        first = first.replace(" ", "_")
        if last == "zip":
            print("yes")
            import shutil
            if not os.path.exists(os.path.join(os.getcwd(), "upload", f'{first}')):
                os.mkdir(os.path.join(os.getcwd(), "upload", f'{first}'))
            path_zip = os.path.join(os.getcwd(), "upload", filename)
            path3 = os.path.join(os.getcwd(), "upload", f'{first}')
            print(path_zip)
            shutil.unpack_archive(path_zip, path3)
        else:
            os.rename(path3, os.path.join(os.getcwd(), "upload", f'{first}.{last}'))
            path3 = os.path.join(os.getcwd(), "upload", f'{first}.{last}')
        analysis(path3, name)
        context["filename"] = "yes"
        context["extra"] = name
        return render_template("button2.html", filename= context['filename'],  extra= context['extra'])
    return render_template("button2.html", context= context)





@app.route('/download', methods=['GET'])
def download():
    # path = os.path.join(os.getcwd(), "result.zip")
    return send_from_directory(os.getcwd(), path = "result.zip", as_attachment=True)





if __name__ == '__main__':
    app.debug = True
    app.run()
