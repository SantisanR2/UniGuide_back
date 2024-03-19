from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/prueba'
app.config['JWT_SECRET_KEY'] = 'somos_unos_cracks'

db = SQLAlchemy(app)
jwt = JWTManager(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    coordinate = db.Column(db.String(60), nullable=False)
    direction = db.Column(db.String(120), nullable=False)
    img = db.Column(db.String(120), nullable=True)
    type = db.Column(db.String(80), nullable=False)
    counter = db.Column(db.Integer, default=0)

    def __init__(self, name, description, coordinate, direction, img, type):
        self.name = name
        self.description = description
        self.coordinate = coordinate
        self.direction = direction
        self.type = type

class PlaceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Place

place_schema = PlaceSchema()
places_schema = PlaceSchema(many=True)

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = User.query.filter_by(email=email, password=password).first()
    if user is None:
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200

@app.route('/user', methods=['POST'])
def add_user():
    email = request.json['email']
    name = request.json['name']
    password = request.json['password']
    new_user = User(email, name, password)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    email = request.json['email']
    name = request.json['name']
    password = request.json['password']
    user.password = password
    user.name = name
    user.email = email
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/place', methods=['POST'])
def add_place():
    name = request.json['name']
    description = request.json['description']
    coordinate = request.json['coordinate']
    direction = request.json['direction']
    img = request.json['img']
    type = request.json['type']
    new_place = Place(name, description, coordinate, direction, img, type)
    db.session.add(new_place)
    db.session.commit()
    return place_schema.jsonify(new_place)

@app.route('/place', methods=['GET'])
def get_places():
    all_places = Place.query.all()
    result = places_schema.dump(all_places)
    return jsonify(result)

@app.route('/place/<id>', methods=['GET'])
def get_place(id):
    place = Place.query.get(id)
    place.counter += 1
    db.session.commit()
    return place_schema.jsonify(place)

@app.route('/place/<id>', methods=['PUT'])
def update_place(id):
    place = Place.query.get(id)
    name = request.json['name']
    description = request.json['description']
    coordinate = request.json['coordinate']
    direction = request.json['direction']
    img = request.json['img']
    type = request.json['type']
    place.name = name
    place.description = description
    place.coordinate = coordinate
    place.direction = direction
    place.img = img
    place.type = type
    db.session.commit()
    return place_schema.jsonify(place)

@app.route('/place/<id>', methods=['DELETE'])
def delete_place(id):
    place = Place.query.get(id)
    db.session.delete(place)
    db.session.commit()
    return place_schema.jsonify(place)

@app.route('/top3places', methods=['GET'])
def get_top3_places():
    top3_places = Place.query.order_by(Place.counter.desc()).limit(3).all()
    result = places_schema.dump(top3_places)
    return jsonify(result)

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'hello': 'world'}), 200

if __name__ == '__main__':
    app.run(debug=True)
