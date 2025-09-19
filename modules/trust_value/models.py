from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class UserVisit(db.Model):
    """用户访问记录模型，用于跟踪用户的访问次数"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False, comment="用户唯一标识")
    visit_count = db.Column(db.Integer, default=0, nullable=False, comment="访问次数")
    last_visit = db.Column(db.DateTime, default=datetime.utcnow, comment="最后访问时间")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="记录创建时间")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="记录更新时间")

    def __repr__(self):
        return f'<UserVisit {self.user_id}: {self.visit_count} visits>'

    def increment_visit(self):
        """增加访问次数并更新最后访问时间"""
        self.visit_count += 1
        self.last_visit = datetime.utcnow()
        return self
