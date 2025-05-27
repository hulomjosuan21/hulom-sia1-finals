from langchain.tools import tool
from src.extensions import db
from src.models.users import *
from src.models.assignment import *
from datetime import datetime
from uuid import UUID
from sqlalchemy import or_

class AgentTool:
    @tool("LookupUser")
    def lookup_user(input_text: str):
        """Look up student users by name or email. If input is empty, return all students."""
        try:
            keyword = input_text.strip()
            query = User.query.filter(User.role == "Student")

            if keyword:
                query = query.filter(
                    or_(
                        User.first_name.ilike(f"%{keyword}%"),
                        User.last_name.ilike(f"%{keyword}%"),
                        User.email.ilike(f"%{keyword}%")
                    )
                )

            users = query.all()
            user_dicts = [user.to_dict() for user in users]
            return user_dicts[0] if len(user_dicts) == 1 else user_dicts

        except Exception as e:
            return {"error": str(e)}

    @tool("AddAssignmentAndAssign")
    def add_assignment_and_assign(input_data: dict) -> str:
        """
        Create a new assignment and assign it to users.
        Required keys in input_data:
        - title, description, due_date (ISO format), assigned_to_ids (list of int), created_by (str)
        """
        from datetime import datetime

        try:
            required_fields = ['title', 'description', 'due_date', 'assigned_to_ids', 'created_by']
            missing = [f for f in required_fields if f not in input_data or input_data[f] in (None, '', [])]
            if missing:
                return f"Error: Missing required field(s): {', '.join(missing)}"

            created_by = input_data['created_by']
            title = input_data['title']
            description = input_data['description']
            due_date = datetime.fromisoformat(input_data['due_date'])

            assigned_to_ids = [UUID(uid) for uid in input_data['assigned_to_ids']]

            assignment = Assignment(
                title=title,
                description=description,
                due_date=due_date,
                created_by=created_by
            )
            db.session.add(assignment)
            db.session.flush()

            assignees = [
                AssignmentAssignee(
                    assignment_id=assignment.assignment_id,
                    assigned_by_id=created_by,
                    assigned_to_id=user_id
                ) for user_id in assigned_to_ids
            ]
            if(len(assignees) > 0):
                db.session.add_all(assignees)
            db.session.commit()

            return f"Assignment '{title}' created and assigned to {len(assigned_to_ids)} student(s)."
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"

    @tool("DeleteAssignment")
    def delete_assignment(input_text: str) -> str:
        """
        Delete assignments by title or description keyword.
        Input: keyword (partial match allowed)
        """
        try:
            keyword = input_text.strip()
            if not keyword:
                return "Error: Please provide a keyword to match assignment title/description."

            like_pattern = f"%{keyword}%"
            assignments = Assignment.query.filter(
                or_(
                    Assignment.title.ilike(like_pattern),
                    Assignment.description.ilike(like_pattern)
                )
            ).all()

            if not assignments:
                return f"No assignments found matching '{keyword}'."

            count = len(assignments)
            for assignment in assignments:
                db.session.delete(assignment)
            db.session.commit()

            return f"Deleted {count} assignment(s) matching '{keyword}'."
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"

    @tool("UpdateAssignment")
    def update_assignment(input_text: str) -> str:
        """
        Update assignment(s) by keyword.
        Input format: keyword | new_title | new_description | new_due_date (YYYY-MM-DD HH:MM)
        Leave a field blank to skip updating it.
        """
        try:
            parts = [p.strip() for p in input_text.split('|')]
            if len(parts) != 4:
                return "Error: Input must be: keyword | new_title | new_description | new_due_date"

            keyword, new_title, new_desc, new_due = parts
            if not keyword:
                return "Error: A keyword is required to find assignments."

            like_pattern = f"%{keyword}%"
            assignments = Assignment.query.filter(
                or_(
                    Assignment.title.ilike(like_pattern),
                    Assignment.description.ilike(like_pattern)
                )
            ).all()

            if not assignments:
                return f"No assignments found matching '{keyword}'."

            parsed_due_date = None
            if new_due:
                try:
                    parsed_due_date = datetime.strptime(new_due, "%Y-%m-%d %H:%M")
                except ValueError:
                    return "Error: Invalid due date format. Use 'YYYY-MM-DD HH:MM'."

            count = 0
            for assignment in assignments:
                if new_title:
                    assignment.title = new_title
                if new_desc:
                    assignment.description = new_desc
                if parsed_due_date:
                    assignment.due_date = parsed_due_date
                count += 1

            db.session.commit()
            return f"Updated {count} assignment(s) matching '{keyword}'."
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
