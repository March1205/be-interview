from sqlmodel import SQLModel, Field, Relationship


class Base(SQLModel):
    pass


class CreateOrganisation(Base):
    name: str


class Organisation(Base, table=True):
    id: int | None = Field(primary_key=True)
    name: str


class Location(Base, table=True):
    id: int | None = Field(primary_key=True)
    organisation_id: int = Field(foreign_key="organisation.id")
    organisation: Organisation = Relationship()
    location_name: str
    longitude: float
    latitude: float
