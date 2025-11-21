from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)


@auth.route('/submit', methods=['POST'])
def submit():
    return "Backend request recieved!"

@auth.route('/map/Nizhny-Novgorod')
def map():
    return render_template("map.html")

@auth.route('/info')
def info():
    return render_template("info.html")

@auth.route('/contacts')
def contacts():
    return render_template("contacts.html")