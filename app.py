# ================================================
# app.py — The brain of your entire website
# ================================================

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- Create the Flask app ---
app = Flask(__name__)

# --- Secret key (used for sessions and security) ---
app.config['SECRET_KEY'] = 'myportfolio-secret-key-2024'

# --- Database location ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Connect database and login manager ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

# ================================================
# DATABASE MODELS
# ================================================

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):           return str(self.id)
    def is_authenticated(self): return True
    def is_active(self):        return True
    def is_anonymous(self):     return False

class Project(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack  = db.Column(db.String(200))
    github_url  = db.Column(db.String(200))
    live_url    = db.Column(db.String(200))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class BlogPost(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    published  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ================================================
# USER LOADER
# ================================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================================================
# PUBLIC ROUTES
# ================================================
@app.route('/')
def home():
    projects = Project.query.order_by(Project.created_at.desc()).limit(3).all()
    return render_template('index.html', projects=projects)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=all_projects)

@app.route('/blog')
def blog():
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('blog_post.html', post=post)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        msg = Message(
            name    = request.form['name'],
            email   = request.form['email'],
            content = request.form['message']
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# ================================================
# AUTH ROUTES
# ================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        user = User(
            username      = request.form['username'],
            email         = request.form['email'],
            password_hash = hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# ================================================
# ADMIN ROUTES
# ================================================
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    stats = {
        'projects' : Project.query.count(),
        'posts'    : BlogPost.query.count(),
        'messages' : Message.query.count(),
        'unread'   : Message.query.filter_by(is_read=False).count(),
        'users'    : User.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/projects')
@login_required
def admin_projects():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
@login_required
def admin_add_project():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    if request.method == 'POST':
        p = Project(
            title       = request.form['title'],
            description = request.form['description'],
            tech_stack  = request.form['tech_stack'],
            github_url  = request.form['github_url'],
            live_url    = request.form['live_url']
        )
        db.session.add(p)
        db.session.commit()
        flash('Project added!', 'success')
        return redirect(url_for('admin_projects'))
    return render_template('admin/add_project.html')

@app.route('/admin/projects/delete/<int:id>')
@login_required
def admin_delete_project(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    p = Project.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Project deleted!', 'success')
    return redirect(url_for('admin_projects'))

@app.route('/admin/messages')
@login_required
def admin_messages():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

# ================================================
# REST API
# ================================================
@app.route('/api/projects')
def api_projects():
    projects = Project.query.all()
    return jsonify([{
        'id'          : p.id,
        'title'       : p.title,
        'description' : p.description,
        'tech_stack'  : p.tech_stack,
        'github_url'  : p.github_url
    } for p in projects])

# ================================================
# RUN
# ================================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@portfolio.com').first():
            admin = User(
                username      = 'admin',
                email         = 'admin@portfolio.com',
                password_hash = generate_password_hash('admin123'),
                is_admin      = True
            )
            db.session.add(admin)
            db.session.commit()
            print('=' * 50)
            print('Admin account created!')
            print('Email   : admin@portfolio.com')
            print('Password: admin123')
            print('=' * 50)
    app.run(debug=True)