from utils.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# modules/data_management/models.py
from utils.extensions import db
from datetime import datetime
import json

# ------------------- 访问成功率追踪 -------------------
class AccessSuccessTracker(db.Model):
    __tablename__ = 'access_success_tracker'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ast_num_as = db.Column(db.Integer, default=0, comment='访问成功次数')
    ast_num_af = db.Column(db.Integer, default=0, comment='访问失败次数')
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # 业务计算
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

# ------------------- 操作行为追踪 -------------------
class OperationBehaviorTracker(db.Model):
    __tablename__ = 'operation_behavior_tracker'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ob_num_view      = db.Column(db.Integer, default=0)
    ob_num_copy      = db.Column(db.Integer, default=0)
    ob_num_download  = db.Column(db.Integer, default=0)
    ob_num_add       = db.Column(db.Integer, default=0)
    ob_num_revise    = db.Column(db.Integer, default=0)
    ob_num_delete    = db.Column(db.Integer, default=0)
    ob_a = db.Column(db.Float, default=0.3)
    ob_b = db.Column(db.Float, default=0.3)
    ob_c = db.Column(db.Float, default=0.4)
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    def calculate_behavior_score(self):
        read_ops   = self.ob_num_view + self.ob_num_copy + self.ob_num_download
        write_ops  = self.ob_num_add + self.ob_num_revise
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

# ------------------- 数据敏感度追踪 -------------------
class DataSensitivityTracker(db.Model):
    __tablename__ = 'data_sensitivity_tracker'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ds_num1 = db.Column(db.Integer, default=0)
    ds_num2 = db.Column(db.Integer, default=0)
    ds_num3 = db.Column(db.Integer, default=0)
    ds_num4 = db.Column(db.Integer, default=0)
    ds_a = db.Column(db.Float, default=1.0)
    ds_b = db.Column(db.Float, default=1.0)
    ds_c = db.Column(db.Float, default=1.0)
    ds_d = db.Column(db.Float, default=1.0)
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

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

# ------------------- 访问时间追踪 -------------------
class AccessTimeTracker(db.Model):
    __tablename__ = 'access_time_tracker'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ap_num_ni = db.Column(db.Integer, default=0)
    ap_num_ui = db.Column(db.Integer, default=0)
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

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

# ------------------- 访问地点/IP 追踪 -------------------
class AccessLocationTracker(db.Model):
    __tablename__ = 'access_location_tracker'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    at_num_nd = db.Column(db.Integer, default=0)
    at_num_ad = db.Column(db.Integer, default=0)
    last_ip   = db.Column(db.String(45))
    ip_history = db.Column(db.Text)           # JSON 字符串
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    def calculate_normal_location_ratio(self):
        total = self.at_num_nd + self.at_num_ad
        return self.at_num_nd / total if total > 0 else 0

    def add_ip_to_history(self, ip):
        try:
            history = json.loads(self.ip_history) if self.ip_history else []
        except Exception:      # 若历史字段损坏，回退为空
            history = []
        history.append({'ip': ip, 'timestamp': datetime.utcnow().isoformat()})
        history = history[-100:] if len(history) > 100 else history
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
