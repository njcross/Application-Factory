from flask import jsonify, request
from sqlalchemy import select
from .schemas import mechanic_schema, mechanics_schema
from marshmallow import ValidationError
from . import mechanics_bp
from app.extensions import cache
from sqlalchemy import func
from flask import request
from app.models import Mechanics, db, service_mechanics

@mechanics_bp.route('/most-active', methods=['GET'])
def most_active_mechanics():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    stmt = (
        db.session.query(Mechanics, func.count(service_mechanics.c.ticket_id).label('ticket_count'))
        .join(service_mechanics)
        .group_by(Mechanics.id)
        .order_by(func.count(service_mechanics.c.ticket_id).desc())
    )

    pagination = stmt.paginate(page=page, per_page=per_page, error_out=False)

    results = [
        {
            "id": mech.id,
            "name": mech.name,
            "email": mech.email,
            "ticket_count": count
        }
        for mech, count in pagination.items
    ]

    return jsonify({
        "mechanics": results,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    }), 200

@mechanics_bp.route('')
@cache.cached(timeout=60)
def get_mechanics():   
    """
    Cached for 60 seconds to reduce DB load for frequent access.
    """ 
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