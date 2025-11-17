from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import TaiKhoan, db
from .forms import ChangePasswordForm

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        user = TaiKhoan.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Sai thông tin", "danger")
            return redirect(url_for("auth.login"))
        login_user(user)
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if check_password_hash(user.password_hash, form.old_password.data):
            user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Đổi mật khẩu thành công!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Mật khẩu hiện tại không đúng.", "danger")
    return render_template("change_password.html", form=form)