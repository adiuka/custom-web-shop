from flask import Flask, render_template, redirect, url_for, flash, abort, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey, Numeric, Float, DateTime
from typing import List
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from forms import ItemForm, RegisterForm, LoginForm
import os
import json
import stripe
from datetime import datetime


class Base(DeclarativeBase):
    pass


# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['CKEDITOR_PKG_TYPE'] = 'standard'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///items.db"
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ckeditor = CKEditor(app)
Bootstrap5(app)


# --- Log-In Manager ---
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# --- Models and DB management ---
class Category(db.Model):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    items: Mapped[list["Item"]] = relationship(back_populates="category")


class Item(db.Model):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2)) # Keep your local price for display/logic
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="items")
    stripe_price_id: Mapped[str | None] = mapped_column(String, nullable=True)
    

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    orders: Mapped[List["Order"]] = relationship(back_populates="user")


class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    items: Mapped[str] = mapped_column(Text, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user: Mapped["User"] = relationship(back_populates="orders")
    

# --- Cart Management ---
YOUR_DOMAIN = "http://127.0.0.1:5000"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    cart = session.get("cart", {})
    line_items = []

    for item_id, quantity in cart.items():
        item = db.get_or_404(Item, item_id)
        if not item.stripe_price_id:
            continue  # skip if no Stripe price
        line_items.append({
            'price': item.stripe_price_id,
            'quantity': quantity,
        })

    try:
        session_obj = stripe.checkout.Session.create(
            ui_mode='embedded',
            line_items=line_items,
            mode='payment',
            return_url=YOUR_DOMAIN + '/return?session_id={CHECKOUT_SESSION_ID}',
            shipping_address_collection={'allowed_countries': ['DK']}
        )
        return jsonify(clientSecret=session_obj.client_secret)
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.route('/session-status', methods=['GET'])
def session_status():
    session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
    return jsonify(status=session.status, customer_email=session.customer_details.email)


@app.route("/add-to-cart/<int:item_id>")
def add_to_cart(item_id):
    cart = session.get("cart", {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    session["cart"] = cart
    flash("Item added to cart!")
    return redirect(url_for("render_home"))


@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    items = []
    total = 0

    for item_id, quantity in cart.items():
        item = db.get_or_404(Item, item_id)
        item.quantity = quantity
        item.subtotal = float(item.price) * quantity
        total += item.subtotal
        items.append(item)

    return render_template("cart.html", items=items, total=total)


@app.route('/update-cart', methods=['POST'])
def update_cart():
    item_id = request.form['item_id']
    action = request.form['action']

    cart = session.get('cart', {})

    if item_id in cart:
        if action == 'increase':
            cart[item_id] += 1
        elif action == 'decrease':
            cart[item_id] -= 1
            if cart[item_id] <= 0:
                del cart[item_id]
    session['cart'] = cart
    return redirect(url_for('view_cart'))
  

@app.route('/checkout')
def show_checkout():
    stripe_public_key = os.environ.get('STRIPE_PUBLIC_KEY')
    return render_template('checkout.html', stripe_public_key=stripe_public_key)


@app.route('/return')
def show_return():
    total = 0
    if 'cart' in session and current_user.is_authenticated:
        cart = session.get("cart", {})
        
        for item_id, quantity in cart.items():
            item = db.get_or_404(Item, item_id)
            item.quantity = quantity
            item.subtotal = float(item.price) * quantity
            total += item.subtotal

        order = Order(
            user_id=current_user.id,
            items=json.dumps(cart),
            total_price=total
        )
        db.session.add(order)
        db.session.commit()

    session.pop("cart", None)
    return render_template('return.html')


# --- Site Functionality ---
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs) 
    return decorated_function


@app.route('/')
def render_home():
    result = db.session.execute(db.select(Item))
    items = result.scalars().all()
    return render_template('index.html', items=items)


@app.route('/add-item', methods=['GET', 'POST'])
@admin_only
def add_item():
    form = ItemForm()
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]
    if form.validate_on_submit():
        new_item = Item(
            name=form.name.data,
            body=form.body.data,
            img_url=form.photo_link.data,
            category_id=form.category_id.data,
            stripe_price_id=form.stripe_price_id.data,
            price=form.price.data
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('render_home'))
    return render_template('add_item.html', form=form)


@app.route("/item/<int:item_id>", methods=["GET", "POST"])
def show_item(item_id):
    requested_item = db.get_or_404(Item, item_id)

    return render_template("item.html", item=requested_item)


# --- User Handling ---
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            flash("That email already has an account, try loging in")
            return redirect(url_for('login'))
        hashed_pass = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=hashed_pass
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('render_home'))
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter(Order.user_id == current_user.id).order_by(Order.date.desc()).all()
    return render_template('my_orders.html', orders=orders)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('render_home'))
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not Category.query.first():
            db.session.add(Category(name="Clothing", 
                                    description="All kinds of Clothes",
                                    ))
            db.session.commit()
    app.run(debug=True)
