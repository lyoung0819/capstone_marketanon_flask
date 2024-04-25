import secrets
from . import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


class UserBuyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    company = db.Column(db.String, nullable=False)
    token = db.Column(db.String, unique=True)
    token_exp = db.Column(db.DateTime(timezone=True))
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    reviews = db.relationship('Review', back_populates='author')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, plaintext_pass):
        self.password = generate_password_hash(plaintext_pass)
        self.save()

    def check_password(self, plaintext_pass):
        return check_password_hash(self.password, plaintext_pass)
    
    def to_dict(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            'username': self.username,
            "title": self.title,
            'company': self.company
        }
    
    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_exp > now + timedelta(minutes=1):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_exp = now + timedelta(hours=1)
        self.save()
        return {"token": self.token, "tokenExpiration": self.token_exp}
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Company {self.id}|{self.company_name}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            "id": self.id,
            "companyName": self.company_name,
            "address": self.address
        }



class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    dateCreated = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)) 
    user_id = db.Column(db.Integer, db.ForeignKey('user_buyer.id'), nullable=False) 
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    author = db.relationship('UserBuyer', back_populates='reviews')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()
    
    def __repr__(self):
        return f"<Review {self.id}|{self.title}|{self.author}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "rating": self.rating,
            "dateCreated": self.dateCreated,
            "author": self.author.to_dict()  
        }
    
    def update(self, **kwargs):
        allowed_fields = {'title', 'body', 'rating'}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()