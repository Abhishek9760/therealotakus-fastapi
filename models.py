from sqlalchemy import Boolean, Column, String, Integer, DECIMAL

from database import Base


class App(Base):
    __tablename__ = "app"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)
    show_message = Column(Boolean, index=True)
    version = Column(String, index=True)

class AppInstall(Base):
    __tablename__ = "app_install"

    id = Column(Integer, primary_key=True, index=True)
    total_install = Column(Integer, index=True)

