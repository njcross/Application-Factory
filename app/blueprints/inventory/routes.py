from flask import request, jsonify
from app.models import db, Inventory
from . import inventory_bp
from .schemas import inventory_schema, inventories_schema
from marshmallow import ValidationError
from sqlalchemy import select

@inventory_bp.route('', methods=['GET'])
def get_inventory():
    stmt = select(Inventory)
    items = db.session.execute(stmt).scalars().all()
    return inventories_schema.jsonify(items)

@inventory_bp.route('/<int:id>', methods=['GET'])
def get_item(id):
    item = db.session.get(Inventory, id)
    if item:
        return inventory_schema.jsonify(item)
    return jsonify({"error": "Item not found."}), 404

@inventory_bp.route('', methods=['POST'])
def add_item():
    try:
        data = inventory_schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400
    item = Inventory(**data)
    db.session.add(item)
    db.session.commit()
    return inventory_schema.jsonify(item), 201

@inventory_bp.route('/<int:id>', methods=['PUT'])
def update_item(id):
    item = db.session.get(Inventory, id)
    if not item:
        return jsonify({"error": "Item not found."}), 404
    try:
        data = inventory_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return {"errors": err.messages}, 400
    for key, value in data.items():
        setattr(item, key, value)
    db.session.commit()
    return inventory_schema.jsonify(item), 200

@inventory_bp.route('/<int:id>', methods=['DELETE'])
def delete_item(id):
    item = db.session.get(Inventory, id)
    if not item:
        return jsonify({"error": "Item not found."}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted."}), 200