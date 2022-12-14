#from crypt import methods
import os
from urllib import response
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drink = Drink.query.all()
    drinks = [item.short() for item in drink]

    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload): 
    drink = Drink.query.all()
    drinks = [item.short() for item in drink]

    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    new_drink = Drink(title=new_title, recipe=json.dumps([new_recipe]))
    new_drink.insert()
    drink = new_drink.long()
    #print(payload)
    return jsonify({
        'success': True,
        'drinks': drink
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    body = request.get_json()
    specific_drink = Drink.query.filter(Drink.id == id).one_or_none()

    if specific_drink is None:
        abort(404)

    if 'title' in body:
        specific_drink.title = body.get('title')
        specific_drink.update()

    if 'recipe' in body:
        specific_drink.recipe = body.get('recipe')
        specific_drink.update()

    drinks = Drink.query.filter(Drink.id == id).all()
    for drink in drinks:
        drink = drink.long()

    
    return jsonify({
        'success': True,
        'drinks': drink
    })
    
    

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)
    print(payload)
    drink.delete()
    return jsonify({
        'success': True,
        'delete': id
    })





# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(400)
def bad_request():
    return jsonify({
        "success": False,
        "message": "bad request",
        "error": 400
    }), 400

@app.errorhandler(401)
def unauthorized():
    return jsonify({
        "success": False,
        "message": "unauthorized",
        "error": 401
    }), 401

@app.errorhandler(403)
def forbidden():
    return jsonify({
        "success": False,
        "message": "forbidden",
        "error": 403
    }), 403

@app.errorhandler(404)
def not_found():
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed():
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method_not_allowed"
    }), 405

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
    
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
