from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Text, Boolean, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

def uuid_pk():
    return uuid.uuid4()

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pk)
    name: Mapped[str]            = mapped_column(Text, nullable=False)
    email: Mapped[str]           = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str]   = mapped_column(Text, nullable=False)
    is_admin: Mapped[bool]       = mapped_column(Boolean, default=False, nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pk)
    name: Mapped[str]            = mapped_column(Text, unique=True, nullable=False)

class Item(Base):
    __tablename__ = "items"
    id: Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pk)
    seller_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str]           = mapped_column(Text, nullable=False)
    description: Mapped[str]     = mapped_column(Text, nullable=False)
    price: Mapped[float]         = mapped_column(Numeric(10,2), nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"))
    status: Mapped[str]          = mapped_column(Text, nullable=False, default="active")
    listing_type: Mapped[str]    = mapped_column(Text, nullable=False, default="auction")
    buy_now_price: Mapped[float | None] = mapped_column(Numeric(10,2))
    pickup_location: Mapped[str | None] = mapped_column(Text)
    pickup_campus: Mapped[str | None] = mapped_column(Text)
    pickup_lat: Mapped[float | None] = mapped_column()
    pickup_lng: Mapped[float | None] = mapped_column()

class ItemImage(Base):
    __tablename__ = "item_images"
    id: Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pk)
    item_id: Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    image_path: Mapped[str]      = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool]     = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int]      = mapped_column(Integer, default=0, nullable=False)


class Bid(Base):
    __tablename__ = "bids"
    id: Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid_pk)
    item_id: Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    bidder_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount: Mapped[float]        = mapped_column(Numeric(10,2), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")  # pending / accepted / not_accepted

    # placed_at set by DB default
