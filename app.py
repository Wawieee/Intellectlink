from app import create_app
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask_wtf.csrf import CSRFProtect



load_dotenv('.env')
app = create_app()
csrf = CSRFProtect(app)
csrf.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)