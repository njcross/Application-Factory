from app.extensions import ma
from app.models import Customers
from marshmallow import fields

class CustomersSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(required=True, load_only=True)  # required, write-only

    class Meta:
        model = Customers
        exclude = ("password_hash",)  # still exclude this from output

customer_schema = CustomersSchema()
customers_schema = CustomersSchema(many=True)

class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

login_schema = LoginSchema()