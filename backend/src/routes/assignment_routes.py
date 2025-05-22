from flask import Blueprint,request,jsonify
from src.models.assignment import Assignment,AssignmentAssignee,AssignmentAssigneeStatusEnum
from src.extensions import db
assignment_bp = Blueprint('assignment_bp',__name__)

@assignment_bp.post('/add')
async def add_assignment():
    try:
        
        required_fields = ['created_by', 'title', 'description', 'due_date', 'userIDs']
        data = request.get_json()
        missing_fields = [field for field in required_fields if field not in data or data[field] in (None, '')]
        if missing_fields:
            return jsonify({"error": f"Missing required field(s): {', '.join(missing_fields)}"}), 400
        
        data = request.get_json()
        created_by = data.get('created_by')
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        user_ids = data.get('userIDs')
        
        new_assignment = Assignment(title=title,description=description,due_date=due_date,created_by=created_by)
        db.session.add(new_assignment)
        db.session.flush()
        db.session.commit()
        
        user_ids_list = list(user_ids)
        assignment_id = new_assignment.assignment_id
        assigned_by_id = new_assignment.created_by
        
        if len(user_ids_list) > 0:
            for id in user_ids_list:
                new_assignee = AssignmentAssignee(
                    assignment_id=assignment_id,
                    assigned_by_id=assigned_by_id,
                    assigned_to_id=id
                )
                db.session.add(new_assignee)
            
            db.session.commit()
            
        response = jsonify({
            "success": True,
            "message": "Done assigning"
        })
        
        return response
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@assignment_bp.get('/by')
async def get_assignments():
    try:
        created_by = request.args.get('created_by')
        
        assignments = Assignment.query.filter(Assignment.created_by == created_by).all()
        
        response = jsonify({
            "success": True,
            "message": "Done assigning",
            "payload": [assignment.to_dict() for assignment in assignments]
        })
        
        return response
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@assignment_bp.delete('/remove/<string:assignment_id>')
async def delete_assignment(assignment_id):
    try:
        assignment = Assignment.query.filter(Assignment.assignment_id == assignment_id).first()
        if not assignment:
            return jsonify({"success": False, "message": "Assignment not found"}), 404

        db.session.delete(assignment)
        db.session.commit()

        return jsonify({"success": True, "message": f"Assignment {assignment_id} deleted successfully"})
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500
    
@assignment_bp.put('/update/assignee-status/<string:assigned_to_id>')
async def update_assignee_assignment(assigned_to_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        if new_status not in [status.value for status in AssignmentAssigneeStatusEnum]:
            return jsonify({
                "success": False,
                "message": f"Invalid status. Must be one of: {[s.value for s in AssignmentAssigneeStatusEnum]}"
            }), 400

        assignment = AssignmentAssignee.query.filter_by(assigned_to_id=assigned_to_id).first()
        if not assignment:
            return jsonify({
                "success": False,
                "message": "Assignment not found"
            }), 404

        assignment.status = AssignmentAssigneeStatusEnum(new_status)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Assignee status updated to {new_status}"
        }), 200

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500

