from flask import request, jsonify, make_response, Blueprint
import secrets
from datetime import datetime, timedelta, timezone
from src.email_send_code import send_secret_via_email
from src.extensions import db
from src.models.users import User, GenderEnum
from src.utils import upload_image_to_bucket
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
)

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.post('/sign-up')
def sign_up():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        gender_input = request.form['gender'].upper()
        gender = GenderEnum[gender_input].value 
        birth_date = request.form['birth_date']
        address = request.form['address']
        course = request.form['course']

        email = request.form['email']
        password_hash = request.form['password']

        verification_token = str(secrets.randbelow(900000) + 100000)
        token_expiration = datetime.now(timezone.utc) + timedelta(hours=24)

        phone_number = request.form['phone_number']
        profile_file = request.files['profile_url']
            
        image_url = upload_image_to_bucket(profile_file) if profile_file else None

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            birth_date=birth_date,
            address=address,
            course=course,
            email=email,
            verification_token=verification_token,
            token_expiration=token_expiration,
            phone_number=phone_number,
        )
        if image_url:
            new_user.set_profile_url(image_url)
        new_user.set_password(password_hash)
        db.session.add(new_user)
        db.session.flush()
        db.session.commit()
        
        if(send_secret_via_email(email,verification_token)):

            access_token = create_access_token(identity=str(new_user.account_id),additional_claims={
                "verification_token": verification_token,
                "email":email},expires_delta=timedelta(hours=1))
            
            response = make_response(jsonify({
                "success": True,
                "message": f"Hi there welcome {first_name}",
                "payload": {
                    "access_token": access_token
                }
            }))
            
            return response
        else:
           raise Exception("Failed to send verification email")
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    

@auth_bp.put('/verify-account')
def verify_user():
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        verification_token = data.get('verification_token')

        if not account_id or not verification_token:
            return jsonify({"success": False, "error": "Missing account ID or verification token"}), 400

        user = User.query.filter_by(account_id=account_id, verification_token=verification_token).first()

        if not user:
            return jsonify({"success": False, "error": "Invalid verification token or account ID"}), 404

        if user.token_expiration.tzinfo is None:
            user.token_expiration = user.token_expiration.replace(tzinfo=timezone.utc)
        
        if user.token_expiration < datetime.now(timezone.utc):
            return jsonify({"success": False, "error": "Verification token expired"}), 400

        user.is_verified = True
        user.verification_token = None
        user.token_expiration = None
        db.session.commit()

        access_token = create_access_token(identity=str(account_id))

        response = make_response(jsonify({
            "success": True,
            "message": "Account verified successfully",
            "payload": {
                "access_token": access_token
            }
        }), 200)

        return response
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
    
@auth_bp.post('/sign-in')
def login():
    try:
        email = request.form['email']
        password_hash = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user.verify_password(str(password_hash)):
            return jsonify({"success": False, "error": "Passwords do not match"}), 400
        
        access_token = create_access_token(identity=str(user.account_id),expires_delta=timedelta(days=1))
        response = make_response(jsonify({
                "success": True,
                "payload": {
                    "role": str(user.role.value),
                     "access_token": access_token
                },
                "message": f"Hi there welcome {user.first_name}"
        }))

        return response
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500