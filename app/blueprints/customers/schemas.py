from app.extensions import ma
from app.models import Customers  # Import the Customers model

class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers

customer_schema = CustomersSchema()
customers_schema = CustomersSchema(many=True)