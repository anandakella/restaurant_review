from sqlalchemy.engine import Engine
from sqlalchemy import event, CheckConstraint, and_, func
from datetime import datetime
import default_settings
from . import db, app

# Sqlite doesnt support foreign key by default
# Below code is logic is taken from
# https://stackoverflow.com/questions/31794195/
# how-to-correctly-add-foreign-key-constraints-to-sqlite-db-using-sqlalchemy
@event.listens_for(Engine, "connect")
def enable_pragma(connection, connection_record):
    if app.config['DB_TYPE'] == 'SQLITE':
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.String(35), nullable=False)
    last = db.Column(db.String(35), nullable=False)
    phone = db.Column(db.String(35), unique=True, nullable=False)

    def __init__(self, first, last, phone):
        self.first = first
        self.last = last
        self.phone = phone
    
    @classmethod
    def create(cls, first, last, phone):
        result = cls(first, last, phone)
        db.session.add(result)
        db.session.commit()
        return result

    @classmethod
    def query_by_phone(cls, phone):
        return cls.query.filter(cls.phone==phone).first()

    @classmethod
    def query_user_by(cls, user_id=None):
        if user_id:
            return cls.query.filter(cls.id==user_id).first_or_404()
        else:
            return cls.query.all()

    def __repr__(self):
        return '<User first=%s last=%s phone=%s>' % (self.first,
            self.last, self.phone)

class Restaurant(db.Model):
    __tablename__ = 'Restaurant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    addresses =  db.relationship('Address', backref='restaurant', lazy='dynamic')
    ratings =  db.relationship('Rating', backref='restaurant', lazy='dynamic')
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow(),\
                onupdate=datetime.utcnow())

    def __init__(self, name, category):
        self.name = name
        self.category = category

    @classmethod
    def create(cls, name, category):
        result = cls(name, category)
        db.session.add(result)
        db.session.commit()
        return result

    @classmethod
    def update(cls, restaurant_id, name=None, category=None):
        result = cls.query.filter(cls.id==restaurant_id).first_or_404()
        if name:
            result.name = name
        if category:
            result.category = category
        db.session.commit()
        return result

    @classmethod
    def get_restaurant_by_name(cls, name):
        return cls.query.filter(cls.name.ilike('%{}%'.format(name))).\
                join(Address).add_columns(cls.name, cls.category,\
                Address.address, Address.city, Address.state, Address.zip_code).all()
    @classmethod
    def get_restaurant_by_category(cls, category):
        return cls.query.filter(cls.category.ilike('%{}%'.format(category))).\
                join(Address).add_columns(cls.name, cls.category,\
                Address.address, Address.city, Address.state, Address.zip_code).all()

    @classmethod
    def get_restaurant_by_city(cls, city):
        return cls.query.join(Address).add_columns(cls.name, cls.category,\
                Address.address, Address.city, Address.state, Address.zip_code).\
                filter(Address.city.ilike('%{}%'.format(city))).all()

    @classmethod
    def get_restaurant_by_total_score(cls, category, city, total_score):
        response_list = list()
        results = cls.query.filter(cls.category.ilike('%{}%'.format(category))).\
                    join(Address).add_columns(cls.name, cls.category,\
                    Address.address, Address.city, Address.state, Address.zip_code, cls.id).\
                    filter(Address.city.ilike('%{}%'.format(city))).all()
        app.logger.debug('Results:{}'.format(results))
        for result in results:
            new_dict = dict()
            avg_score, = Rating.query.with_entities(func.avg(Rating.total_score)).\
                        filter(Rating.restaurant_id==result.id)[0]
            app.logger.debug('avg_score:{}'.format(avg_score))
            avg_score = round(avg_score, 2)
            if avg_score >= total_score:
                new_dict = {'Name':result.name, 'Category':result.category, 'Address': result.address,
                            'City': result.city, 'State': result.state,
                            'Zip_code': result.zip_code, 'total_score': avg_score}
                response_list.append(new_dict)
        return response_list

    def __repr__(self):
        return '<Restaurant name=%s category=%s>' % (self.name,
            self.category)


class Address(db.Model):
    __tablename__ = 'Address'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(35), nullable=False)
    city = db.Column(db.String(35), nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    restaurant_id  = db.Column(db.Integer, db.ForeignKey('Restaurant.id'))

    def __init__(self, address, state, city, zip_code, restaurant):
        self.address = address
        self.state = state
        self.city = city
        self.zip_code = zip_code
        self.restaurant = restaurant
    
    @classmethod
    def create(cls, address, state, city, zip_code, restaurant):
        address = cls(address, state, city, zip_code, restaurant)
        db.session.add(address)
        db.session.commit()
        return address

    @classmethod
    def get_address_by(cls, restaurant_id=None):
        if restaurant_id:
            return cls.query.filter(cls.restaurant_id == restaurant_id).all()
        else:
            return cls.query.all()

    def __repr__(self):
        return '<Address address=%s state=%s city=%s \
                zip_code=%d restaurant_id=%d>' % (self.address, self.state,\
                self.city, self.zip_code, self.restaurant_id)

class Rating(db.Model):
    __tablename__ = 'Rating'
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Integer, nullable=False)
    food = db.Column(db.Integer, nullable=False)
    cleanliness = db.Column(db.Integer, nullable=False)
    service = db.Column(db.Integer, nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    restaurant_id = db.Column(db.Integer, db.ForeignKey('Restaurant.id'))
    user_id =  db.Column(db.Integer, db.ForeignKey('User.id'))

    __table_args__ = (
            CheckConstraint(and_(cost >= 1, cost <= 5)),
            CheckConstraint(and_(food >= 1, food <= 5)),
            CheckConstraint(and_(cleanliness >= 1, cleanliness <= 5)),
            CheckConstraint(and_(service >= 1, service <= 5))
    )

    def __init__(self, cost, food, cleanliness, service, restaurant_id, user_id):
        self.cost = cost
        self.food = food
        self.cleanliness = cleanliness
        self.service = service
        self.update_score()
        self.restaurant_id = restaurant_id
        self.user_id = user_id

    def update_score(self):
        self.total_score = float(self.cost + self.food + \
            self.cleanliness + self.service)/float(4)

    @classmethod
    def create(cls, food, cost, cleanliness, service, restaurant_id, user_id):
        result = cls.query.filter(and_(cls.restaurant_id == restaurant_id, \
                    cls.user_id==user_id)).first()
        app.logger.debug('Result: {}'.format(result))
        if result:
            diff = (datetime.utcnow() - result.created_on).total_seconds()
            if diff > default_settings.RATINGS_USER_WAIT_TIME_IN_SECONDS:
                rating = cls(cost, food, cleanliness,\
                        service, restaurant_id, user_id)
                db.session.add(rating)
                db.session.commit()
                return rating
            else:
                return False
        else:
            rating = cls(cost, food, cleanliness,\
                        service, restaurant_id, user_id)
            db.session.add(rating)
            db.session.commit()
            return rating

    @classmethod
    def update(cls, food, cost, cleanliness, service, restaurant_id, user_id):
        result = cls.query.filter(and_(cls.restaurant_id==restaurant_id,\
            cls.user_id==user_id)).first_or_404()
        result.cost = cost
        result.cleanliness = cleanliness
        result.service = service
        result.food = food
        db.session.commit()
        return result

    @classmethod
    def query_rating_by_user(cls, user_id):
        results = cls.query.join(Restaurant, Address).add_columns(Restaurant.name, \
            Restaurant.category, Address.address, Address.city, Address.state, cls.cost, \
            cls.food, cls.cleanliness, cls.service, cls.restaurant_id, cls.user_id, cls.total_score).\
            filter(cls.user_id==user_id).filter(Restaurant.id==cls.restaurant_id).\
            filter(Address.restaurant_id==cls.restaurant_id).all()
        return results
        
    def __repr__(self):
        return '<Rating cost=%d food=%d cleanliness=%d \
                service=%d total_score=%d user_id=%d \
                created_on=%s restaurant_id=%d>' % (self.cost,
            self.food, self.cleanliness, self.service, self.total_score,
            self.user_id, self.created_on, self.restaurant_id)

class Posts(db.Model):
    __tablename__ = 'Posts'
    id = db.Column(db.Integer, primary_key=True)
    comments = db.Column(db.String(255), nullable=True)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    updated_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow(),\
                onupdate=datetime.utcnow())
    restaurant_id = db.Column(db.Integer, db.ForeignKey('Restaurant.id'))
    user_id =  db.Column(db.Integer, db.ForeignKey('User.id'))

    def __init__(self, comments, user_id, restaurant_id):
        self.comments = comments
        self.user_id = user_id
        self.restaurant_id = restaurant_id

    @classmethod
    def create(cls, comments, user_id, restaurant_id):
        result = cls(comments, user_id, restaurant_id)
        db.session.add(result)
        db.session.commit()
        return result

    def __repr__(self):
        return '<Posts comments=%s>' % (self.comments)