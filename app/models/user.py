from app import db
from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index

class User(db.Model):
    """User model with performance optimizations."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_premium = db.Column(db.Boolean, default=False, index=True)
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_verified = db.Column(db.Boolean, default=False, index=True)
    last_login = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    deleted_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    items = db.relationship('Item', backref='owner', lazy='dynamic')

    # Indexes for common queries
    __table_args__ = (
        Index('idx_users_email_username', 'email', 'username'),
        Index('idx_users_status', 'is_active', 'is_deleted', 'is_premium'),
    )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])

    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the password matches."""
        return check_password_hash(self.password_hash, password)

    def soft_delete(self):
        """Soft delete the user."""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = datetime.now(UTC)

    def restore(self):
        """Restore a soft-deleted user."""
        self.is_deleted = False
        self.is_active = True
        self.deleted_at = None

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now(UTC)

    def __repr__(self):
        return f'<User {self.username}>' 