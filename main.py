from flask import (Flask,render_template,request,jsonify,session,redirect,url_for,flash,send_from_directory)
import os
import re
import json
import uuid

app = Flask(__name__)

app.secret_key = "change-this-to-a-random-secret-key"

app.config["SESSION_PERMANENT"] = False

DATA_FILE = os.path.join(app.root_path,"data_storage","data.json")
BACKGROUND_FOLDER = os.path.join(app.static_folder,"background")
ALLOWED_EXTENSIONS = {"jpg","jpeg","png","webp","gif"}


# =====================================================
# USER DATA
# =====================================================

def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError,FileNotFoundError):
        return []


def save_users(users):
    os.makedirs(os.path.dirname(DATA_FILE),exist_ok=True)
    with open(DATA_FILE,"w",encoding="utf-8") as file:
        json.dump(users,file,indent=4,ensure_ascii=False)

def get_background_data(user):
    background_data = user.get("background_image",{})
    if not isinstance(background_data,dict):
        background_data = {}
    background_list = background_data.get("background",[])
    if not isinstance(background_list,list):
        background_list = []
    selected_background = background_data.get("selected_background","")
    return {"selected_background": selected_background,"background": background_list}

def get_current_user(users):
    user_email = session.get("user_email","").strip().lower()
    user_phone = re.sub(
        r"\D",
        "",
        session.get(
            "user_phone",
            ""
        )
    )

    if not user_email and not user_phone:
        return None

    for user in users:

        email = user.get(
            "email",
            ""
        ).strip().lower()

        phone = re.sub(
            r"\D",
            "",
            user.get(
                "phone",
                ""
            )
        )

        if (
            user_email
            and email == user_email
        ):

            return user

        if (
            user_phone
            and phone == user_phone
        ):

            return user

    return None


# =====================================================
# SESSION DATA
# =====================================================

def update_background_session(
    background_data
):

    session["background_image"] = (
        background_data
    )

    session["background"] = (
        background_data.get(
            "background",
            []
        )
    )

    session["selected_background"] = (
        background_data.get(
            "selected_background",
            ""
        )
    )

@app.context_processor
def inject_user_data():
    city_name = []
    if "user_email" in session:
        users = load_users()
        user = get_current_user(users)
        if user is not None:
            city_data = user.get("city",{})
            if isinstance(city_data, dict):
                city_name = city_data.get("city_name",[])
            if isinstance(city_name, dict):
                city_name = [city_name]
            if not isinstance(city_name,list):
                city_name = []
    return {
        "user_name": session.get("user_name","Guest"),
        "logged_in": ("user_email" in session),
        "selected_background": session.get("selected_background",""),
        "background_image": session.get("background",[]),
        "timezone": session.get("timezone","Asia/Kolkata"),
        "city_name": city_name
    }




# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    logged_in = (
        "user_email" in session
    )

    section = request.args.get(
        "section",
        ""
    )

    background_image = session.get(
        "background",
        []
    )

    selected_background = session.get(
        "selected_background",
        ""
    )

    return render_template(
        "index.html",

        user_name=session.get(
            "user_name",
            "Guest"
        ),

        logged_in=logged_in,

        open_login=not logged_in,

        section=section,

        background_image=background_image,

        selected_background=selected_background,

        timezone=session.get(
            "timezone",
            "Asia/Kolkata"
        )
    )


# =====================================================
# LOGIN
# =====================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # -------------------------------------------------
    # GET
    # -------------------------------------------------

    if request.method == "GET":

        if "user_email" in session:

            return redirect(
                url_for("home")
            )

        return render_template(
            "index.html",

            user_name="Guest",

            logged_in=False,

            open_login=True
        )


    # -------------------------------------------------
    # POST
    # -------------------------------------------------

    if request.is_json:

        data = request.get_json(
            silent=True
        ) or {}

        login_value = data.get(
            "login",
            ""
        ).strip()

        password = data.get(
            "password",
            ""
        )

    else:

        login_value = request.form.get(
            "login",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


    if not login_value:

        return jsonify({
            "success": False,
            "message": "Email or phone is required."
        }), 400


    if not password:

        return jsonify({
            "success": False,
            "message": "Password is required."
        }), 400


    users = load_users()


    login_email = login_value.lower()

    login_phone = re.sub(
        r"\D",
        "",
        login_value
    )


    user = None


    for item in users:

        item_email = item.get(
            "email",
            ""
        ).strip().lower()

        item_phone = re.sub(
            r"\D",
            "",
            item.get(
                "phone",
                ""
            )
        )

        item_password = item.get(
            "password",
            ""
        )


        email_match = (
            login_email
            and
            item_email == login_email
        )


        phone_match = (
            login_phone
            and
            item_phone == login_phone
        )


        password_match = (
            item_password == password
        )


        if (
            (email_match or phone_match)
            and
            password_match
        ):

            user = item

            break


    if user is None:

        return jsonify({

            "success": False,

            "message":
                "Invalid email/phone or password."

        }), 401


    # -------------------------------------------------
    # CREATE SESSION
    # -------------------------------------------------

    session.clear()


    session["user_email"] = user.get(
        "email",
        ""
    )

    session["user_name"] = user.get(
        "name",
        "User"
    )

    session["user_phone"] = user.get(
        "phone",
        ""
    )

    session["gender"] = user.get(
        "gender",
        ""
    )


    timezone = user.get(
        "timezone",
        ""
    )

    if not timezone:

        timezone = "Asia/Kolkata"


    session["timezone"] = timezone


    # -------------------------------------------------
    # BACKGROUND
    # -------------------------------------------------

    background_data = get_background_data(
        user
    )

    update_background_session(
        background_data
    )


    # -------------------------------------------------
    # CITY
    # -------------------------------------------------

    city_data = user.get(
        "city",
        {}
    )


    if not isinstance(
        city_data,
        dict
    ):

        city_data = {
            "name": "",
            "places": []
        }


    session["city"] = city_data

    session["city_name"] = city_data.get(
        "name",
        ""
    )

    session["places"] = city_data.get(
        "places",
        []
    )


    return jsonify({

        "success": True,

        "message":
            "Login successful.",

        "user_name":
            session["user_name"],

        "user_email":
            session["user_email"],

        "user_phone":
            session["user_phone"],

        "gender":
            session["gender"],

        "timezone":
            session["timezone"],

        "background_image":
            session["background_image"],

        "selected_background":
            session["selected_background"],

        "background":
            session["background"],

        "city":
            session["city"],

        "city_name":
            session["city_name"],

        "places":
            session["places"],

        "redirect":
            url_for("home")

    })


# =====================================================
# CHECK LOGIN
# =====================================================

@app.route(
    "/check-login",
    methods=["GET"]
)
def check_login():

    if "user_email" not in session:

        return jsonify({
            "logged_in": False
        })


    return jsonify({

        "logged_in": True,

        "user_name": session.get(
            "user_name",
            "User"
        ),

        "user_email": session.get(
            "user_email",
            ""
        )

    })


# =====================================================
# SIGNUP
# =====================================================

@app.route(
    "/signup",
    methods=["POST"]
)
def signup():

    if request.is_json:

        data = request.get_json(
            silent=True
        ) or {}

        name = data.get(
            "name",
            ""
        ).strip()

        email = data.get(
            "email",
            ""
        ).strip().lower()

        phone = data.get(
            "phone",
            ""
        ).strip()

        password = data.get(
            "password",
            ""
        )

        gender = data.get(
            "gender",
            ""
        ).strip()

    else:

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        gender = request.form.get(
            "gender",
            ""
        ).strip()


    if not name:

        return jsonify({
            "success": False,
            "message": "Please enter your name."
        }), 400


    if not email:

        return jsonify({
            "success": False,
            "message": "Please enter your email."
        }), 400


    email_pattern = (
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )


    if not re.fullmatch(
        email_pattern,
        email
    ):

        return jsonify({
            "success": False,
            "message": "Please enter a valid email."
        }), 400


    phone = re.sub(
        r"\D",
        "",
        phone
    )


    if len(phone) != 10:

        return jsonify({
            "success": False,
            "message":
                "Phone number must contain 10 digits."
        }), 400


    if not password:

        return jsonify({
            "success": False,
            "message":
                "Please enter a password."
        }), 400


    if len(password) < 6:

        return jsonify({
            "success": False,
            "message":
                "Password must contain at least 6 characters."
        }), 400


    users = load_users()


    for user in users:

        existing_email = user.get(
            "email",
            ""
        ).strip().lower()

        existing_phone = re.sub(
            r"\D",
            "",
            user.get(
                "phone",
                ""
            )
        )


        if existing_email == email:

            return jsonify({
                "success": False,
                "message":
                    "This email is already registered."
            }), 409


        if existing_phone == phone:

            return jsonify({
                "success": False,
                "message":
                    "This phone number is already registered."
            }), 409


    new_user = {

        "name": name,

        "email": email,

        "phone": phone,

        "password": password,

        "gender": gender,

        "timezone": "",

        "background_image": {

            "selected_background": "",

            "background": []

        },

        "city": {

        }

    }


    users.append(
        new_user
    )


    save_users(
        users
    )


    return jsonify({

        "success": True,

        "message":
            "Account created successfully."

    })


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =====================================================
# SETTINGS
# =====================================================

@app.route("/setting")
def setting():

    if "user_email" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    return redirect(
        url_for(
            "home",
            section="setting"
        )
    )


# =====================================================
# ADD BACKGROUND TO USER DATA
# =====================================================

def add_background_image(
    image_name
):

    users = load_users()

    user = get_current_user(
        users
    )


    if user is None:

        return (
            False,
            "User not found."
        )


    background_data = get_background_data(
        user
    )


    background_list = (
        background_data["background"]
    )


    if image_name in background_list:

        return (
            False,
            "This image already exists."
        )


    background_list.append(
        image_name
    )


    background_data[
        "background"
    ] = background_list


    user[
        "background_image"
    ] = background_data


    save_users(
        users
    )


    update_background_session(
        background_data
    )


    return (
        True,
        "Background image added successfully."
    )


# =====================================================
# ADD BACKGROUND
# =====================================================

@app.route(
    "/add_background",
    methods=["POST"]
)
def add_background():

    setting_url = url_for(
        "home",
        section="setting"
    )


    if "user_email" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    if "background" not in request.files:

        flash(
            "No image selected.",
            "error"
        )

        return redirect(
            setting_url
        )


    file = request.files[
        "background"
    ]


    if (
        file is None
        or
        file.filename == ""
    ):

        flash(
            "No image selected.",
            "error"
        )

        return redirect(
            setting_url
        )


    filename = os.path.basename(
        file.filename
    )


    if "." not in filename:

        flash(
            "Invalid image file.",
            "error"
        )

        return redirect(
            setting_url
        )


    extension = (
        filename
        .rsplit(
            ".",
            1
        )[-1]
        .lower()
    )


    if extension not in ALLOWED_EXTENSIONS:

        flash(
            "Only JPG, JPEG, PNG, WEBP and GIF files are allowed.",
            "error"
        )

        return redirect(
            setting_url
        )


    os.makedirs(
        BACKGROUND_FOLDER,
        exist_ok=True
    )


    file_path = os.path.join(
        BACKGROUND_FOLDER,
        filename
    )


    if os.path.exists(
        file_path
    ):

        flash(
            "An image with this name already exists.",
            "error"
        )

        return redirect(
            setting_url
        )


    try:

        file.save(
            file_path
        )


        success, message = (
            add_background_image(
                filename
            )
        )


        if not success:

            if os.path.isfile(
                file_path
            ):

                os.remove(
                    file_path
                )


            flash(
                message,
                "error"
            )

            return redirect(
                setting_url
            )


        flash(
            message,
            "success"
        )


    except Exception as error:

        if os.path.isfile(
            file_path
        ):

            os.remove(
                file_path
            )


        flash(
            f"Error adding background image: {error}",
            "error"
        )


    return redirect(
        setting_url
    )


# =====================================================
# SET BACKGROUND
# =====================================================

@app.route(
    "/set_background",
    methods=["POST"]
)
def set_background():

    setting_url = url_for(
        "home",
        section="setting"
    )


    if "user_email" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    image_name = request.form.get(
        "background",
        ""
    ).strip()


    if not image_name:

        flash(
            "Background image was not selected.",
            "error"
        )

        return redirect(
            setting_url
        )


    image_name = os.path.basename(
        image_name
    )


    users = load_users()

    user = get_current_user(
        users
    )


    if user is None:

        flash(
            "User not found.",
            "error"
        )

        return redirect(
            setting_url
        )


    background_data = get_background_data(
        user
    )


    background_list = (
        background_data["background"]
    )


    if image_name not in background_list:

        flash(
            "Background image not found in your images.",
            "error"
        )

        return redirect(
            setting_url
        )


    background_data[
        "selected_background"
    ] = image_name


    user[
        "background_image"
    ] = background_data


    save_users(
        users
    )


    update_background_session(
        background_data
    )


    flash(
        "Background image selected successfully.",
        "success"
    )


    return redirect(
        setting_url
    )


# =====================================================
# DELETE BACKGROUND
# =====================================================

@app.route(
    "/delete_background",
    methods=["POST"]
)
def delete_background():

    setting_url = url_for(
        "home",
        section="setting"
    )


    if "user_email" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    image_name = request.form.get(
        "background",
        ""
    ).strip()


    if not image_name:

        flash(
            "Image name is required.",
            "error"
        )

        return redirect(
            setting_url
        )


    image_name = os.path.basename(
        image_name
    )


    users = load_users()

    user = get_current_user(
        users
    )


    if user is None:

        flash(
            "User not found.",
            "error"
        )

        return redirect(
            setting_url
        )


    background_data = get_background_data(
        user
    )


    background_list = (
        background_data["background"]
    )


    if image_name not in background_list:

        flash(
            "Background image not found.",
            "error"
        )

        return redirect(
            setting_url
        )


    background_list.remove(
        image_name
    )


    if (
        background_data.get(
            "selected_background",
            ""
        )
        ==
        image_name
    ):

        background_data[
            "selected_background"
        ] = ""


    background_data[
        "background"
    ] = background_list


    user[
        "background_image"
    ] = background_data


    save_users(
        users
    )


    update_background_session(
        background_data
    )


    file_path = os.path.join(
        BACKGROUND_FOLDER,
        image_name
    )


    if os.path.isfile(
        file_path
    ):

        try:

            os.remove(
                file_path
            )

        except OSError as error:

            flash(
                f"Image removed from your account, but the file could not be deleted: {error}",
                "error"
            )

            return redirect(
                setting_url
            )


    flash(
        "Background image deleted successfully.",
        "success"
    )


    return redirect(
        setting_url
    )

# =====================================================
# SET TIMEZONE
# =====================================================

@app.route(
    "/set_timezone",
    methods=["POST"]
)
def set_timezone():

    setting_url = url_for(
        "home",
        section="setting"
    )

    # -------------------------------------------------
    # CHECK LOGIN
    # -------------------------------------------------

    if "user_email" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # -------------------------------------------------
    # GET TIMEZONE
    # -------------------------------------------------

    timezone = request.form.get(
        "timezone",
        ""
    ).strip()


    if not timezone:

        flash(
            "Please select a timezone.",
            "error"
        )

        return redirect(
            setting_url
        )


    # -------------------------------------------------
    # LOAD USERS
    # -------------------------------------------------

    users = load_users()


    # -------------------------------------------------
    # FIND CURRENT USER
    # -------------------------------------------------

    user = get_current_user(
        users
    )


    if user is None:

        flash(
            "User not found.",
            "error"
        )

        return redirect(
            setting_url
        )


    # -------------------------------------------------
    # UPDATE TIMEZONE
    # -------------------------------------------------

    user["timezone"] = timezone


    # -------------------------------------------------
    # SAVE USER DATA
    # -------------------------------------------------

    save_users(
        users
    )


    # -------------------------------------------------
    # UPDATE SESSION
    # -------------------------------------------------

    session["timezone"] = timezone


    # -------------------------------------------------
    # SUCCESS
    # -------------------------------------------------

    flash(
        "Timezone changed successfully.",
        "success"
    )


    return redirect(
        setting_url
    )



# =====================================================
# ABOUT ME
# =====================================================

@app.route("/aboutme")
def aboutme():

    if "user_email" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    background_data = session.get(
        "background_image",
        {}
    )


    if not isinstance(
        background_data,
        dict
    ):

        background_data = {}


    backgrounds = session.get(
        "background",
        []
    )


    selected_background = session.get(
        "selected_background",
        ""
    )


    city = session.get(
        "city",
        {}
    )


    return render_template(

        "index.html",

        section="aboutme",

        user_name=session.get(
            "user_name",
            "User"
        ),

        user_gmail=session.get(
            "user_email",
            ""
        ),

        user_phone=session.get(
            "user_phone",
            ""
        ),

        timezone=session.get(
            "timezone",
            "Asia/Kolkata"
        ),

        gender=session.get(
            "gender",
            ""
        ),

        background_image=background_data,

        backgrounds=backgrounds,

        selected_background=selected_background,

        city=city,

        city_name=session.get(
            "city_name",
            ""
        ),

        places=session.get(
            "places",
            []
        )

    )




@app.route('/add_city')
def add_city():
    return render_template('index.html' , section="add_city")

@app.route("/create_city",methods=["POST"])
def create_city():
    if "user_email" not in session:
        flash("Please login first.","error")
        return redirect(url_for("login"))
    city_name = request.form.get("city_name","").strip()
    if not city_name:
        flash("Please enter a city name.","error")
        return redirect(url_for("city"))
    users = load_users()
    user = get_current_user(users)
    if user is None:
        flash("User not found.","error")
        return redirect(url_for("login"))
    if "city" not in user:
        user["city"] = {}
    if "city_name" not in user["city"]:
        user["city"]["city_name"] = []
    elif isinstance(user["city"]["city_name"],dict):
        old_city = user["city"]["city_name"]
        user["city"]["city_name"] = []
        if old_city.get("name_of_city"):
            user["city"]["city_name"].append(old_city)
    for city in user["city"]["city_name"]:
        if not isinstance(city, dict):
            continue
        existing_name = city.get("name_of_city","").strip()
        if (existing_name.lower()== city_name.lower()):
            flash(f"{city_name} already exists.","error")
            return redirect(url_for("city",city_name=city_name))
    new_city = {"name_of_city": city_name,"places": []}
    user["city"]["city_name"].append(new_city)
    save_users(users)
    session["city_name"] = (user["city"]["city_name"])
    flash(f"{city_name} created successfully.","success")
    return redirect(url_for("city",city_name=city_name))

@app.route("/city")
def city():
    if "user_email" not in session:
        flash("Please login first.","error")
        return redirect(url_for("login"))
    selected_city_name = request.args.get("city_name","").strip()
    users = load_users()
    user = get_current_user(users)
    if user is None:
        flash("User not found.","error")
        return redirect(url_for("login"))
    city_data = user.get("city",{})
    city_name = city_data.get("city_name",[])
    if isinstance(city_name, dict):
        city_name = [city_name]
    selected_city = None
    if selected_city_name:
        for city in city_name:
            if not isinstance(city, dict):
                continue
            existing_name = city.get("name_of_city","").strip()
            if (existing_name.lower()== selected_city_name.lower()):
                selected_city = city
                break
    if selected_city is None:
        flash("City not found.","error")
        return redirect(url_for("home", section="setting"))
    return render_template("index.html",section="city",city_name=city_name,selected_city=selected_city,city=selected_city)


@app.route("/create_place", methods=["POST"])
def create_place():

    if "user_email" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    place_name = request.form.get("place_name", "").strip()
    about_place = request.form.get("about_place", "").strip()
    city_name = request.form.get("city_name", "").strip()

    if not city_name:
        flash("Please select a city first.", "error")
        return redirect(url_for("city"))

    if not place_name:
        flash("Please enter a place name.", "error")
        return redirect(url_for("city", city_name=city_name))

    if not about_place:
        flash("Please enter information about the place.", "error")
        return redirect(url_for("city", city_name=city_name))

    users = load_users()
    user = get_current_user(users)

    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("login"))

    if "city" not in user:
        flash("City information not found.", "error")
        return redirect(url_for("city"))

    cities = user["city"].get("city_name", [])

    if isinstance(cities, dict):
        cities = [cities]
        user["city"]["city_name"] = cities

    selected_city = None

    for city in cities:

        if not isinstance(city, dict):
            continue

        existing_name = city.get("name_of_city", "").strip()

        if existing_name.lower() == city_name.lower():
            selected_city = city
            break

    if selected_city is None:
        flash(f"City '{city_name}' not found.", "error")
        return redirect(url_for("city"))

    if "places" not in selected_city:
        selected_city["places"] = []

    if not isinstance(selected_city["places"], list):
        selected_city["places"] = []

    for place in selected_city["places"]:

        if not isinstance(place, dict):
            continue

        existing_place = place.get("place_name", "").strip()

        if existing_place.lower() == place_name.lower():
            flash(
                f"{place_name} already exists in {city_name}.",
                "error"
            )
            return redirect(
                url_for("city", city_name=city_name)
            )

    new_place = {
        "place_name": place_name,
        "description": about_place,
        "images": []
    }

    selected_city["places"].append(new_place)

    save_users(users)

    session["selected_city"] = city_name

    flash(
        f"{place_name} added successfully to {city_name}.",
        "success"
    )

    return redirect(
        url_for("city", city_name=city_name)
    )

@app.route("/image-upload", methods=["POST"])
def image_upload():

    # ==========================================
    # CHECK LOGIN
    # ==========================================

    if "user_email" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))


    # ==========================================
    # GET FORM DATA
    # ==========================================

    city_name = request.form.get(
        "city_name",
        ""
    ).strip()

    place_index = request.form.get(
        "place_index",
        ""
    ).strip()


    # ==========================================
    # VALIDATE CITY
    # ==========================================

    if not city_name:
        flash("City not found.", "error")
        return redirect(url_for("city"))


    # ==========================================
    # VALIDATE PLACE INDEX
    # ==========================================

    if not place_index.isdigit():
        flash("Invalid place.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )

    place_index = int(place_index)


    # ==========================================
    # GET MULTIPLE IMAGES
    # ==========================================

    images = request.files.getlist("place_images")

    # Remove empty file selections
    images = [
        image for image in images
        if image and image.filename
    ]

    if not images:
        flash("Please select at least one image.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # ALLOWED EXTENSIONS
    # ==========================================

    allowed_extensions = {
        "jpg",
        "jpeg",
        "png",
        "webp",
        "gif"
    }


    # ==========================================
    # LOAD USER
    # ==========================================

    users = load_users()

    user = get_current_user(users)

    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("login"))


    # ==========================================
    # GET CITIES
    # ==========================================

    cities = user.get(
        "city",
        {}
    ).get(
        "city_name",
        []
    )


    if isinstance(cities, dict):
        cities = [cities]


    # ==========================================
    # FIND CITY
    # ==========================================

    selected_city = None

    for city in cities:

        if not isinstance(city, dict):
            continue

        if city.get(
            "name_of_city",
            ""
        ).strip().lower() == city_name.lower():

            selected_city = city
            break


    if selected_city is None:
        flash("City not found.", "error")
        return redirect(url_for("city"))


    # ==========================================
    # GET PLACES
    # ==========================================

    places = selected_city.get(
        "places",
        []
    )


    if not isinstance(places, list):
        places = []
        selected_city["places"] = places


    # ==========================================
    # CHECK PLACE
    # ==========================================

    if place_index < 0 or place_index >= len(places):
        flash("Place not found.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    place = places[place_index]


    if not isinstance(place, dict):
        flash("Invalid place.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # CREATE UPLOAD DIRECTORY
    # ==========================================

    upload_folder = os.path.join(
        app.static_folder,
        "place_images"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    # ==========================================
    # CREATE IMAGES LIST
    # ==========================================

    if "images" not in place:
        place["images"] = []

    if not isinstance(place["images"], list):
        place["images"] = []


    # ==========================================
    # SAVE ALL IMAGES
    # ==========================================

    uploaded_count = 0

    for image in images:

        filename = image.filename

        # --------------------------------------
        # CHECK EXTENSION
        # --------------------------------------

        if "." not in filename:
            continue

        extension = filename.rsplit(
            ".",
            1
        )[-1].lower()

        if extension not in allowed_extensions:
            continue


        # --------------------------------------
        # CREATE UNIQUE FILE NAME
        # --------------------------------------

        new_filename = (
            str(uuid.uuid4())
            + "."
            + extension
        )


        file_path = os.path.join(
            upload_folder,
            new_filename
        )


        # --------------------------------------
        # SAVE IMAGE
        # --------------------------------------

        image.save(file_path)


        # --------------------------------------
        # SAVE IMAGE PATH
        # --------------------------------------

        image_path = os.path.join(
            "place_images",
            new_filename
        ).replace(
            os.sep,
            "/"
        )


        place["images"].append(
            image_path
        )

        uploaded_count += 1


    # ==========================================
    # CHECK UPLOAD RESULT
    # ==========================================

    if uploaded_count == 0:

        flash(
            "No valid images were uploaded. "
            "Only JPG, JPEG, PNG, WEBP and GIF images are allowed.",
            "error"
        )

        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # SAVE USER DATA
    # ==========================================

    save_users(users)

    session["selected_city"] = city_name


    # ==========================================
    # SUCCESS MESSAGE
    # ==========================================

    flash(
        f"{uploaded_count} image(s) added successfully.",
        "success"
    )


    return redirect(
        url_for(
            "city",
            city_name=city_name
        )
    )



@app.route("/delete_place_image", methods=["POST"])
def delete_place_image():

    # ==========================================
    # CHECK LOGIN
    # ==========================================

    if "user_email" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))


    # ==========================================
    # GET FORM DATA
    # ==========================================

    city_name = request.form.get(
        "city_name",
        ""
    ).strip()

    place_index = request.form.get(
        "place_index",
        ""
    ).strip()

    image_index = request.form.get(
        "image_index",
        ""
    ).strip()


    # ==========================================
    # VALIDATE CITY
    # ==========================================

    if not city_name:
        flash("City not found.", "error")
        return redirect(url_for("city"))


    # ==========================================
    # VALIDATE PLACE
    # ==========================================

    if not place_index.isdigit():
        flash("Invalid place.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # VALIDATE IMAGE
    # ==========================================

    if not image_index.isdigit():
        flash("Invalid image.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    place_index = int(place_index)
    image_index = int(image_index)


    # ==========================================
    # LOAD USER
    # ==========================================

    users = load_users()

    user = get_current_user(users)

    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("login"))


    # ==========================================
    # GET CITIES
    # ==========================================

    cities = user.get(
        "city",
        {}
    ).get(
        "city_name",
        []
    )


    if isinstance(cities, dict):
        cities = [cities]


    # ==========================================
    # FIND CITY
    # ==========================================

    selected_city = None

    for city in cities:

        if not isinstance(city, dict):
            continue

        if city.get(
            "name_of_city",
            ""
        ).strip().lower() == city_name.lower():

            selected_city = city
            break


    if selected_city is None:
        flash("City not found.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # GET PLACES
    # ==========================================

    places = selected_city.get(
        "places",
        []
    )


    if not isinstance(places, list):
        flash("Place not found.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # CHECK PLACE INDEX
    # ==========================================

    if place_index < 0 or place_index >= len(places):
        flash("Place not found.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    place = places[place_index]


    if not isinstance(place, dict):
        flash("Invalid place.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # GET IMAGES
    # ==========================================

    images = place.get(
        "images",
        []
    )


    if not isinstance(images, list):
        flash("No images found.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # CHECK IMAGE INDEX
    # ==========================================

    if image_index < 0 or image_index >= len(images):
        flash("Image not found.", "error")
        return redirect(
            url_for(
                "city",
                city_name=city_name
            )
        )


    # ==========================================
    # GET IMAGE PATH
    # ==========================================

    image_path = images[image_index]


    # ==========================================
    # DELETE PHYSICAL FILE
    # ==========================================

    if image_path:

        # Stored value:
        #
        # place_images/abc123.jpg
        #
        # Physical file:
        #
        # static/place_images/abc123.jpg

        full_path = os.path.join(
            app.static_folder,
            image_path
        )


        if os.path.isfile(full_path):

            try:

                os.remove(full_path)

            except OSError as e:

                print(
                    f"Error deleting image: {e}"
                )


    # ==========================================
    # REMOVE FROM USER DATA
    # ==========================================

    images.pop(image_index)


    # ==========================================
    # SAVE USER DATA
    # ==========================================

    save_users(users)


    session["selected_city"] = city_name


    flash(
        "Image deleted successfully.",
        "success"
    )


    return redirect(
        url_for(
            "city",
            city_name=city_name
        )
    )

@app.route("/download_place_image/<path:filename>")
def download_place_image(filename):

    # Make sure only the filename is used
    filename = filename.replace(
        "place_images/",
        "",
        1
    )

    upload_folder = os.path.join(
        app.static_folder,
        "place_images"
    )

    return send_from_directory(
        upload_folder,
        filename,
        as_attachment=True
    )

@app.route("/update_place", methods=["POST"])
def update_place():

    # ==========================================
    # CHECK LOGIN
    # ==========================================

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    try:

        # ==========================================
        # GET JSON DATA FROM JAVASCRIPT
        # ==========================================

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "message": "Invalid request data."
            }), 400


        city_name = str(
            data.get("city_name", "")
        ).strip()

        place_name = str(
            data.get("place_name", "")
        ).strip()

        description = str(
            data.get("description", "")
        ).strip()

        place_index = data.get("place_index")


        # ==========================================
        # VALIDATION
        # ==========================================

        if not city_name:
            return jsonify({
                "success": False,
                "message": "City name is required."
            }), 400


        if not place_name:
            return jsonify({
                "success": False,
                "message": "Place name cannot be empty."
            }), 400


        if not description:
            return jsonify({
                "success": False,
                "message": "Description cannot be empty."
            }), 400


        if place_index is None:
            return jsonify({
                "success": False,
                "message": "Place index is required."
            }), 400


        try:
            place_index = int(place_index)

        except (ValueError, TypeError):

            return jsonify({
                "success": False,
                "message": "Invalid place index."
            }), 400


        # ==========================================
        # LOAD ALL USERS
        # ==========================================

        users = load_users()


        # ==========================================
        # GET CURRENT LOGGED-IN USER
        # ==========================================

        user = get_current_user(users)


        if user is None:

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404


        # ==========================================
        # CHECK CITY DATA
        # ==========================================

        if "city" not in user:

            return jsonify({
                "success": False,
                "message": "City information not found."
            }), 404


        if not isinstance(
            user["city"],
            dict
        ):

            return jsonify({
                "success": False,
                "message": "Invalid city data."
            }), 500


        # ==========================================
        # GET CITY LIST
        # ==========================================

        cities = user["city"].get(
            "city_name",
            []
        )


        # ==========================================
        # HANDLE SINGLE CITY DICT
        # ==========================================

        if isinstance(cities, dict):

            cities = [cities]

            user["city"]["city_name"] = cities


        if not isinstance(cities, list):

            return jsonify({
                "success": False,
                "message": "Invalid city list."
            }), 500


        # ==========================================
        # FIND SELECTED CITY
        # ==========================================

        selected_city = None


        for city_item in cities:

            if not isinstance(
                city_item,
                dict
            ):
                continue


            existing_city_name = str(
                city_item.get(
                    "name_of_city",
                    ""
                )
            ).strip()


            if (
                existing_city_name.lower()
                == city_name.lower()
            ):

                selected_city = city_item

                break


        # ==========================================
        # CITY NOT FOUND
        # ==========================================

        if selected_city is None:

            return jsonify({
                "success": False,
                "message":
                    f"City '{city_name}' not found."
            }), 404


        # ==========================================
        # GET PLACES
        # ==========================================

        if "places" not in selected_city:

            selected_city["places"] = []


        if not isinstance(
            selected_city["places"],
            list
        ):

            selected_city["places"] = []


        places = selected_city["places"]


        # ==========================================
        # CHECK PLACE INDEX
        # ==========================================

        if (
            place_index < 0
            or place_index >= len(places)
        ):

            return jsonify({
                "success": False,
                "message": "Place not found."
            }), 404


        # ==========================================
        # CHECK DUPLICATE PLACE NAME
        # ==========================================

        for index, place in enumerate(places):

            if index == place_index:
                continue


            if not isinstance(
                place,
                dict
            ):
                continue


            existing_place_name = str(
                place.get(
                    "place_name",
                    ""
                )
            ).strip()


            if (
                existing_place_name.lower()
                == place_name.lower()
            ):

                return jsonify({
                    "success": False,
                    "message":
                        f"{place_name} already exists in {city_name}."
                }), 409


        # ==========================================
        # GET CURRENT PLACE
        # ==========================================

        current_place = places[place_index]


        if not isinstance(
            current_place,
            dict
        ):

            return jsonify({
                "success": False,
                "message": "Invalid place data."
            }), 500


        # ==========================================
        # UPDATE ONLY NAME + DESCRIPTION
        #
        # IMPORTANT:
        # images are NOT changed.
        # ==========================================

        current_place["place_name"] = place_name

        current_place["description"] = description


        # ==========================================
        # MAKE SURE IMAGES REMAIN
        # ==========================================

        if "images" not in current_place:

            current_place["images"] = []


        if not isinstance(
            current_place["images"],
            list
        ):

            current_place["images"] = []


        # ==========================================
        # SAVE JSON
        # ==========================================

        save_users(users)


        # ==========================================
        # KEEP SELECTED CITY IN SESSION
        # ==========================================

        session["selected_city"] = city_name


        # ==========================================
        # SUCCESS
        # ==========================================

        return jsonify({

            "success": True,

            "message":
                f"{place_name} updated successfully.",

            "place_name":
                place_name,

            "description":
                description

        })


    except Exception as e:

        print(
            "UPDATE PLACE ERROR:",
            str(e)
        )


        return jsonify({

            "success": False,

            "message":
                "An error occurred while updating the place."

        }), 500

import os
from flask import request, jsonify, session

@app.route("/delete_place", methods=["POST"])
def delete_place():

    if "user_email" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    try:
        data = request.get_json()

        city_name = data.get("city_name", "").strip()
        place_index = data.get("place_index")

        if not city_name:
            return jsonify({
                "success": False,
                "message": "City name is required."
            }), 400

        if place_index is None:
            return jsonify({
                "success": False,
                "message": "Place index is required."
            }), 400

        try:
            place_index = int(place_index)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Invalid place index."
            }), 400

        users = load_users()
        user = get_current_user(users)

        if user is None:
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        # -------------------------------------------------
        # GET CITY LIST
        # -------------------------------------------------

        if "city" not in user:
            return jsonify({
                "success": False,
                "message": "City information not found."
            }), 404

        cities = user["city"].get("city_name", [])

        if isinstance(cities, dict):
            cities = [cities]
            user["city"]["city_name"] = cities

        # -------------------------------------------------
        # FIND CITY
        # -------------------------------------------------

        selected_city = None

        for city in cities:

            if not isinstance(city, dict):
                continue

            existing_city_name = city.get(
                "name_of_city", ""
            ).strip()

            if existing_city_name.lower() == city_name.lower():
                selected_city = city
                break

        if selected_city is None:
            return jsonify({
                "success": False,
                "message": f"City '{city_name}' not found."
            }), 404

        # -------------------------------------------------
        # GET PLACES
        # -------------------------------------------------

        places = selected_city.get("places", [])

        if not isinstance(places, list):
            return jsonify({
                "success": False,
                "message": "Invalid places data."
            }), 400

        # -------------------------------------------------
        # VALIDATE PLACE INDEX
        # -------------------------------------------------

        if place_index < 0 or place_index >= len(places):
            return jsonify({
                "success": False,
                "message": "Invalid place index."
            }), 400

        # -------------------------------------------------
        # GET PLACE BEFORE DELETING
        # -------------------------------------------------

        deleted_place = places[place_index]

        place_name = deleted_place.get(
            "place_name",
            "Unknown Place"
        )

        # -------------------------------------------------
        # DELETE ALL PLACE IMAGES FROM FOLDER
        # -------------------------------------------------

        images = deleted_place.get("images", [])

        if isinstance(images, list):

            for image_path in images:

                if not image_path:
                    continue

                try:
                    # Example JSON:
                    # place_images/abc.jpeg
                    #
                    # Convert to:
                    # static/place_images/abc.jpeg

                    image_file = os.path.join(
                        app.static_folder,
                        image_path
                    )

                    # Security check:
                    # Make sure file remains inside static folder
                    static_folder = os.path.abspath(
                        app.static_folder
                    )

                    image_file = os.path.abspath(
                        image_file
                    )

                    if image_file.startswith(
                        static_folder + os.sep
                    ):

                        if os.path.isfile(image_file):
                            os.remove(image_file)

                            print(
                                f"Deleted image: {image_file}"
                            )

                        else:
                            print(
                                f"Image not found: {image_file}"
                            )

                except Exception as image_error:

                    print(
                        f"Could not delete image "
                        f"{image_path}: {image_error}"
                    )

        # -------------------------------------------------
        # DELETE PLACE FROM JSON
        # -------------------------------------------------

        places.pop(place_index)

        # -------------------------------------------------
        # SAVE UPDATED JSON
        # -------------------------------------------------

        save_users(users)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "message": (
                f"'{place_name}' deleted successfully "
                f"along with all its images."
            )
        })

    except Exception as e:

        print("Delete place error:", e)

        return jsonify({
            "success": False,
            "message": "Something went wrong while deleting the place."
        }), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)