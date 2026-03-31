from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home_page():
    return render_template("home.html", background_image="home.png")

@views.route('/info')
def info_page():
    return render_template("info.html", background_image="info.png")

@views.route('/contacts')
def contacts_page():
    return render_template("contacts.html", background_image="contacts.png")
