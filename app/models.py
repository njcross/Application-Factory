from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


# Create a base class for our models
class Base(DeclarativeBase):
    pass
 
#Instantiate your SQLAlchemy database

db = SQLAlchemy(model_class = Base)




#========== Models ==========
service_mechanics = db.Table(
    'service_mechanics',
    Base.metadata,
    db.Column('mechanic_id', db.ForeignKey('mechanics.id')),
    db.Column('ticket_id', db.ForeignKey('service_tickets.id'))
)

class Customers(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)

    tickets: Mapped[List['Tickets']] = db.relationship(back_populates='customer')
    def set_password(self, password: str):
        """Hashes the plaintext password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks a plaintext password against the hashed version."""
        return check_password_hash(self.password_hash, password)

class Tickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))

    parts = relationship('Inventory', secondary='ticket_inventory', back_populates='tickets')
    customer: Mapped['Customers'] = db.relationship(back_populates='tickets')
    mechanics: Mapped[List['Mechanics']] = db.relationship(secondary=service_mechanics, back_populates='tickets')

class Mechanics(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    tickets: Mapped[List['Tickets']] = db.relationship(secondary=service_mechanics, back_populates='mechanics')

class TicketInventory(db.Model):
    __tablename__ = 'ticket_inventory'
    ticket_id = db.Column(db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    tickets = relationship('Tickets', secondary='ticket_inventory', back_populates='parts')
#========== End of Models ==========