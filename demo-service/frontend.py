import random
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import json
import boto3
import names
import logging

app = Flask(__name__)

# ----------------------- Logging Configuration -----------------------
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------- AWS Secrets Manager -------------------------
aws_region = os.getenv("AWS_DEFAULT_REGION", default='eu-west-1')
secret_arn = os.getenv("DEMO_DB_SECRET_ARN")

try:
    sm_client = boto3.client('secretsmanager', region_name=aws_region)
    response = sm_client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response['SecretString'])
except Exception as e:
    logger.error(f"Failed to retrieve secret: {e}")
    sys.exit(1)

# ------------------ Aurora (PostgreSQL Database) ---------------------
DB_URL = f"postgresql://{secret['username']}:{secret['password']}@{secret['host']}/{secret['dbname']}"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------- Database Model ------------------------------
class UserModel(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"<User {self.email}>"

# ------------------------ Routes -------------------------------------
@app.route('/', methods=["GET", "POST"])
def create_user():
    if request.method == 'POST':
        try:
            # Capture form data and save to database
            new_customer = UserModel(
                name=request.form['user'],
                email=request.form['email']
            )
            db.session.add(new_customer)
            db.session.commit()
            logger.info(f"User {new_customer.email} created successfully.")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return "Error creating user", 500

        return redirect(url_for('users'))

    # Prepopulate form with random user data
    first_name = names.get_first_name()
    last_name = names.get_last_name()
    name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}_{last_name.lower()}@mydomain.com"

    return render_template('index.html', user=name, email=email)


@app.route('/users')
def users():
    try:
        # Fetch all users from the database
        users_list = UserModel.query.all()
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return "Error fetching users", 500

    return render_template('users.html', users=users_list)

# ----------------------- App Initialization --------------------------
if __name__ == '__main__':
    try:
        db.create_all()
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")
        sys.exit(1)

    app.run(host='0.0.0.0', port=5000, debug=False)
