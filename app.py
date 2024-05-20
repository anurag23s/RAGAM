from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_music_app.db'
db.init_app(app)
migrate = Migrate(app, db)


@app.template_filter('average')
def average_filter(ratings):
    if not ratings:
        return 0
    total_ratings = sum([rating.rating for rating in ratings])
    return total_ratings / len(ratings)


from routes import *

if __name__ == '__main__':
    from models import db
    db.create_all()
    app.run(debug=True)
