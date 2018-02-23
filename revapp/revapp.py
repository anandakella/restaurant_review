from flask import Flask, request, current_app, Blueprint, jsonify, make_response
from models import (enable_pragma,
                    User, Address,
                    Restaurant, Rating)
from utils import to_string, sanitize_number, json_response
from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload
from . import app, db

main = Blueprint('main', __name__)

@main.route('/user', methods=['GET', 'POST'])
@main.route('/user/<int:user_id>', methods=['GET'])
def user(user_id=None):
    if request.method == 'POST':
        app.logger.debug('Args: {}'.format(request.args))
        first = to_string(request.args.get('firstName', ''))
        last = to_string(request.args.get('lastName', ''))
        phone = to_string(request.args.get('phoneNum', ''))
        if not first or not last or not phone:
            return json_response({'response': \
                'Either firstName or lastName or phoneNum missing in params '}, 400)
        phone = sanitize_number(phone)
        user_query = User.query_by_phone(phone=phone)
        if not user_query:
            user = User.create(first, last, phone)
            return json_response({'response': 'Created', 'id': user.id})
        else:
            return json_response({'response': 'User with above phone is already registered', \
                'id': user_query.id}, status_code=400)
    elif request.method == 'GET':
        if user_id:
            user = User.query_user_by(user_id)
            app.logger.debug('user: {}'.format(user))
            return jsonify(firtname=user.first,
                lastname=user.last,
                phone=user.phone,
                id=user.id)
        else:
            response_list = list()
            users = User.query_user_by()
            app.logger.debug('user: {}'.format(users))
            if users:
                for user in users:
                    response_list.append({'first':user.first,
                        'last':user.last, 'phone':user.phone,
                        'id':user.id})
            return json_response(response_list)

@main.route('/restaurant', methods=['POST'])
@main.route('/restaurant/<int:restaurant_id>', methods=['PUT'])
def restaurant(restaurant_id=None):
    app.logger.debug('Args: {}'.format(request.args))
    restaurant_name = to_string(request.args.get('name', ''))
    category = to_string(request.args.get('category', ''))
    if request.method == 'POST':
        if not restaurant_name or not category:
            return json_response({'response':'Either name or category is missing in params'}, 400)
        result = Restaurant.create(restaurant_name, category)
        return json_response({'response': 'Created', 'id': result.id})
    elif request.method == 'PUT':
        # restaurant_id = int(request.args.get('id', ''))
        app.logger.debug('Restaurant_id: {}'.format(restaurant_id))
        if not restaurant_name and not category:
            json_response({'response':'Either name or category is missing in params'}, 400)
        result = Restaurant.update(restaurant_id, restaurant_name, category)
        app.logger.debug('result: {}'.format(result))
        return json_response({'response': 'Updated', 'id': result.id})
    else:
        return json_response({'response':'BAD Request'}, 400)

@main.route('/restaurant/<name>')
@main.route('/restaurant/category/<category>')
@main.route('/restaurant/city/<city>')
def get_restaurant_by(name=None, category=None, city=None):
    response_list = list()
    if name:
        results = Restaurant.get_restaurant_by_name(name)
    if category:
        results = Restaurant.get_restaurant_by_category(category)
    if city:
        results = Restaurant.get_restaurant_by_city(city)
    app.logger.debug('Results:{}'.format(results))
    for result in results:
        response_list.append({'Name':result.name, 'Category':result.category,
        'Address': result.address, 'City': result.city, 'State': result.state,
        'Zip_code': result.zip_code})
    return json_response(response_list)

@main.route('/restaurant/<category>/<city>/<float:total_score>')
def restaurant_profile( category, city, total_score):
    """
    Get Restaurant(s) by name/ city/ category/ total score
    Example: Find Mexican restaurant(s) in San Jose (or zip code) with total score above 3 star
    Working query
    avg_score, = Rating.query.with_entities(func.avg(Rating.total_score)).\
        filter(Rating.restaurant_id==restaurant_id)[0]
    app.logger.debug('results: {}'.format(avg_score))
    WIP:
    results = Rating.query.with_entities(func.avg(Rating.total_score) >= total_score).\
            join(Restaurant, Address).filter(Restaurant.category.ilike('%{}%'.format(category))).\
            filter(Address.city.ilike('%{}%'.format(city)))[0]
    The below solution is hacky way listing restaurant by >= total_score. 
    Im sure there is sql command need to investigate.
    """
    return jsonify(Restaurant.get_restaurant_by_total_score(category, city, total_score))

@main.route('/address', methods=['POST', 'GET'])
def address():
    if request.method == 'POST':
        app.logger.debug('Args: {}'.format(request.args))
        restaurant_id = int(request.args.get('restaurant_id', ''))
        address = to_string(request.args.get('address',''))
        state = to_string(request.args.get('state',''))
        city = to_string(request.args.get('city', ''))
        zip_code = int(request.args.get('zip', ''))
        r = Restaurant.query.filter(Restaurant.id==restaurant_id).first_or_404()
        address = Address.create(address, state, city, zip_code, restaurant=r)
        return json_response({'response': 'Created', 'id': address.id})
    elif request.method == 'GET':
        response_list = list()
        restaurant_id = int(request.args.get('restaurant_id', 0))
        results = Address.get_address_by(restaurant_id)
        app.logger.debug('Address: {}'.format(results))
        if results:
            for result in results:
                response_list.append({'address':result.address, 'state':result.state,
                    'city': result.city, 'restaurant_id': result.restaurant_id,
                    'id':result.id})
        return json_response(response_list)

@main.route('/rating', methods=['POST', 'PUT'])
def rating():
    app.logger.debug('Args: {}'.format(request.args))
    cost = float(request.args.get('cost', 0))
    cleanliness = float(request.args.get('cleanliness', 0))
    service = float(request.args.get('service', 0))
    food = float(request.args.get('food', 0))
    user_id = int(request.args.get('user_id', 0))
    restaurant_id = int(request.args.get('restaurant_id', 0))
    r = Restaurant.query.filter_by(id=restaurant_id).first_or_404()
    user = User.query.filter_by(id=user_id).first_or_404()
    if request.method == 'POST':
        rating = Rating.create(cost, food, cleanliness,\
                service, restaurant_id, user_id)
        if rating:
            return json_response({'response': 'Created', 'id': rating.id})
        else:
            return json_response({'response': 'Cannot post within a month for same restaurant'}, 400)
    elif request.method == 'PUT':
        result = Rating.update(cost, food, cleanliness,\
                service, restaurant_id, user_id)
        return json_response({'response': 'Updated', 'id': result.id})

@main.route('/rating/user/<int:user_id>')
def get_rating_by_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    response_list = list()
    results = Rating.query_rating_by_user(user_id)
    app.logger.debug('Rating: {}'.format(results))
    if results:
        for result in results:
            response_list.append({'Cost':result.cost, 'Food':result.food,
                'Service': result.service, 'Cleanliness': result.cleanliness,
                'Total_score': result.total_score, 'Restaurant_name': result.name,
                'Restaurant_category': result.category, 'Address': result.address, 
                'City': result.city, 'State': result.state, 'Restaurant_id': result.restaurant_id})
    return jsonify(response_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')