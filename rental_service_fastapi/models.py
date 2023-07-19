from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.types import DECIMAL
import datetime

from .database import Base
from .enum import RequestApprovedState, Grade

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    role = Column(String(255), default="user")
    location_id = Column(Integer, ForeignKey("locations.id"))
    location_details = Column(String(1000))
    hashed_password = Column(String(255))
    registration_time = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    location = relationship("Location", back_populates="users")
    items = relationship("Item", passive_deletes=True, back_populates="owner")
    rents = relationship("Rent", passive_deletes=True, back_populates="renter")
    rent_requests = relationship("RentRequest", passive_deletes=True, back_populates="renter")
    reviews = relationship("ItemReview", passive_deletes=True, back_populates="reviewer")

class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    unit_name = Column(String(64), unique=True, index=True)
    unit_to_seconds = Column(Integer)

class ItemType(Base):
    __tablename__ = "item_types"

    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(64), unique=True, index=True)

    items = relationship("Item", back_populates="item_type")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(255))
    item_type_id = Column(Integer, ForeignKey("item_types.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    item_location = Column(String(255))
    description = Column(String(255))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    price_per_unit = Column(DECIMAL(precision=8, scale=2))
    unit_id = Column(Integer, ForeignKey("units.id"))
    available = Column(Boolean)

    # available should turn to False if rent is still in process

    item_type = relationship("ItemType", back_populates="items")
    location = relationship("Location", back_populates="items")
    owner = relationship("User", back_populates="items")
    unit = relationship("Unit")
    rent = relationship("Rent", passive_deletes=True, back_populates="item")
    rent_requests = relationship("RentRequest", passive_deletes=True, back_populates="item")
    reviews = relationship("ItemReview", passive_deletes=True, back_populates="item")



class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    postal_code = Column(String(16), index=True)
    name = Column(String(255))
    description = Column(String(1000))
    country_id = Column(Integer, ForeignKey("countries.id"))

    country = relationship("Country", back_populates="cities")
    users = relationship("User", back_populates="location")
    items = relationship("Item", back_populates="location")

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, index=True)

    cities = relationship("Location", back_populates="country")

class Rent(Base): # должна создаваться только после того как реквест на аренду был заапрувен
    __tablename__ = "rent"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete='CASCADE'))
    renter_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE')) # who rented the item
    time_from = Column(TIMESTAMP)
    time_to = Column(TIMESTAMP)
    unit_id = Column(Integer, ForeignKey("units.id"))
    price_per_unit = Column(DECIMAL(precision=8, scale=2))
    price_total = Column(DECIMAL(precision=8, scale=2))

    item = relationship("Item", back_populates="rent")
    renter = relationship("User", back_populates="rents")
    unit = relationship("Unit")

class RentRequest(Base):
    __tablename__ = "rent_request"

    id = Column(Integer, primary_key=True, index=True)
    approved = Column(Enum(RequestApprovedState), default=RequestApprovedState.not_yet)
    item_id = Column(Integer, ForeignKey("items.id", ondelete='CASCADE'))
    renter_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    time_from = Column(TIMESTAMP)
    time_to = Column(TIMESTAMP)

    item = relationship("Item", back_populates="rent_requests")
    renter = relationship("User", back_populates="rent_requests")

class ItemReview(Base):
    __tablename__ = "item_review"

    id = Column(Integer, primary_key=True, index=True)
    rented_item_id = Column(Integer, ForeignKey("items.id",ondelete='CASCADE'))
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    grade = Column(Enum(Grade))
    description = Column(String(1000))
    date = Column(TIMESTAMP)

    item = relationship("Item", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")




