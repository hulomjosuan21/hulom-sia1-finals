from src.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from src.utils import CreatedAt, UpdatedAt
from argon2 import PasswordHasher
import uuid
from sqlalchemy import Enum as SqlEnum
from enum import Enum
from datetime import datetime, date

ph = PasswordHasher()

class RoleEnum(Enum):
    ADMIN = "Admin"
    STUDENT = "Student"

class GenderEnum(Enum):
    MALE = "Male"
    FEMALE = "Female"

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    account_id = db.Column(
        UUID(as_uuid=True),
        default=uuid.uuid4
    )

    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    gender = db.Column(
        SqlEnum(
            GenderEnum,
            values_callable=lambda x: [e.value for e in x],
            name="genderenum"
        ),
        default=GenderEnum.MALE.value
    )
    birth_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String, nullable=False)

    course = db.Column(db.String(50), nullable=False)

    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String, unique=True, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    phone_number = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String)
    role = db.Column(
        SqlEnum(
            RoleEnum,
            values_callable=lambda x: [e.value for e in x],
            name="roleenum"
        ),
        default=RoleEnum.STUDENT.value
    )
    profile_url = db.Column(db.String)

    is_active = db.Column(db.Boolean, default=False)
    created_at = CreatedAt()
    updated_at = UpdatedAt()

    def set_password(self, password: str):
        self.password_hash = ph.hash(password)

    def set_profile_url(self, profile_url: str):
        self.profile_url = profile_url

    def verify_password(self, password: str) -> bool:
        try:
            return ph.verify(self.password_hash, password)
        except Exception:
            return False
    def to_dict(self):
        return {
            "user_id": str(self.user_id),
            "account_id": str(self.account_id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": str(self.gender.value),
            "birth_date": self.birth_date.isoformat() if isinstance(self.birth_date, (date, datetime)) else self.birth_date,
            "address": self.address,
            "course": self.course,
            "is_verified": self.is_verified,
            "phone_number": self.phone_number,
            "email": self.email,
            "role": str(self.role.value),
            "profile_url": self.profile_url,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
            
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    enrollment_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )

    enrolled_at = CreatedAt()
    updated_at = UpdatedAt()