#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(jsonify(bakeries), 200)

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    
    if request.method == 'GET':
        if not bakery:
            return make_response(jsonify({"error": "Bakery not found"}), 404)
        bakery_serialized = bakery.to_dict()
        return make_response(jsonify(bakery_serialized), 200)
    
    elif request.method == 'PATCH':
        # Get the name from the form data
        new_name = request.form.get('name')
        
        if not bakery:
            return make_response(jsonify({"error": "Bakery not found"}), 404)
        
        if new_name:
            # Update the bakery's name
            bakery.name = new_name
            
            # Commit the changes to the database
            db.session.commit()
            
            # Return the updated bakery
            return make_response(jsonify(bakery.to_dict()), 200)
        
        # If no name provided, return an error
        return make_response(jsonify({"error": "Name is required"}), 400)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response(jsonify(baked_goods_by_price_serialized), 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response(jsonify(most_expensive_serialized), 200)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    # Get form data
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')
    
    # Validate input
    if not all([name, price, bakery_id]):
        return make_response(jsonify({"error": "Missing required fields"}), 400)
    
    try:
        # Try to find or create the bakery if it doesn't exist
        bakery = Bakery.query.filter_by(id=bakery_id).first()
        if not bakery:
            # If bakery doesn't exist, create a new one
            bakery = Bakery(name=f"Bakery {bakery_id}")
            db.session.add(bakery)
            db.session.commit()
        
        # Create new baked good
        new_baked_good = BakedGood(
            name=name, 
            price=float(price), 
            bakery_id=bakery.id
        )
        
        # Add to database
        db.session.add(new_baked_good)
        db.session.commit()
        
        # Return the created baked good
        return make_response(jsonify(new_baked_good.to_dict()), 201)
    
    except ValueError:
        return make_response(jsonify({"error": "Invalid price"}), 400)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    # Find the baked good
    baked_good = BakedGood.query.filter_by(id=id).first()
    
    # Check if baked good exists
    if not baked_good:
        return make_response(jsonify({"error": "Baked good not found"}), 404)
    
    # Delete the baked good
    db.session.delete(baked_good)
    db.session.commit()
    
    # Return a success message
    return make_response(jsonify({"message": "Baked good successfully deleted"}), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)