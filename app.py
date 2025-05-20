from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Review

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

# ===== USER AUTH ROUTES =====

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ===== DASHBOARD =====

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ===== REVIEWS CRUD =====

@app.route('/reviews')
@login_required
def reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    return render_template('reviews.html', reviews=reviews)

@app.route('/reviews/add', methods=['GET', 'POST'])
@login_required
def add_review():
    if request.method == 'POST':
        book_title = request.form['book_title']
        review_text = request.form['review_text']
        new_review = Review(book_title=book_title, review_text=review_text, user_id=current_user.id)
        db.session.add(new_review)
        db.session.commit()
        flash('Review added!', 'success')
        return redirect(url_for('reviews'))
    return render_template('add_review.html')

@app.route('/reviews/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        flash("You can't edit this review.", 'danger')
        return redirect(url_for('reviews'))
    if request.method == 'POST':
        review.book_title = request.form['book_title']
        review.review_text = request.form['review_text']
        db.session.commit()
        flash('Review updated!', 'success')
        return redirect(url_for('reviews'))
    return render_template('edit_review.html', review=review)

@app.route('/reviews/delete/<int:review_id>')
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.author != current_user:
        flash("You can't delete this review.", 'danger')
        return redirect(url_for('reviews'))
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'success')
    return redirect(url_for('reviews'))

# ===== SIMPLE CHATBOT PAGE =====
@app.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    suggestion = ""
    user_input = ""
    if request.method == 'POST':
        user_input = request.form['user_input'].lower()
        # Simple hardcoded suggestions for demo
        if 'fantasy' in user_input:
            suggestion = "You might like 'Harry Potter' by J.K. Rowling."
        elif 'science fiction' in user_input or 'sci-fi' in user_input:
            suggestion = "Try 'Dune' by Frank Herbert."
        elif 'classic' in user_input:
            suggestion = "How about 'To Kill a Mockingbird' by Harper Lee?"
        else:
            suggestion = "Sorry, I don't have a suggestion for that genre yet."

    return render_template('chatbot.html', suggestion=suggestion, user_input=user_input)

if __name__ == '__main__':
    app.run(debug=True)
