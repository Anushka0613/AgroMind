from flask import Flask, render_template, request, redirect, url_for, session, flash

from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3
import joblib
import os
import requests

from openai import OpenAI

from flask_babel import Babel, gettext




# ====================================
# Flask App Setup
# ====================================
app = Flask(__name__)
app.secret_key = "smartcrop123"

#multilingual support

app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

def get_locale():
    return session.get("language", "en")

babel = Babel(app, locale_selector=get_locale)

    




# ====================================
# OpenWeather API
# ====================================

WEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"



# ====================================
# OpenAI API
# ====================================

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"


client = OpenAI(
    api_key=OPENAI_API_KEY
)



# ====================================
# Load Machine Learning Model
# ====================================

model_path = os.path.join(
    "ml",
    "crop_model.pkl"
)


model = joblib.load(model_path)
# ====================================
# Home Page
# ====================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        _=gettext
    )



# ====================================
# Recommendation Page
# ====================================

@app.route("/recommend")
def recommend():

    if "user" not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "recommend.html",
        _=gettext
    )



# ====================================
# Register
# ====================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():


    if request.method == "POST":


        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]



        hashed_password = generate_password_hash(
            password
        )



        db_path = os.path.join(
            "database",
            "database.db"
        )



        with sqlite3.connect(
            db_path,
            timeout=10
        ) as conn:


            cursor = conn.cursor()



            cursor.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            )


            user = cursor.fetchone()



            if user:


                flash(
                    "Email already registered!",
                    "danger"
                )


                return redirect(
                    url_for("register")
                )



            cursor.execute(
                """
                INSERT INTO users
                (username,email,password)
                VALUES (?,?,?)
                """,
                (
                    username,
                    email,
                    hashed_password
                )
            )


            conn.commit()



        flash(
            "Registration Successful! Please Login.",
            "success"
        )


        return redirect(
            url_for("login")
        )



    return render_template(
        "register.html",
        _=gettext
    )



# ====================================
# Login
# ====================================

@app.route(
    "/login",
    methods=["GET","POST"]
)

def login():


    if request.method == "POST":


        email = request.form["email"]

        password = request.form["password"]



        db_path = os.path.join(
            "database",
            "database.db"
        )



        with sqlite3.connect(
            db_path,
            timeout=10
        ) as conn:


            cursor = conn.cursor()


            cursor.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            )


            user = cursor.fetchone()



        if user and check_password_hash(
            user[3],
            password
        ):


            session["user"] = user[1]


            flash(
                "Login Successful!",
                "success"
            )


            return redirect(
                url_for("home")
            )


        else:


            flash(
                "Invalid Email or Password!",
                "danger"
            )


            return redirect(
                url_for("login")
            )



    return render_template(
        "login.html",
        _=gettext
    )



# ====================================
# Logout
# ====================================

@app.route("/logout")

def logout():


    session.clear()


    flash(
        "Logged out successfully.",
        "info"
    )


    return redirect(
        url_for("login")
    )
# ====================================
# Prediction History
# ====================================

@app.route("/history")

def history():


    if "user" not in session:


        flash(
            "Please login first.",
            "warning"
        )


        return redirect(
            url_for("login")
        )



    db_path = os.path.join(
        "database",
        "database.db"
    )



    with sqlite3.connect(
        db_path,
        timeout=10
    ) as conn:


        conn.row_factory = sqlite3.Row


        cursor = conn.cursor()



        cursor.execute(
            "SELECT * FROM history ORDER BY id DESC"
        )


        records = cursor.fetchall()



    return render_template(
        "history.html",
        records=records,
        _=gettext
    )





# ====================================
# Predict Crop
# ====================================

@app.route(
    "/predict",
    methods=["POST"]
)

def predict():


    if "user" not in session:


        flash(
            "Please login first.",
            "warning"
        )


        return redirect(
            url_for("login")
        )



    N = float(
        request.form["N"]
    )


    P = float(
        request.form["P"]
    )


    K = float(
        request.form["K"]
    )


    temperature = float(
        request.form["temperature"]
    )


    humidity = float(
        request.form["humidity"]
    )


    ph = float(
        request.form["ph"]
    )


    rainfall = float(
        request.form["rainfall"]
    )



    prediction = model.predict(
        [[
            N,
            P,
            K,
            temperature,
            humidity,
            ph,
            rainfall
        ]]
    )



    crop = prediction[0]





    # ====================================
    # Crop Details
    # ====================================


    crop_details = {


        "rice": {


            "category":
            "🌾 Cereal Crop",


            "description":
            "Rice grows best in fertile soil with high rainfall.",


            "fertilizer":[

                "Urea",

                "DAP",

                "MOP (Potash)"

            ],


            "dosage":{


                "Urea":
                "120 kg/hectare",


                "DAP":
                "60 kg/hectare",


                "MOP (Potash)":
                "40 kg/hectare"

            }

        },



        "wheat":{


            "category":
            "🌾 Cereal Crop",


            "description":
            "Wheat grows well in cool climate.",


            "fertilizer":[

                "Urea",

                "DAP",

                "Potash"

            ],


            "dosage":{


                "Urea":
                "100 kg/hectare",


                "DAP":
                "50 kg/hectare",


                "Potash":
                "40 kg/hectare"

            }

        },



        "maize":{


            "category":
            "🌽 Cereal Crop",


            "description":
            "Maize requires warm weather.",


            "fertilizer":[

                "Urea",

                "NPK 20:20:0",

                "Potash"

            ],


            "dosage":{


                "Urea":
                "150 kg/hectare",


                "NPK 20:20:0":
                "60 kg/hectare",


                "Potash":
                "50 kg/hectare"

            }

        },



        "cotton":{


            "category":
            "🧵 Cash Crop",


            "description":
            "Cotton grows best in black soil.",


            "fertilizer":[

                "Urea",

                "DAP",

                "MOP (Potash)"

            ],


            "dosage":{


                "Urea":
                "100 kg/hectare",


                "DAP":
                "50 kg/hectare",


                "MOP (Potash)":
                "50 kg/hectare"

            }

        },



        "banana":{


            "category":
            "🍌 Fruit Crop",


            "description":
            "Banana requires high humidity.",


            "fertilizer":[

                "NPK 19:19:19",

                "Urea",

                "Potash"

            ],


            "dosage":{


                "NPK 19:19:19":
                "100 kg/hectare",


                "Urea":
                "150 kg/hectare",


                "Potash":
                "80 kg/hectare"

            }

        },



        "mango":{


            "category":
            "🥭 Fruit Crop",


            "description":
            "Mango is a tropical fruit crop.",


            "fertilizer":[

                "Organic Compost",

                "NPK",

                "Potash"

            ],


            "dosage":{


                "Organic Compost":
                "25 kg/tree",


                "NPK":
                "2 kg/tree",


                "Potash":
                "1 kg/tree"

            }

        }


    }



    info = crop_details.get(

        crop.lower(),

        {

            "category":
            "🌱 Crop",


            "description":
            "Suitable crop based on soil and weather.",


            "fertilizer":[

                "General NPK"

            ],


            "dosage":{

                "General NPK":
                "As per soil test"

            }

        }

    )



    # ====================================
    # Save Prediction History
    # ====================================


    db_path = os.path.join(
        "database",
        "database.db"
    )



    with sqlite3.connect(
        db_path,
        timeout=10
    ) as conn:


        cursor = conn.cursor()


        cursor.execute(
            """
            INSERT INTO history
            (crop,N,P,K,temperature,humidity,ph,rainfall)
            VALUES (?,?,?,?,?,?,?,?)
            """,

            (

                crop,

                N,

                P,

                K,

                temperature,

                humidity,

                ph,

                rainfall

            )

        )


        conn.commit()



    flash(
        "Crop Predicted Successfully!",
        "success"
    )



    # ====================================
    # OpenAI Explanation
    # ====================================


    prompt = f"""

You are an agriculture expert.

Explain why {crop} is recommended.

Crop: {crop}

Nitrogen: {N}

Phosphorus: {P}

Potassium: {K}

Temperature: {temperature} °C

Humidity: {humidity} %

pH: {ph}

Rainfall: {rainfall} mm


Give:

1. Why this crop is suitable.
2. Soil analysis.
3. Weather suitability.
4. Farming advice.


Keep answer simple and under 120 words.

"""



    try:


        response = client.chat.completions.create(

            model="gpt-4o-mini",


            messages=[

                {

                    "role":"user",

                    "content":prompt

                }

            ],


            max_tokens=200

        )


        ai_explanation = (
            response
            .choices[0]
            .message
            .content
        )



    except Exception as e:


        print(
            "OPENAI ERROR:",
            e
        )


        ai_explanation = (
            f"AI explanation unavailable. Error: {e}"
        )



    return render_template(

        "result.html",


        crop=crop.title(),


        category=info["category"],


        description=info["description"],


        fertilizer=info["fertilizer"],


        dosage=info["dosage"],


        ai_explanation=ai_explanation,


        N=N,


        P=P,


        K=K,


        temperature=temperature,


        humidity=humidity,


        ph=ph,


        rainfall=rainfall,


        accuracy="99.32%"

    )
# ====================================
# Fertilizer Dosage Calculator
# ====================================


@app.route(
    "/calculate_dosage",
    methods=["POST"]
)

def calculate_dosage():


    crop = request.form["crop"].lower()


    area = float(
        request.form["area"]
    )



    fertilizer_data = {


        "rice":{


            "Urea":120,

            "DAP":60,

            "MOP (Potash)":40

        },


        "wheat":{


            "Urea":100,

            "DAP":50,

            "Potash":40

        },


        "maize":{


            "Urea":150,

            "NPK 20:20:0":60,

            "Potash":50

        },


        "cotton":{


            "Urea":100,

            "DAP":50,

            "MOP (Potash)":50

        },


        "banana":{


            "NPK 19:19:19":100,

            "Urea":150,

            "Potash":80

        },


        "mango":{


            "Organic Compost":25,

            "NPK":2,

            "Potash":1

        }


    }



    dosage = {}



    if crop in fertilizer_data:


        for fertilizer, amount in fertilizer_data[crop].items():


            dosage[fertilizer] = round(

                amount * area,

                2

            )



    return render_template(

        "dosage_result.html",

        crop=crop.title(),

        area=area,

        dosage=dosage

    )





# ====================================
# Weather Data API
# ====================================


@app.route(
    "/get_weather",
    methods=["POST"]
)

def get_weather():


    city = request.form["city"]



    url = (

        "https://api.openweathermap.org/data/2.5/weather"

        f"?q={city}&appid={WEATHER_API_KEY}&units=metric"

    )



    try:


        response = requests.get(

            url,

            timeout=10

        )


    except Exception as e:


        flash(

            "Weather service unavailable!",

            "danger"

        )


        return redirect(

            url_for("recommend")

        )



    if response.status_code != 200:


        flash(

            "City not found!",

            "danger"

        )


        return redirect(

            url_for("recommend")

        )



    data = response.json()



    temperature = data["main"]["temp"]


    humidity = data["main"]["humidity"]



    rainfall = 0



    if "rain" in data:


        rainfall = data["rain"].get(

            "1h",

            0

        )



    return render_template(

        "recommend.html",

        weather=True,

        city=city,

        temperature=temperature,

        humidity=humidity,

        rainfall=rainfall

    )

# ====================================
# Change Language
# ====================================

@app.route("/change_language/<lang>")
def change_language(lang):

    session["language"] = lang

    return redirect(request.referrer or url_for("home"))





# ====================================
# Run Application
# ====================================

if __name__ == "__main__":


    app.run(
        debug=True
    )