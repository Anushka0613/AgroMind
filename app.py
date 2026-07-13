from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import joblib
import os

app = Flask(__name__)

app.secret_key = "smartcrop123"

# ==========================
# Load ML Model
# ==========================

model_path = os.path.join("ml", "crop_model.pkl")
model = joblib.load(model_path)

# ==========================
# Home
# ==========================

@app.route("/")
def home():
    return render_template("index.html")

# ==========================
# Recommend Page
# ==========================

@app.route("/recommend")
def recommend():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("recommend.html")

# ==========================
# Register
# ==========================

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        db_path = os.path.join("database","database.db")

        with sqlite3.connect(db_path, timeout=10) as conn:

            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            )

            user = cursor.fetchone()

            if user:

                return "<h2>Email Already Registered!</h2>"

            cursor.execute(
                """
                INSERT INTO users
                (username,email,password)
                VALUES(?,?,?)
                """,
                (
                    username,
                    email,
                    hashed_password
                )
            )

            conn.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# ==========================
# Login
# ==========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        db_path = os.path.join("database", "database.db")

        with sqlite3.connect(db_path, timeout=10) as conn:

            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            )

            user = cursor.fetchone()

        if user and check_password_hash(user[3], password):

            session["user"] = user[1]

            return redirect(url_for("home"))

        else:

            return "<h2>Invalid Email or Password!</h2>"

    return render_template("login.html")


# ==========================
# Logout
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ==========================
# History
# ==========================

@app.route("/history")
def history():

    if "user" not in session:
        return redirect(url_for("login"))

    db_path = os.path.join("database", "database.db")

    with sqlite3.connect(db_path, timeout=10) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM history ORDER BY id DESC"
        )

        records = cursor.fetchall()

    return render_template(
        "history.html",
        records=records
    )

# ==========================
# Predict Crop
# ==========================

@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return redirect(url_for("login"))

    N = float(request.form["N"])
    P = float(request.form["P"])
    K = float(request.form["K"])
    temperature = float(request.form["temperature"])
    humidity = float(request.form["humidity"])
    ph = float(request.form["ph"])
    rainfall = float(request.form["rainfall"])

    prediction = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])

    crop = prediction[0]

    crop_details = {

        "rice": {
            "category": "🌾 Cereal Crop",
            "description": "Rice grows best in fertile soil with high rainfall."
        },

        "wheat": {
            "category": "🌾 Cereal Crop",
            "description": "Wheat grows well in cool climate."
        },

        "maize": {
            "category": "🌽 Cereal Crop",
            "description": "Maize requires warm weather and moderate rainfall."
        },

        "cotton": {
            "category": "🧵 Cash Crop",
            "description": "Cotton grows best in black soil."
        },

        "banana": {
            "category": "🍌 Fruit Crop",
            "description": "Banana requires high humidity."
        },

        "apple": {
            "category": "🍎 Fruit Crop",
            "description": "Apple grows well in cool regions."
        },

        "orange": {
            "category": "🍊 Fruit Crop",
            "description": "Orange prefers subtropical climates."
        },

        "papaya": {
            "category": "🍈 Fruit Crop",
            "description": "Papaya grows well in tropical climates."
        },

        "mango": {
            "category": "🥭 Fruit Crop",
            "description": "Mango is a popular tropical fruit crop."
        },

        "watermelon": {
            "category": "🍉 Fruit Crop",
            "description": "Watermelon grows well in sandy soil."
        },

        "grapes": {
            "category": "🍇 Fruit Crop",
            "description": "Grapes require warm and dry weather."
        },

        "coffee": {
            "category": "☕ Plantation Crop",
            "description": "Coffee grows well in hilly regions."
        },

        "coconut": {
            "category": "🥥 Plantation Crop",
            "description": "Coconut grows best in coastal regions."
        },

        "jute": {
            "category": "🪢 Fiber Crop",
            "description": "Jute requires high rainfall."
        }

    }

    info = crop_details.get(
        crop.lower(),
        {
            "category": "🌱 Crop",
            "description": "Suitable crop based on the given soil and weather conditions."
        }
    )

    # ==========================
    # Save Prediction
    # ==========================

    db_path = os.path.join("database", "database.db")

    with sqlite3.connect(db_path, timeout=10) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO history
            (crop, N, P, K, temperature, humidity, ph, rainfall)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            crop,
            N,
            P,
            K,
            temperature,
            humidity,
            ph,
            rainfall
        ))

        conn.commit()

    return render_template(
        "result.html",
        crop=crop.title(),
        category=info["category"],
        description=info["description"],
        N=N,
        P=P,
        K=K,
        temperature=temperature,
        humidity=humidity,
        ph=ph,
        rainfall=rainfall,
        accuracy="99.32%"
    )


# ==========================
# Run Flask
# ==========================

if __name__ == "__main__":
    app.run(debug=True)



