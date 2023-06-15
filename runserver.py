from api.v1 import create_app, db
from api.v1.config.config import config_dict

app = create_app(config=config_dict['dev'])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
