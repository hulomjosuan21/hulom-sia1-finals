from langchain.tools import tool
from src.models.assignment import Assignment, AssignmentAssignee
from src.models.users import User
from src.extensions import db
from sqlalchemy import or_
from datetime import datetime
from uuid import UUID


class AgentTool:
    @staticmethod
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
            return [user.to_dict() for user in users] if users else []
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _resolve_student_ids(keyword: str):
        """Helper method to return list of student UUID strings by keyword or all if 'all'."""
        try:
            keyword = (keyword or "").strip().lower()
            query = User.query.filter(User.role == "Student")

            if keyword and keyword != "all":
                query = query.filter(
                    or_(
                        User.first_name.ilike(f"%{keyword}%"),
                        User.last_name.ilike(f"%{keyword}%"),
                        User.email.ilike(f"%{keyword}%")
                    )
                )
            users = query.all()
            return [str(user.user_id) for user in users] if users else []
        except Exception:
            return []

    @staticmethod
    @tool("AddAssignmentAndAssign")
    def add_assignment_and_assign(input_text: str) -> str:
        """
        Create an assignment and assign it to students by keyword or 'all'.

        Expected input format (semicolon-separated key:value pairs):
          title:<title>; description:<desc>; due_date:<ISO date>; created_by:<uuid>; assigned_to_keyword:<keyword|all>

        Example:
          title: Homework 1; description: Solve exercises; due_date: 2025-06-01T23:59:00; created_by: f573cb39-6b5a-4335-8c2c-d77b...; assigned_to_keyword: all
        """
        try:
            # Parse input_text into dict
            fields = {}
            for part in input_text.split(';'):
                if ':' not in part:
                    continue
                key, val = part.split(':', 1)
                fields[key.strip()] = val.strip()

            required_fields = ['title', 'description', 'due_date', 'created_by']
            missing = [f for f in required_fields if f not in fields or not fields[f]]
            if missing:
                return f"Error: Missing fields: {', '.join(missing)}"

            due_date = datetime.fromisoformat(fields['due_date'])

            assignment = Assignment(
                title=fields['title'],
                description=fields['description'],
                due_date=due_date,
                created_by=fields['created_by']
            )
            db.session.add(assignment)
            db.session.flush()

            assigned_to_keyword = fields.get('assigned_to_keyword', '')
            assigned_to_ids = []
            if assigned_to_keyword:
                assigned_to_ids = AgentTool._resolve_student_ids(assigned_to_keyword)

            assignees = []
            if assigned_to_ids:
                assignees = [
                    AssignmentAssignee(
                        assignment_id=assignment.assignment_id,
                        assigned_by_id=fields['created_by'],
                        assigned_to_id=UUID(user_id)
                    )
                    for user_id in assigned_to_ids
                ]
                db.session.add_all(assignees)

            db.session.commit()
            return f"Assignment '{assignment.title}' created and assigned to {len(assignees)} student(s)."
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"

    @staticmethod
    @tool("DeleteAssignment")
    def delete_assignment(input_text: str) -> str:
        """Delete assignments by keyword in title or description."""
        try:
            keyword = input_text.strip()
            if not keyword:
                return "Error: Provide a keyword."

            assignments = Assignment.query.filter(
                or_(
                    Assignment.title.ilike(f"%{keyword}%"),
                    Assignment.description.ilike(f"%{keyword}%")
                )
            ).all()

            if not assignments:
                return f"No assignments found matching '{keyword}'."

            for assignment in assignments:
                db.session.delete(assignment)
            db.session.commit()
            return f"Deleted {len(assignments)} assignment(s)."
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"

    @staticmethod
    @tool("UpdateAssignment")
    def update_assignment(input_text: str) -> str:
        """
        Update assignment(s) using the format:
        keyword | new_title | new_description | new_due_date (YYYY-MM-DD HH:MM)

        Only fields with values will be updated. If you leave any blank, it will remain unchanged.
        """
        try:
            parts = [p.strip() for p in input_text.split('|')]
            if len(parts) != 4:
                return "Error: Input must be: keyword | new_title | new_description | new_due_date"

            keyword, new_title, new_desc, new_due = parts

            assignments = Assignment.query.filter(
                or_(
                    Assignment.title.ilike(f"%{keyword}%"),
                    Assignment.description.ilike(f"%{keyword}%")
                )
            ).all()

            if not assignments:
                return f"No assignments found matching keyword '{keyword}'."

            updated_count = 0
            for assignment in assignments:
                if new_title:
                    assignment.title = new_title
                if new_desc:
                    assignment.description = new_desc
                if new_due:
                    try:
                        parsed_due = datetime.strptime(new_due, "%Y-%m-%d %H:%M")
                        assignment.due_date = parsed_due
                    except ValueError:
                        return "Error: Invalid date format. Use YYYY-MM-DD HH:MM."

                updated_count += 1

            db.session.commit()
            return f"Updated {updated_count} assignment(s)."
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
