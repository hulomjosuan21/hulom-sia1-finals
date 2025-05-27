from flask import request, jsonify, Blueprint
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agent.tools import AgentTool
import os

load_dotenv()

agent_dp = Blueprint("agent_dp",__name__)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

tools = [
    AgentTool.lookup_user,
    AgentTool.add_assignment_and_assign,
    AgentTool.delete_assignment,
    AgentTool.update_assignment
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

@agent_dp.post("/text")
def text_agent():
    try:
        data = request.get_json()
        created_by = data.get("created_by")
        query = data.get("query", "").strip()

        if not query:
            return jsonify({
                "success": False,
                "message": "Missing 'query' in request",
                "payload": None
            }), 400

        full_query = f"{query} (created_by: {created_by})"

        result = agent.run(full_query)

        try:
            payload = eval(result) if isinstance(result, str) and result.startswith("[") else result
        except Exception:
            payload = result

        return jsonify({
            "success": True,
            "payload": payload,
            "message": f"Query completed: {query}"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Agent error occurred",
            "payload": str(e)
        }), 500

from datetime import datetime
from langchain.tools import tool
from src.models.assignment import Assignment, AssignmentAssignee
from src.models.users import User
from src.extensions import db

class AgentTool:
    @tool("LookupUser")
    def lookup_user(input_text: str):
        """Look up a user by name or email. If input is empty, return all users."""
        try:
            keyword = input_text.strip()
            if not keyword:
                users = User.query.all()
            else:
                users = User.query.filter(
                    (User.name.ilike(f"%{keyword}%")) |
                    (User.email.ilike(f"%{keyword}%"))
                ).all()

            user_dicts = [user.to_dict() for user in users]

            return user_dicts[0] if len(user_dicts) == 1 else user_dicts

        except Exception as e:
            return {"error": str(e)}
        
    @tool("AddAssignmentAndAssign")
    def add_assignment_and_assign(input_data: dict) -> str:
        """
        Create a new assignment and assign it to users.
        Input format:
        {
            "title": str,
            "description": str,
            "due_date": str (ISO format: "YYYY-MM-DDTHH:MM:SS"),
            "assigned_to_ids": list of int  # from LookupUser
        }
        Note: `created_by` is set automatically to the name of the prompt user.
        """
        from datetime import datetime

        try:
            required_fields = ['title', 'description', 'due_date', 'assigned_to_ids']
            missing = [f for f in required_fields if f not in input_data or input_data[f] in (None, '', [])]
            if missing:
                return f"Error: Missing required field(s): {', '.join(missing)}"

            created_by = "You" 
            title = input_data['title']
            description = input_data['description']
            due_date_str = input_data['due_date']
            assigned_to_ids = input_data['assigned_to_ids']

            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                return "Error: Invalid due_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."

            new_assignment = Assignment(
                created_by=created_by,
                title=title,
                description=description,
                due_date=due_date
            )
            db.session.add(new_assignment)
            db.session.flush()

            assignment_id = new_assignment.assignment_id

            assignees = [
                AssignmentAssignee(
                    assignment_id=assignment_id,
                    assigned_by_id=created_by,
                    assigned_to_id=user_id
                ) for user_id in assigned_to_ids
            ]
            db.session.add_all(assignees)
            db.session.commit()

            return f"Assignment '{title}' created by you and assigned to {len(assigned_to_ids)} user(s)."

        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"

    @tool("DeleteAssignment")
    def delete_assignment(input_text: str) -> str:
        """
        Delete assignment(s) by matching title or description.
        Input is matched partially (case-insensitive).
        """
        try:
            keyword = input_text.strip()
            if not keyword:
                return "Error: Please provide a title or description to delete assignments."

            like_pattern = f"%{keyword}%"
            assignments = Assignment.query.filter(
                (Assignment.title.ilike(like_pattern)) |
                (Assignment.description.ilike(like_pattern))
            ).all()

            if not assignments:
                return "No assignments matched your criteria."

            count = len(assignments)
            for assignment in assignments:
                db.session.delete(assignment)
            db.session.commit()

            return f"Deleted {count} assignment{'s' if count > 1 else ''} matching '{keyword}'."

        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
        
    @tool("UpdateAssignment")
    def update_assignment(input_text: str) -> str:
        """
        Update assignment(s) by matching title or description.
        Input format: keyword | new_title | new_description | new_due_date (YYYY-MM-DD HH:MM)
        Any of the new fields can be left empty to skip updating that field.
        """
        from datetime import datetime

        try:
            parts = [p.strip() for p in input_text.split('|')]
            if len(parts) != 4:
                return "Error: Input must be in the format 'keyword | new_title | new_description | new_due_date'."

            keyword, new_title, new_description, new_due_date = parts
            if not keyword:
                return "Error: Please provide a keyword to match assignments."

            like_pattern = f"%{keyword}%"
            assignments = Assignment.query.filter(
                (Assignment.title.ilike(like_pattern)) |
                (Assignment.description.ilike(like_pattern))
            ).all()

            if not assignments:
                return "No assignments matched your criteria."

            parsed_due_date = None
            if new_due_date:
                try:
                    parsed_due_date = datetime.strptime(new_due_date, "%Y-%m-%d %H:%M")
                except ValueError:
                    return "Error: Invalid due_date format. Use 'YYYY-MM-DD HH:MM'."

            count = 0
            for assignment in assignments:
                if new_title:
                    assignment.title = new_title
                if new_description:
                    assignment.description = new_description
                if parsed_due_date:
                    assignment.due_date = parsed_due_date
                count += 1

            db.session.commit()
            return f"Updated {count} assignment{'s' if count > 1 else ''} matching '{keyword}'."

        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"