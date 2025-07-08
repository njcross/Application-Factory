from flask import jsonify, request
from sqlalchemy import select
from app.models import Mechanics, db
from .schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError
from . import mechanics_bp

@mechanics_bp.route('')
def get_mechanics():    
    query = select(Mechanics)
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics)

@mechanics_bp.route('/<int:id>')
def get_mechanic(id):   
    mechanic = db.session.get(Mechanics, id)
    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404

@mechanics_bp.route('', methods=['POST'])
def add_mechanic():
    from flask import request
    data = request.get_json()
    try:
        mechanic_data = mechanic_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400
    
    query = select(Mechanics).where(Mechanics.email == mechanic_data['email']) #Checking our db for a member with this email
    existing_mechanic = db.session.execute(query).scalars().all()   
    if existing_mechanic:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    mechanic = Mechanics(**mechanic_data)
    db.session.add(mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 201

@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = db.session.get(Mechanics, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanics, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic deleted successfully."}), 200