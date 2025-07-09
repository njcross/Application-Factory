from flask import jsonify, request
from sqlalchemy import select
from app.models import Tickets, db, Customers
from .schemas import ticket_schema, tickets_schema
from app.models import Inventory, TicketInventory
from marshmallow import ValidationError
from . import tickets_bp
from app.extensions import limiter
from app.utils.util import token_required

@tickets_bp.route('')
@limiter.limit("10 per minute")
def get_tickets():
    """
    Public: Rate limited to 10 requests per minute per IP.
    """
    query = select(Tickets)
    tickets = db.session.execute(query).scalars().all() 
    return tickets_schema.jsonify(tickets)

@tickets_bp.route('/<int:id>')
@token_required
def get_ticket(customer_id, id):
    ticket = db.session.get(Tickets, id)
    if not ticket or ticket.customer_id != int(customer_id):
        return jsonify({"error": "Unauthorized access or ticket not found."}), 403
    return ticket_schema.jsonify(ticket), 200

@tickets_bp.route('', methods=['POST'])
@token_required
def add_ticket(customer_id):
    data = request.get_json()
    try:
        ticket_data = ticket_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    # Ensure ticket is created only for the authenticated customer
    if ticket_data.get("customer_id") != int(customer_id):
        return jsonify({"error": "Cannot create ticket for another customer."}), 403

    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({"error": "Authenticated customer not found."}), 400

    ticket = Tickets(**ticket_data)
    db.session.add(ticket)
    db.session.commit()
    return ticket_schema.jsonify(ticket), 201

@tickets_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_ticket(customer_id, id):
    ticket = db.session.get(Tickets, id)
    if not ticket or ticket.customer_id != int(customer_id):
        return jsonify({"error": "Unauthorized or ticket not found."}), 403

    try:
        ticket_data = ticket_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Optional customer_id change check
    if "customer_id" in ticket_data and ticket_data["customer_id"] != int(customer_id):
        return jsonify({"error": "Cannot assign ticket to a different customer."}), 403

    for key, value in ticket_data.items():
        setattr(ticket, key, value)

    db.session.commit()
    return ticket_schema.jsonify(ticket), 200

@tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@token_required
def assign_mechanic(customer_id, ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    if not ticket or ticket.customer_id != int(customer_id):
        return jsonify({"error": "Unauthorized or ticket not found."}), 403

    from app.models import Mechanics
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned."}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic successfully assigned."}), 200

@tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@token_required
def remove_mechanic(customer_id, ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    if not ticket or ticket.customer_id != int(customer_id):
        return jsonify({"error": "Unauthorized or ticket not found."}), 403

    from app.models import Mechanics
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic is not assigned."}), 200

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic successfully removed."}), 200

@tickets_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_ticket(customer_id, id):
    ticket = db.session.get(Tickets, id)
    if not ticket or ticket.customer_id != int(customer_id):
        return jsonify({"error": "Unauthorized or ticket not found."}), 403

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": "Ticket deleted successfully."}), 200

@tickets_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    """
    Returns all service tickets associated with the authenticated customer.
    Requires Bearer token.
    """
    query = select(Tickets).where(Tickets.customer_id == int(customer_id))
    tickets = db.session.execute(query).scalars().all()
    
    return tickets_schema.jsonify(tickets), 200

@tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@token_required
def edit_ticket_mechanics(customer_id, ticket_id):
    data = request.get_json()
    add_ids = data.get('add_ids', [])
    remove_ids = data.get('remove_ids', [])

    ticket = db.session.get(Tickets, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    # ✅ Ensure this ticket belongs to the authenticated customer
    if ticket.customer_id != int(customer_id):
        return jsonify({"error": "You do not have permission to modify this ticket."}), 403

    from app.models import Mechanics

    # Add mechanics
    for mechanic_id in add_ids:
        mechanic = db.session.get(Mechanics, mechanic_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    # Remove mechanics
    for mechanic_id in remove_ids:
        mechanic = db.session.get(Mechanics, mechanic_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return jsonify({"message": "Mechanic assignments updated."}), 200

@tickets_bp.route('/<int:ticket_id>/add-part/<int:inventory_id>', methods=['PUT'])
@token_required
def add_part_to_ticket(customer_id, ticket_id, inventory_id):
    ticket = db.session.get(Tickets, ticket_id)
    if not ticket or ticket.customer_id != int(customer_id):
        return jsonify({"error": "Ticket not found or access denied."}), 404

    part = db.session.get(Inventory, inventory_id)
    if not part:
        return jsonify({"error": "Part not found."}), 404

    # check if already exists in junction
    existing = db.session.query(TicketInventory).filter_by(ticket_id=ticket_id, inventory_id=inventory_id).first()
    if existing:
        existing.quantity += 1
    else:
        new_link = TicketInventory(ticket_id=ticket_id, inventory_id=inventory_id, quantity=1)
        db.session.add(new_link)

    db.session.commit()
    return jsonify({"message": "Part added to ticket."}), 200