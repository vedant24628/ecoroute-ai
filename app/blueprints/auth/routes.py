from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Admin, Society, Worker
from app.blueprints.auth.forms import LoginForm, RegisterSocietyForm
from app.services.mail_service import send_registration_received_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for('admin.dashboard'))
        elif isinstance(current_user, Society):
            return redirect(url_for('society.dashboard'))
        elif isinstance(current_user, Worker):
            return redirect(url_for('worker.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data
        role = form.role.data

        user = None
        if role == 'admin':
            user = Admin.query.filter_by(email=email).first()
        elif role == 'society':
            user = Society.query.filter_by(email=email).first()
        elif role == 'worker':
            user = Worker.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if role == 'society' and user.status == 'PENDING':
                flash('Your society registration is still pending Super Admin approval. Please check back soon.', 'warning')
                return render_template('auth/login.html', form=form)

            login_user(user)
            flash(f'Welcome back, {getattr(user, "full_name", getattr(user, "secretary_name", "User"))}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'society':
                return redirect(url_for('society.dashboard'))
            elif role == 'worker':
                return redirect(url_for('worker.dashboard'))
        else:
            flash('Invalid email, password, or selected role.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register-society', methods=['GET', 'POST'])
def register_society():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterSocietyForm()
    if form.validate_on_submit():
        existing_reg = Society.query.filter_by(registration_number=form.registration_number.data).first()
        existing_email = Society.query.filter_by(email=form.email.data).first()

        if existing_reg:
            flash('A society with this registration number already exists.', 'warning')
            return render_template('auth/register_society.html', form=form)
        if existing_email:
            flash('This email address is already registered.', 'warning')
            return render_template('auth/register_society.html', form=form)

        new_society = Society(
            society_name=form.society_name.data,
            registration_number=form.registration_number.data,
            secretary_name=form.secretary_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            landmark=form.landmark.data,
            city=form.city.data,
            state=form.state.data,
            pin_code=form.pin_code.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            num_buildings=form.num_buildings.data,
            num_wings=form.num_wings.data,
            num_flats=form.num_flats.data,
            total_residents=form.total_residents.data,
            estimated_daily_waste=form.estimated_daily_waste.data,
            preferred_pickup_time=form.preferred_pickup_time.data,
            status='PENDING'
        )
        new_society.set_password(form.password.data)
        db.session.add(new_society)
        db.session.commit()

        mail_sent = send_registration_received_email(new_society)
        if mail_sent:
            flash('Society registered successfully! A confirmation email has been sent, and your account is pending Super Admin approval.', 'success')
        else:
            flash('Society registered successfully! Your account is pending Super Admin approval. (We could not send a confirmation email - please check the mail configuration.)', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_society.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')
