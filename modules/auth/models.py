# modules/auth/models.py
from utils.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------------- 用户表 -----------------------
class User(db.Model):
    __tablename__ = 'users'

    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(80),  unique=True, nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow,
                            onupdate=datetime.utcnow)

    # 依赖其他模块里的模型名（字符串声明即可，SQLAlchemy 会延迟解析）
    access_success_records   = db.relationship('AccessSuccessTracker',
                               backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    operation_behavior_records = db.relationship('OperationBehaviorTracker',
                               backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    data_sensitivity_records = db.relationship('DataSensitivityTracker',
                               backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    access_time_records      = db.relationship('AccessTimeTracker',
                               backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')
    access_location_records  = db.relationship('AccessLocationTracker',
                               backref='user', lazy='dynamic',
                               cascade='all, delete-orphan')

    # 与 Role 的多对多
    user_roles_association = db.relationship('UserRole',
                              back_populates='user_obj',
                              lazy='dynamic', cascade='all, delete-orphan')

    # ---------------- 密码辅助方法 ----------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ----------------------- 角色表 -----------------------
class Role(db.Model):
    __tablename__ = 'roles'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Integer, default=0)          # 位掩码
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    role_users_association = db.relationship('UserRole',
                             back_populates='role_obj',
                             lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions
        }

# ----------------------- 用户-角色关联表 -----------------------
class UserRole(db.Model):
    __tablename__ = 'user_roles'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer,
                           db.ForeignKey('users.id'), nullable=False)
    role_id    = db.Column(db.Integer,
                           db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_obj   = db.relationship('User', back_populates='user_roles_association')
    role_obj   = db.relationship('Role', back_populates='role_users_association')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
