from flask import jsonify, request
from sqlalchemy import select
from app.models import Customers, db
from .schemas import customer_schema, customers_schema, login_schema
from marshmallow import ValidationError
from app.utils.util import encode_token, token_required
from . import customers_bp


@customers_bp.route('/login', methods=['POST'])
def login():
    try:
        data = login_schema.load(request.get_json())
    except Exception as err:
        return jsonify(err.messages), 400

    customer = db.session.execute(
        select(Customers).filter_by(email=data['email'])
    ).scalars().first()

    if not customer or not customer.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token}), 200


@customers_bp.route('')
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    stmt = select(Customers).order_by(Customers.name)
    pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    return jsonify({
        "customers": customers_schema.dump(pagination.items),
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    }), 200


@customers_bp.route('/<int:id>')
@token_required
def get_customer(customer_id, id):
    if int(customer_id) != id:
        return jsonify({"error": "Unauthorized"}), 403
    customer = db.session.get(Customers, id)
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


@customers_bp.route('', methods=['POST'])
def add_customer():
    data = request.get_json()
    try:
        customer_data = customer_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    # Check if email already exists
    query = select(Customers).where(Customers.email == customer_data['email'])
    existing_member = db.session.execute(query).scalars().first()
    if existing_member:
        return jsonify({"error": "Email already associated with an account."}), 400

    # Hash password before saving
    raw_password = customer_data.pop('password', None)
    customer = Customers(**customer_data)
    if raw_password:
        customer.set_password(raw_password)

    db.session.add(customer)
    db.session.commit()
    return customer_schema.jsonify(customer), 201

@customers_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_customer(customer_id, id):
    if int(customer_id) != id:
        return jsonify({"error": f'Unauthorized {id}'}), 403
    customer = db.session.get(Customers, id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    try:
        customer_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    raw_password = customer_data.pop('password', None)
    for key, value in customer_data.items():
        setattr(customer, key, value)
    if raw_password:
        customer.set_password(raw_password)
    db.session.commit()
    return customer_schema.jsonify(customer), 200


@customers_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id, id):
    if int(customer_id) != id:
        return jsonify({"error": "Unauthorized"}), 403
    customer = db.session.get(Customers, id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully."}), 200
