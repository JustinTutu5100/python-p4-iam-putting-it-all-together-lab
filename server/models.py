from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # === columns ===
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # === relationships ===
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    # === serializer config ===
    serialize_rules = ('-recipes.user', '-_password_hash',)

    # === password hash property ===
    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes are not viewable.')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # === authentication helper ===
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    # === validations ===
    @validates('username')
    def validate_username(self, key, value):
        if not value or value.strip() == '':
            raise ValueError('Username cannot be empty')
        return value


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    # === columns ===
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    # foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # === serializer config ===
    serialize_rules = ('-user.recipes',)

    @validates('title')
    def validate_title(self, key, value):
        if not value or value.strip() == '':
            raise ValueError('Title cannot be empty')
        return value

    @validates('instructions')
    def validate_instructions(self, key, value):
        if not value or len(value.strip()) < 50:
            raise ValueError('Instructions must be at least 50 characters long')
        return value
