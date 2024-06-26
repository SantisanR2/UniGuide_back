from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from sqlalchemy.sql import func
from flask_marshmallow import Marshmallow
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://UniGuide:Moviles12345@UniGuide.mysql.pythonanywhere-services.com/UniGuide$db'
app.config['JWT_SECRET_KEY'] = 'somos_unos_cracks'

db = SQLAlchemy(app)
jwt = JWTManager(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)
    suggestions = db.relationship('Suggestion', backref='user', lazy=True)
    preferences = db.relationship('UserPreferences', backref='user', uselist=False)

    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    coordinate = db.Column(db.String(60), nullable=False)
    direction = db.Column(db.String(120), nullable=False)
    img = db.Column(db.String(120), nullable=True)
    type = db.Column(db.String(80), nullable=False)
    counter = db.Column(db.Integer, default=0)
    reviews = db.relationship('Review', backref='place', lazy=True)
    suggestions = db.relationship('Suggestion', backref='place', lazy=True)

    def __init__(self, name, description, coordinate, direction, img, type):
        self.name = name
        self.description = description
        self.coordinate = coordinate
        self.direction = direction
        self.img = img
        self.type = type

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)

    def __init__(self, user_id, place_id):
        self.user_id = user_id
        self.place_id = place_id

class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type_places = db.Column(db.String(100))
    review_places = db.Column(db.String(100))
    counter_places = db.Column(db.String(100))

    def __init__(self, user_id, type_places, review_places, counter_places):
        self.user_id = user_id
        self.type_places = type_places
        self.review_places = review_places
        self.counter_places = counter_places

class Review(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    rating = db.Column(db.Integer,nullable=False)
    comment = db.Column(db.String(700), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable=False)
    init_date = db.Column(db.Date, nullable=False)
    
    def __init__(self, rating, comment, user_id, place_id, init_date):
        self.rating = rating
        self.comment = comment
        self.user_id = user_id
        self.place_id = place_id
        self.init_date = init_date

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class ReviewSchema(ma.SQLAlchemyAutoSchema):
    user_id = ma.auto_field()
    place_id = ma.auto_field()
    class Meta:
        model = Review

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many = True)

class SuggestionsSchema(ma.SQLAlchemyAutoSchema):
    user_id = ma.auto_field()
    place_id = ma.auto_field()
    class Meta:
        model = Suggestion
    
suggestions_schema = SuggestionsSchema()
suggestions_schema = SuggestionsSchema(many=True)

class UserPreferencesSchema(ma.SQLAlchemyAutoSchema):
    user_id = ma.auto_field()
    class Meta:
        model = UserPreferences

user_preferences_schema = UserPreferencesSchema()
user_preferences_schema = UserPreferencesSchema(many=True)

class PlaceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Place

place_schema = PlaceSchema()
places_schema = PlaceSchema(many=True)

class FeatureCounters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature = db.Column(db.Integer, nullable=False)
    counter = db.Column(db.Integer, default=0)

class FeatureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FeatureCounters

features_schema = FeatureSchema(many=True)

class AndroidDistribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(120), nullable=False)
    android = db.Column(db.String(120), nullable=False)

    def __init__(self, device, android):
        self.device = device
        self.android = android

class AndroidDistributionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AndroidDistribution

android_distribution_schema = AndroidDistributionSchema()
android_distributions_schema = AndroidDistributionSchema(many=True)

class ViewTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    view = db.Column(db.String(20), nullable=False)
    time = db.Column(db.Integer, default=0)

class ViewTimeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ViewTime

viewTimeSchema = ViewTimeSchema(many = True)


@app.route('/view', methods=['POST'])
def add_time_view():
    view_name= request.json['view']
    time = request.json['time']
    view = ViewTime.query.filter_by(view = view_name).first()
    if not view:
        view = ViewTime(view = view_name)
    view.time+=time
    db.session.add(view)
    db.session.commit()
    return jsonify({"message": f"El tiempo de la vista {view_name} ha sido actualizado correctamente."})

@app.route('/view', methods=['GET'])
def get_time_view():
    all_views = ViewTime.query.all()
    result = viewTimeSchema.dump(all_views)
    return jsonify(result)


@app.route('/distribution', methods=['POST'])
def add_distribution():
    device = request.json['device']
    android = request.json['android']
    new_distribution = AndroidDistribution(device, android)
    db.session.add(new_distribution)
    db.session.commit()
    return android_distribution_schema.jsonify(new_distribution)

@app.route('/distribution', methods=['GET'])
def get_distributions():
    all_distributions = AndroidDistribution.query.all()
    result = android_distributions_schema.dump(all_distributions)
    return jsonify(result)

@app.route('/feature', methods=['POST'])
def actualizar_contador():
    try:
        data = request.get_json()
        feature = data.get('feature')

        if feature:
            counter = FeatureCounters.query.filter_by(feature=feature).first()
            if not counter:
                counter = FeatureCounters(feature=feature)

            counter.counter += 1
            db.session.add(counter)
            db.session.commit()

            return jsonify({"message": f"Contador para feature {feature} actualizado correctamente."})
        else:
            return jsonify({"error": "Feature no válida. Debe ser un número."}), 400
    except Exception as e:
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500
    
@app.route('/feature', methods=['GET'])
def get_cont():
    features = FeatureCounters.query.all()
    result = features_schema.dump(features)
    return jsonify(result)

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

    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "access_token": create_access_token(identity=email)
    }

    return jsonify(user_data), 200


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

# Endpoints CRUD para Review
@app.route('/review', methods=['POST'])
def add_review():
    Rating = request.json['rating']
    comment = request.json['comment']
    user_id = request.json['user_id']
    place_id = request.json['place_id']
    date = datetime.now()
    date = date.strftime("%Y-%m-%d")


    new_review = Review(rating=Rating, comment=comment, user_id=user_id, place_id=place_id, init_date = date)

    db.session.add(new_review)
    db.session.commit()

    return review_schema.jsonify(new_review)

@app.route('/review/<id>', methods=['PUT'])
def update_review(id):
    review = Review.query.get(id)
    if review:
        review.Rating = request.json['Rating']
        review.comment = request.json['comment']
        review.user_id = request.json['user_id']
        review.place_id = request.json['place_id']

        db.session.commit()

        return review_schema.jsonify(review)
    else:
        return jsonify({'message': 'Review not found'}), 404

@app.route('/review/<id>', methods=['DELETE'])
def delete_review(id):
    review = Review.query.get(id)
    if review:
        db.session.delete(review)
        db.session.commit()
        return jsonify({'message': 'Review deleted'})
    else:
        return jsonify({'message': 'Review not found'}), 404

@app.route('/review', methods=['GET'])
def get_reviews():
    all_reviews = Review.query.all()
    result = reviews_schema.dump(all_reviews)
    return jsonify(result)

# Consulta por lugar
@app.route('/review/place/<place_id>', methods=['GET'])
def get_reviews_by_place(place_id):
    reviews = Review.query.filter_by(place_id=place_id).all()
    result = reviews_schema.dump(reviews)
    return jsonify(result)

# Consulta por usuario
@app.route('/review/user/<user_id>', methods=['GET'])
def get_reviews_by_user(user_id):
    reviews = Review.query.filter_by(user_id=user_id).all()
    result = reviews_schema.dump(reviews)
    return jsonify(result)

# Consulta por ID
@app.route('/review/<id>', methods=['GET'])
def get_review(id):
    review = Review.query.get(id)
    if review:
        return review_schema.jsonify(review)
    else:
        return jsonify({'message': 'Review not found'}), 404
    
@app.route('/place/<place_id>/average_review', methods=['GET'])
def get_average_review(place_id):
    average_rating = db.session.query(func.avg(Review.rating)).filter(Review.place_id == place_id).scalar()
    return jsonify({'average_rating': round(average_rating, 2) if average_rating else 0})

@app.route('/preferences', methods=['POST'])
def add_or_update_user_preferences():
    user_id = request.json['user_id']
    type_places = request.json['type_places']
    review_places = request.json['review_places']
    counter_places = request.json['counter_places']

    existing_preferences = UserPreferences.query.filter_by(user_id=user_id).all()
    exist = False

    for existing_preference in existing_preferences:
        exist = True
        existing_preference.type_places = type_places
        existing_preference.review_places = review_places
        existing_preference.counter_places = counter_places
    if not exist:
        new_user_preferences = UserPreferences(user_id=user_id, type_places=type_places, review_places=review_places, counter_places=counter_places)
        db.session.add(new_user_preferences)

    existing_suggestions = Suggestion.query.filter_by(user_id=user_id).all()
    for suggestion in existing_suggestions:
        db.session.delete(suggestion)

    filtered_places = Place.query.filter_by(type=type_places).all()
    if review_places == 'good':
        filtered_places = [place for place in filtered_places if get_average_rating(place.id) > 4]
    elif review_places == 'bad':
        filtered_places = [place for place in filtered_places if get_average_rating(place.id) > 2]

    if counter_places == 'yes':
        filtered_places.sort(key=lambda place: place.counter, reverse=True)
        filtered_places = filtered_places[:4]

    for place in filtered_places:
        new_suggestion = Suggestion(user_id=user_id, place_id=place.id)
        db.session.add(new_suggestion)

    db.session.commit()

    return user_preferences_schema.jsonify(existing_preferences or new_user_preferences)

def get_average_rating(place_id):
    average_rating = db.session.query(func.avg(Review.rating)).filter(Review.place_id == place_id).scalar()
    return round(average_rating, 2) if average_rating else 0

@app.route('/suggestions/<int:user_id>', methods=['GET'])
def get_user_suggestions(user_id):
    def get_suggestions_for_user(user_id):
        suggestions = Suggestion.query.filter_by(user_id=user_id).all()
        return [place_schema.dump(suggestion.place) for suggestion in suggestions]
    
    def get_top_places(n):
        return place_schema.dump(Place.query.order_by(Place.counter.desc()).limit(n).all())

    suggestions = get_suggestions_for_user(user_id)
    if suggestions.__len__() == 0:
        top_places = get_top_places(3)
        return jsonify(top_places)
    else:
        return jsonify(suggestions)


if __name__ == '__main__':
    app.run(debug=True)

