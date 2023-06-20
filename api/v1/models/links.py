from api.v1 import db
from datetime import datetime


class Link(db.Model):
    __tablename__ = "link"
    link_id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.user_id'))
    true_link = db.Column(db.String(50), nullable=False, unique=True)
    custom_link = db.Column(db.String(45), nullable=False, unique=True)
    short_link = db.Column(db.String(45), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"<User {self.user_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def refresh(self):
        db.session.refresh()
    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get_or_404(user_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
