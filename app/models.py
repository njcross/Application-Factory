from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List


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

    tickets: Mapped[List['Tickets']] = db.relationship(back_populates='customer')

class Tickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))

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

#========== End of Models ==========