from flask import jsonify, request
from sqlalchemy import select
from app.models import Customers, db
from .schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from . import customers_bp

@customers_bp.route('')
def get_customers():
    query = select(Customers)
    members = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(members)

@customers_bp.route('/<int:id>')
def get_customer(id):
    customer = db.session.get(Customers, id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404

@customers_bp.route('', methods=['POST'])
def add_customer():
    from flask import request
    data = request.get_json()
    try:
        customer_data = customer_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400
    
    query = select(Customers).where(Customers.email == customer_data['email']) #Checking our db for a member with this email
    existing_member = db.session.execute(query).scalars().all()
    if existing_member:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    customer = Customers(**customer_data)
    db.session.add(customer)
    db.session.commit()
    return customer_schema.jsonify(customer), 201

@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customers, id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customers_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):    
    customer = db.session.get(Customers, id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully."}), 200