from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Events(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[str]
    type_name: Mapped[str]
    timestamp: Mapped[float]
    intent_name: Mapped[str]
    action_name: Mapped[str]
    data: Mapped[str]
