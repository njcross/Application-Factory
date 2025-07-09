# tickets/schemas.py
from app.extensions import ma
from app.models import Tickets, Inventory, Mechanics, Customers
from marshmallow_sqlalchemy import fields

class InventoryBriefSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        fields = ("id", "name", "price")

class MechanicBriefSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics
        fields = ("id", "name", "email", "phone")

class CustomerBriefSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers
        fields = ("id", "name", "email", "phone")

class TicketsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tickets
        include_relationships = True
        load_instance = True

    parts = fields.Nested(InventoryBriefSchema, many=True)
    mechanics = fields.Nested(MechanicBriefSchema, many=True)
    customer = fields.Nested(CustomerBriefSchema)

ticket_schema = TicketsSchema()
tickets_schema = TicketsSchema(many=True)