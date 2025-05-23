import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from model import db, User, Review

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # change this in production

# Ensure instance folder exists
os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

# Use absolute path for SQLite DB to avoid "unable to open database file" error
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'ai_book_review.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    reviews = Review.query.all()
    return render_template('index.html', reviews=reviews)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


@app.route('/review/add', methods=['GET', 'POST'])
def add_review():
    if 'user_id' not in session:
        flash('Please log in to add a review.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        book_title = request.form['book_title']
        review_text = request.form['review_text']
        rating = int(request.form['rating'])

        new_review = Review(book_title=book_title, review_text=review_text,
                            rating=rating, user_id=session['user_id'])
        db.session.add(new_review)
        db.session.commit()
        flash('Review added!', 'success')
        return redirect(url_for('index'))

    return render_template('add_review.html')


@app.route('/review/edit/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    if 'user_id' not in session:
        flash('Please log in to edit a review.', 'warning')
        return redirect(url_for('login'))

    review = Review.query.get_or_404(review_id)
    if review.user_id != session['user_id']:
        flash('You are not authorized to edit this review.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        review.book_title = request.form['book_title']
        review.review_text = request.form['review_text']
        review.rating = int(request.form['rating'])
        db.session.commit()
        flash('Review updated!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_review.html', review=review)


@app.route('/review/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if 'user_id' not in session:
        flash('Please log in to delete a review.', 'warning')
        return redirect(url_for('login'))

    review = Review.query.get_or_404(review_id)
    if review.user_id != session['user_id']:
        flash('You are not authorized to delete this review.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(review)
    db.session.commit()
    flash('Review deleted!', 'success')
    return redirect(url_for('index'))


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_message = request.json.get('message').lower()

        # Simple hardcoded book suggestions based on keywords
        if "fantasy" in user_message:
            reply = "Try these fantasy books: 'Harry Potter', 'The Hobbit', 'Game of Thrones'."
        elif "science" in user_message:
            reply = "You might like: 'A Brief History of Time', 'Cosmos', 'The Martian'."
        elif "romance" in user_message:
            reply = "Check out: 'Pride and Prejudice', 'The Notebook', 'Outlander'."
        else:
            reply = "Here are some popular books: 'To Kill a Mockingbird', '1984', 'The Great Gatsby'."

        return jsonify({'response': reply})
    return render_template('chatbot.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
