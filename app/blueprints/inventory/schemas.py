# inventory/schemas.py
from app.extensions import ma
from app.models import Inventory, Tickets
from marshmallow_sqlalchemy import fields

class TicketBriefSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tickets
        include_fk = True
        fields = ('id', 'VIN', 'service_date', 'service_desc')

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_relationships = True
        load_instance = True

    tickets = fields.Nested(TicketBriefSchema, many=True)

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)