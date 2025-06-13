# modules/auth/models.py
from utils.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ----------------------- 用户表 -----------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # 存储密码字段
    name = db.Column(db.String(100), nullable=False)  # 姓名字段
    age = db.Column(db.Integer, nullable=False)  # 年龄字段
    gender = db.Column(db.String(10), nullable=False)  # 性别字段
    enable = db.Column(db.Boolean, default=True, nullable=False)  # 是否可用，1可用；0冻结
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    # 与角色的多对多关系
    user_role_relations = db.relationship('UserRoleRelation',
                                          backref='user', lazy='dynamic',
                                          cascade='all, delete-orphan')

    # 与组的多对多关系
    user_group_relations = db.relationship('UserGroupRelation',
                                           backref='user', lazy='dynamic',
                                           cascade='all, delete-orphan')

    # 依赖其他模块里的模型名（字符串声明即可，SQLAlchemy 会延迟解析）
    access_success_records = db.relationship('AccessSuccessTracker',
                                             backref='user', lazy='dynamic',
                                             cascade='all, delete-orphan')
    operation_behavior_records = db.relationship('OperationBehaviorTracker',
                                                 backref='user', lazy='dynamic',
                                                 cascade='all, delete-orphan')
    data_sensitivity_records = db.relationship('DataSensitivityTracker',
                                               backref='user', lazy='dynamic',
                                               cascade='all, delete-orphan')
    access_time_records = db.relationship('AccessTimeTracker',
                                          backref='user', lazy='dynamic',
                                          cascade='all, delete-orphan')
    access_location_records = db.relationship('AccessLocationTracker',
                                              backref='user', lazy='dynamic',
                                              cascade='all, delete-orphan')

    # ---------------- 密码辅助方法 ----------------
    def set_password(self, password):
        """设置密码哈希"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'enable': self.enable,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ----------------------- 角色表 -----------------------
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_code = db.Column(db.String(50), unique=True, nullable=False)  # 角色code
    role_name = db.Column(db.String(100), nullable=False)  # 角色名称
    description = db.Column(db.String(200), nullable=True)  # 角色描述
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    # 与用户的多对多关系
    role_user_relations = db.relationship('UserRoleRelation',
                                          backref='role', lazy='dynamic',
                                          cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'role_code': self.role_code,
            'role_name': self.role_name,
            'description': self.description,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ----------------------- 用户-角色关系表 -----------------------
class UserRoleRelation(db.Model):
    __tablename__ = 'user_role_relation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ----------------------- 组表 -----------------------
class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(100), nullable=False)  # 组名称（医院名称）
    enable = db.Column(db.Boolean, default=True, nullable=False)  # 是否可用，默认为1；1可用，0冻结
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    # 与用户的多对多关系
    group_user_relations = db.relationship('UserGroupRelation',
                                           backref='group', lazy='dynamic',
                                           cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'group_name': self.group_name,
            'enable': self.enable,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ----------------------- 用户-组关系表 -----------------------
class UserGroupRelation(db.Model):
    __tablename__ = 'user_group_relation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    type = db.Column(db.String(10), default='base', nullable=False)  # 关系类型：base/temp；基础/临时
    enable = db.Column(db.Boolean, default=True, nullable=False)  # 是否可用，默认为1；1可用，0冻结
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'group_id': self.group_id,
            'type': self.type,
            'enable': self.enable,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }