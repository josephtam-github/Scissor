from api.v1 import db
from datetime import datetime


class ViewCount(db.Model):
    __tablename__ = "viewcount"
    link_id = db.Column(db.Integer(), db.ForeignKey("link.link_id"), primary_key=True, nullable=False)
    short_link = db.Column(db.String(45), nullable=False, unique=True)
    view_count = db.Column(db.Integer(), nullable=False, default=0)

    def __repr__(self):
        return f"<User {self.user_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def refresh(self):
        db.session.refresh(self)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get_or_404(user_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
