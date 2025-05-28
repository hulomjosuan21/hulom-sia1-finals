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

        full_query = f"{query}. The created_by is '{created_by}'."

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
