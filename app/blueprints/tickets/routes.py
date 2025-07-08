from flask import jsonify, request
from sqlalchemy import select
from app.models import Tickets, db, Customers
from .schemas import ticket_schema, tickets_schema
from marshmallow import ValidationError
from . import tickets_bp

@tickets_bp.route('')
def get_tickets():
    query = select(Tickets)
    tickets = db.session.execute(query).scalars().all() 
    return tickets_schema.jsonify(tickets)

@tickets_bp.route('/<int:id>')
def get_ticket(id):
    ticket = db.session.get(Tickets, id)
    if ticket:
        return ticket_schema.jsonify(ticket), 200
    return jsonify({"error": "Ticket not found."}), 404

@tickets_bp.route('', methods=['POST'])
def add_ticket():
    data = request.get_json()
    try:
        ticket_data = ticket_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    # Validate customer_id exists
    customer_id = ticket_data.get("customer_id")
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({"error": f"Customer with ID {customer_id} does not exist."}), 400

    ticket = Tickets(**ticket_data)
    db.session.add(ticket)
    db.session.commit()
    return ticket_schema.jsonify(ticket), 201

@tickets_bp.route('/<int:id>', methods=['PUT'])
def update_ticket(id):
    ticket = db.session.get(Tickets, id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    try:
        ticket_data = ticket_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # If customer_id is provided, validate it
    if "customer_id" in ticket_data:
        customer_id = ticket_data["customer_id"]
        customer = db.session.get(Customers, customer_id)
        if not customer:
            return jsonify({"error": f"Customer with ID {customer_id} does not exist."}), 400

    for key, value in ticket_data.items():
        setattr(ticket, key, value)

    db.session.commit()
    return ticket_schema.jsonify(ticket), 200

@tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    from app.models import Mechanics
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned to this ticket."}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic successfully assigned to ticket."}), 200

@tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    from app.models import Mechanics
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic is not assigned to this ticket."}), 200

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic successfully removed from ticket."}), 200

@tickets_bp.route('/<int:id>', methods=['DELETE'])
def delete_ticket(id):  
    ticket = db.session.get(Tickets, id)

    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404
    
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": "Ticket deleted successfully."}), 200