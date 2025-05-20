from src import __initialize__
from dotenv import load_dotenv
from os import getenv

load_dotenv()

port = int(getenv('PORT', 5000))

app = __initialize__()

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=port)