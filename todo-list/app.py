import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Task

app = Flask(__name__)

# Basic Config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todolist.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Handle Render's PostgreSQL URL issue (if migrating to Postgres later)
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

# Initialize Database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Filtering logic
    filter_type = request.args.get('filter', 'all')
    
    if filter_type == 'completed':
        tasks = Task.query.filter_by(is_completed=True).order_by(Task.created_at.desc()).all()
    elif filter_type == 'pending':
        tasks = Task.query.filter_by(is_completed=False).order_by(Task.created_at.desc()).all()
    else:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        
    return render_template('index.html', tasks=tasks, current_filter=filter_type)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    
    if not title:
        flash('Title is required!', 'danger')
        return redirect(url_for('index'))
    
    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()
    
    flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        flash('Task not found or already deleted.', 'danger')
        return redirect(url_for('index'))
        
    task.is_completed = not task.is_completed
    db.session.commit()
    
    status = "completed" if task.is_completed else "pending"
    flash(f'Task marked as {status}!', 'info')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        flash('Task not found or already deleted.', 'danger')
        return redirect(url_for('index'))
        
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Use environment variables for production readiness
    host = '0.0.0.0'
    port = int(os.environ.get("PORT", 5000))
    app.run(host=host, port=port, debug=False)