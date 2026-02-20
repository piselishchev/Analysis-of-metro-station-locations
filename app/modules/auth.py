from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)


@auth.route('/submit')
def submit_page():
    return "Backend request recieved!"

@auth.route('/map/Nizhny-Novgorod')
def map_page():
    return render_template("map.html")

@auth.route('/info')
def info_page():
    return render_template("info.html")

@auth.route('/contacts')
def contacts_page():
    return render_template("contacts.html")