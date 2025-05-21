from flask import Blueprint, request, jsonify

from src.models.users import User

user_bp = Blueprint("user_bp",__name__)

@user_bp.get('/get-single-obj')
async def get_user():
    try:
        account_id = request.args.get('account_id')
        
        user = User.query.filter(User.account_id == account_id).first()
        
        response = jsonify({
            "success": True,
            "payload": user.to_dict(),
            "message": f"Hi there welcome {user.first_name}"
        })
        
        return response
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500

