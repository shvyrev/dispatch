from datetime import datetime
from typing import List, Optional

from pydantic import validator
from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import backref, relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.incident_priority.models import IncidentPriorityCreate, IncidentPriorityRead
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead
from dispatch.messaging import INCIDENT_DOCUMENT_DESCRIPTIONS
from dispatch.models import DispatchBase, ResourceMixin, TermNested, TermReadNested, TimeStampMixin

# Association tables for many to many relationships
assoc_document_incident_priorities = Table(
    "document_incident_priority",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
    PrimaryKeyConstraint("incident_priority_id", "document_id"),
)

assoc_document_incident_types = Table(
    "document_incident_type",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
    PrimaryKeyConstraint("incident_type_id", "document_id"),
)

assoc_document_incidents = Table(
    "document_incident",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
    PrimaryKeyConstraint("incident_id", "document_id"),
)

assoc_document_terms = Table(
    "document_terms",
    Base.metadata,
    Column("term_id", Integer, ForeignKey("term.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
    PrimaryKeyConstraint("term_id", "document_id"),
)


class Document(Base, ResourceMixin, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    incident_priorities = relationship(
        "IncidentPriority", secondary=assoc_document_incident_priorities, backref="documents"
    )
    incident_types = relationship(
        "IncidentType", secondary=assoc_document_incident_types, backref="documents"
    )
    terms = relationship(
        "Term", secondary=assoc_document_terms, backref=backref("documents", cascade="all")
    )
    search_vector = Column(TSVectorType("name"))


# Pydantic models...
class DocumentBase(DispatchBase):
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    weblink: str
    name: str


class DocumentCreate(DocumentBase):
    terms: Optional[List[TermNested]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []


class DocumentUpdate(DocumentBase):
    terms: Optional[List[TermNested]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []


class DocumentRead(DocumentBase):
    id: int
    incident_priorities: Optional[List[IncidentPriorityRead]] = []
    incident_types: Optional[List[IncidentTypeRead]] = []
    terms: Optional[List[TermReadNested]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        return INCIDENT_DOCUMENT_DESCRIPTIONS.get(values["resource_type"], "No Description")


class DocumentNested(DocumentBase):
    id: int


class DocumentPagination(DispatchBase):
    total: int
    items: List[DocumentRead] = []
