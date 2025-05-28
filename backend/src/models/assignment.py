from src.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from src.utils import CreatedAt, UpdatedAt
import uuid
from enum import Enum

class Assignment(db.Model):
    __tablename__ =  'assignments'

    assignment_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    created_by = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )

    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)

    due_date = db.Column(db.DateTime, nullable=False)

    created_at = CreatedAt()
    updated_at = UpdatedAt()

    creator = db.relationship('User', backref=db.backref('assignments', passive_deletes=True))
    
    assignees = db.relationship(
        'AssignmentAssignee',
        backref='assignment',
        cascade='all, delete-orphan',
        lazy='joined'
    )
    
    def to_dict(self):
        return {
            "assignment_id": str(self.assignment_id),
            "created_by": str(self.created_by),
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "assignees": [
                {
                    "user_id": str(assignee.assignee.user_id),
                    "first_name": assignee.assignee.first_name,
                    "last_name": assignee.assignee.last_name,
                    "email": assignee.assignee.email,
                    "status": assignee.status.name,
                    "submitted_at": assignee.submitted_at.isoformat() if assignee.submitted_at else None,
                    "attachment_url": assignee.attachment_url
                }
                for assignee in self.assignees
            ]
        }

class AssignmentAssigneeStatusEnum(Enum):
    COMPLETE = "Complete"
    PENDING = "Pending"
    SUBMITTED = "Submitted"
    LATE = "Late"

class AssignmentAssignee(db.Model):
    __tablename__ =  'assignment_assignee'

    assignment_assignee_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    assignment_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('assignments.assignment_id', ondelete='CASCADE'),
        nullable=False
    )

    assigned_by_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )

    assigned_to_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )

    attachment_url = db.Column(db.String, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.Enum(AssignmentAssigneeStatusEnum), default=AssignmentAssigneeStatusEnum.PENDING)
    
    assignee = db.relationship('User', foreign_keys=[assigned_to_id])

    assigned_at = CreatedAt()
    updated_at = UpdatedAt()