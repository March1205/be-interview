from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select, Session
from typing import Optional, Tuple, List
from pydantic import BaseModel

from app.db import get_db
from app.models import Location, Organisation, CreateOrganisation

router = APIRouter()


class CreateLocation(BaseModel):
    name: str
    latitude: float
    longitude: float
    organisation_id: int


@router.post("/create", response_model=Organisation)
def create_organisation(
    create_organisation: CreateOrganisation, session: Session = Depends(get_db)
) -> Organisation:
    """Create an organisation."""
    organisation = Organisation(name=create_organisation.name)
    session.add(organisation)
    session.commit()
    session.refresh(organisation)
    return organisation


@router.get("/", response_model=list[Organisation])
def get_organisations(session: Session = Depends(get_db)) -> list[Organisation]:
    """
    Get all organisations.
    """
    organisations = session.exec(select(Organisation)).all()
    return organisations


@router.get("/{organisation_id}", response_model=Organisation)
def get_organisation(
    organisation_id: int, session: Session = Depends(get_db)
) -> Organisation:
    """
    Get an organisation by id.
    """
    organisation = session.get(Organisation, organisation_id)
    if organisation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found"
        )
    return organisation


@router.post("/create/locations", response_model=Location)
def create_location(
    create_location: CreateLocation, session: Session = Depends(get_db)
) -> Location:
    """
    Create a location for an organisation.
    """
    organisation = session.get(Organisation, create_location.organisation_id)
    if organisation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found"
        )

    location = Location(
        name=create_location.name,
        latitude=create_location.latitude,
        longitude=create_location.longitude,
        organisation_id=create_location.organisation_id,
    )
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@router.get("/{organisation_id}/locations", response_model=List[Location])
def get_organisation_locations(
    organisation_id: int,
    bounding_box: Optional[Tuple[float, float, float, float]] = None,
    session: Session = Depends(get_db),
) -> List[Location]:
    """
    Get all locations for a specific organisation, optionally filtered by a bounding box.
    """
    query = select(Location).where(Location.organisation_id == organisation_id)

    if bounding_box:
        min_lat, min_lon, max_lat, max_lon = bounding_box
        query = query.where(
            Location.latitude >= min_lat,
            Location.latitude <= max_lat,
            Location.longitude >= min_lon,
            Location.longitude <= max_lon,
        )

    locations = session.exec(query).all()
    if not locations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No locations found for this organisation within the specified bounding box.",
        )

    return locations
