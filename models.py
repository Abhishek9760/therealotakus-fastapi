from sqlalchemy import Boolean, Column, String, Integer, DECIMAL

from database import Base


class App(Base):
    __tablename__ = "app"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)
    show_message = Column(Boolean, index=True)
    version = Column(String, index=True)
    # hashed_password = Column(String)
    # is_active = Column(Boolean, default=True)

    # items = relationship("Item", back_populates="owner")