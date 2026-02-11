from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home_page():
    return render_template("home.html")