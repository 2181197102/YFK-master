from utils.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    access_success_records = db.relationship(
        'AccessSuccessTracker',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    operation_behavior_records = db.relationship(
        'OperationBehaviorTracker',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    data_sensitivity_records = db.relationship(
        'DataSensitivityTracker',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    access_time_records = db.relationship(
        'AccessTimeTracker',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    access_location_records = db.relationship(
        'AccessLocationTracker',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # --- 已修改：使用 back_populates 来连接 User-UserRole 关系 ---
    user_roles_association = db.relationship(
        'UserRole',
        back_populates='user_obj',  # 链接到 UserRole 上的 'user_obj' 关系
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

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


class Role(db.Model):
    """角色表"""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Integer, default=0)  # 位掩码存储权限
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- 已修改：使用 back_populates 来连接 Role-UserRole 关系 ---
    role_users_association = db.relationship(
        'UserRole',
        back_populates='role_obj',  # 链接到 UserRole 上的 'role_obj' 关系
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions
        }


class UserRole(db.Model):
    """用户-角色关系表"""
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- 已修改：使用 back_populates 链接回 User 和 Role 模型 ---
    user_obj = db.relationship(
        'User',
        back_populates='user_roles_association'  # 链接到 User 上的 'user_roles_association' 关系
    )
    role_obj = db.relationship(
        'Role',
        back_populates='role_users_association'  # 链接到 Role 上的 'role_users_association' 关系
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AccessSuccessTracker(db.Model):
    """访问成功率追踪表"""
    __tablename__ = 'access_success_tracker'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ast_num_as = db.Column(db.Integer, default=0, comment='访问成功次数')
    ast_num_af = db.Column(db.Integer, default=0, comment='访问失败次数')
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_success_rate(self):
        total = self.ast_num_as + self.ast_num_af
        return self.ast_num_as / total if total > 0 else 0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'success_count': self.ast_num_as,
            'failure_count': self.ast_num_af,
            'success_rate': self.calculate_success_rate(),
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None
        }


class OperationBehaviorTracker(db.Model):
    """访问操作行为追踪表"""
    __tablename__ = 'operation_behavior_tracker'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ob_num_view = db.Column(db.Integer, default=0, comment='查看次数')
    ob_num_copy = db.Column(db.Integer, default=0, comment='复制次数')
    ob_num_download = db.Column(db.Integer, default=0, comment='下载次数')
    ob_num_add = db.Column(db.Integer, default=0, comment='添加次数')
    ob_num_revise = db.Column(db.Integer, default=0, comment='修改次数')
    ob_num_delete = db.Column(db.Integer, default=0, comment='删除次数')
    ob_a = db.Column(db.Float, default=0.3, comment='权重系数a')
    ob_b = db.Column(db.Float, default=0.3, comment='权重系数b')
    ob_c = db.Column(db.Float, default=0.4, comment='权重系数c')
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_behavior_score(self):
        read_ops = self.ob_num_view + self.ob_num_copy + self.ob_num_download
        write_ops = self.ob_num_add + self.ob_num_revise
        delete_ops = self.ob_num_delete
        return read_ops * self.ob_a + write_ops * self.ob_b + delete_ops * self.ob_c

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'view_count': self.ob_num_view,
            'copy_count': self.ob_num_copy,
            'download_count': self.ob_num_download,
            'add_count': self.ob_num_add,
            'revise_count': self.ob_num_revise,
            'delete_count': self.ob_num_delete,
            'behavior_score': self.calculate_behavior_score(),
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None
        }


class DataSensitivityTracker(db.Model):
    """访问数据敏感度追踪表"""
    __tablename__ = 'data_sensitivity_tracker'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ds_num1 = db.Column(db.Integer, default=0, comment='敏感度级别1访问次数')
    ds_num2 = db.Column(db.Integer, default=0, comment='敏感度级别2访问次数')
    ds_num3 = db.Column(db.Integer, default=0, comment='敏感度级别3访问次数')
    ds_num4 = db.Column(db.Integer, default=0, comment='敏感度级别4访问次数')
    ds_a = db.Column(db.Float, default=1.0, comment='敏感度级别1权重')
    ds_b = db.Column(db.Float, default=1.0, comment='敏感度级别2权重')
    ds_c = db.Column(db.Float, default=1.0, comment='敏感度级别3权重')
    ds_d = db.Column(db.Float, default=1.0, comment='敏感度级别4权重')
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_sensitivity_score(self):
        return (self.ds_num1 * self.ds_a + self.ds_num2 * self.ds_b +
                self.ds_num3 * self.ds_c + self.ds_num4 * self.ds_d)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'level1_count': self.ds_num1,
            'level2_count': self.ds_num2,
            'level3_count': self.ds_num3,
            'level4_count': self.ds_num4,
            'sensitivity_score': self.calculate_sensitivity_score(),
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None
        }


class AccessTimeTracker(db.Model):
    """访问时间追踪表"""
    __tablename__ = 'access_time_tracker'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ap_num_ni = db.Column(db.Integer, default=0, comment='正常时间访问次数')
    ap_num_ui = db.Column(db.Integer, default=0, comment='异常时间访问次数')
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_normal_time_ratio(self):
        total = self.ap_num_ni + self.ap_num_ui
        return self.ap_num_ni / total if total > 0 else 0

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'normal_time_count': self.ap_num_ni,
            'unusual_time_count': self.ap_num_ui,
            'normal_time_ratio': self.calculate_normal_time_ratio(),
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None
        }


class AccessLocationTracker(db.Model):
    """访问IP/地点追踪表"""
    __tablename__ = 'access_location_tracker'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    at_num_nd = db.Column(db.Integer, default=0, comment='正常地点访问次数')
    at_num_ad = db.Column(db.Integer, default=0, comment='异常地点访问次数')
    last_ip = db.Column(db.String(45), comment='最后访问IP')
    ip_history = db.Column(db.Text, comment='IP历史记录(JSON格式)')
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_normal_location_ratio(self):
        total = self.at_num_nd + self.at_num_ad
        return self.at_num_nd / total if total > 0 else 0

    def add_ip_to_history(self, ip):
        try:
            history = json.loads(self.ip_history) if self.ip_history else []
        except:
            history = []

        history.append({
            'ip': ip,
            'timestamp': datetime.utcnow().isoformat()
        })

        # 只保留最近100条记录
        if len(history) > 100:
            history = history[-100:]

        self.ip_history = json.dumps(history)
        self.last_ip = ip

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'normal_location_count': self.at_num_nd,
            'abnormal_location_count': self.at_num_ad,
            'normal_location_ratio': self.calculate_normal_location_ratio(),
            'last_ip': self.last_ip,
            'date_recorded': self.date_recorded.isoformat() if self.date_recorded else None
        }

