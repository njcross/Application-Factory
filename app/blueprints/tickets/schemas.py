from app.extensions import ma
from app.models import Tickets  # Import the Tickets model

class TicketsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tickets
        include_fk = True 
ticket_schema = TicketsSchema()
tickets_schema = TicketsSchema(many=True)