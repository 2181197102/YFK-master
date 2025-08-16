from utils.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# modules/data_management/models.py
from utils.extensions import db
from datetime import datetime
import json

# ------------------- 用户logs ----------------------
class UserLogs(db.Model):
    """用户日志表 - 记录用户的访问操作"""
    __tablename__ = 'user_logs'

    id = db.Column(db.String(20), primary_key=True)
    id_num = db.Column(db.String(20), nullable=False, comment='身份证号')
    access_timestamp = db.Column(db.TIMESTAMP, nullable=False, comment='发生时间戳')
    access_ip = db.Column(db.String(45), nullable=False, comment='访问IP地址')
    operation_type = db.Column(db.Enum('VIEW', 'COPY', 'DOWNLOAD', 'ADD', 'REVISE', 'DELETE', 
                                      name='operation_type_enum'), nullable=False, comment='访问操作类型')
    target_data_sensitivity = db.Column(db.Enum('QUASI_IDENTIFIER', 'EXPLICIT_IDENTIFIER', 
                                               'LOW_SENSITIVITY', 'HIGH_SENSITIVITY', 
                                               name='data_sensitivity_enum'), nullable=False, comment='数据敏感度级别')
    target_disease_codes = db.Column(db.Text, nullable=False, comment='疾病ICD编码列表，JSON格式存储')
    access_status = db.Column(db.Enum('SUCCESS', 'FAILURE', 'DENIED', 
                                     name='access_status_enum'), nullable=False, comment='访问请求的结果')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def get_disease_codes_list(self):
        """获取疾病编码列表"""
        try:
            return json.loads(self.target_disease_codes) if self.target_disease_codes else []
        except json.JSONDecodeError:
            return []

    def set_disease_codes_list(self, codes_list):
        """设置疾病编码列表"""
        self.target_disease_codes = json.dumps(codes_list)

    def to_dict(self):
        return {
            'id': self.id,
            'id_num': self.id_num,
            'access_timestamp': self.access_timestamp.isoformat() if self.access_timestamp else None,
            'access_ip': self.access_ip,
            'operation_type': self.operation_type,
            'target_data_sensitivity': self.target_data_sensitivity,
            'target_disease_codes': self.get_disease_codes_list(),
            'access_status': self.access_status,
            'created_time': self.created_time.isoformat() if self.created_time else None
        }

# ------------------- 用户访问敏感数据统计表 -------------------
class UserAccessSensitiveData(db.Model):
    """用户访问敏感数据统计表"""
    __tablename__ = 'user_access_sensitive_data'

    id = db.Column(db.String(20), primary_key=True)
    id_num = db.Column(db.String(20), nullable=False, comment='身份证号')
    ds_num1 = db.Column(db.SmallInteger, nullable=False, default=0, comment='准标识符访问次数')
    ds_num2 = db.Column(db.SmallInteger, nullable=False, default=0, comment='显示标识符访问次数')
    ds_num3 = db.Column(db.SmallInteger, nullable=False, default=0, comment='低敏感数据访问次数')
    ds_num4 = db.Column(db.SmallInteger, nullable=False, default=0, comment='高敏感数据访问次数')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def calculate_sensitivity_score(self, weights=None):
        """计算敏感度评分"""
        if weights is None:
            # 根据设计文档中的风险等级设置默认权重
            weights = {
                'quasi_identifier_risk': 0.1,
                'explicit_identifier_risk': 0.4,
                'low_sensitivity_risk': 0.2,
                'high_sensitivity_risk': 0.3
            }
        
        return (self.ds_num1 * weights['quasi_identifier_risk'] + 
                self.ds_num2 * weights['explicit_identifier_risk'] +
                self.ds_num3 * weights['low_sensitivity_risk'] + 
                self.ds_num4 * weights['high_sensitivity_risk'])

    def to_dict(self):
        return {
            'id': self.id,
            'id_num': self.id_num,
            'quasi_identifier_count': self.ds_num1,
            'explicit_identifier_count': self.ds_num2,
            'low_sensitivity_count': self.ds_num3,
            'high_sensitivity_count': self.ds_num4,
            'sensitivity_score': self.calculate_sensitivity_score(),
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ------------------- 用户访问地点统计表 -------------------
class UserAccessLocationTracker(db.Model):
    """用户访问地点统计表"""
    __tablename__ = 'user_access_location_tracker'

    id = db.Column(db.String(20), primary_key=True)
    id_num = db.Column(db.String(20), nullable=False, comment='身份证号')
    at_num_nd = db.Column(db.SmallInteger, nullable=False, default=0, comment='正常地点访问次数')
    at_num_ad = db.Column(db.SmallInteger, nullable=False, default=0, comment='异常地点访问次数')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def calculate_normal_location_ratio(self):
        """计算正常地点访问比例"""
        total = self.at_num_nd + self.at_num_ad
        return self.at_num_nd / total if total > 0 else 0

    def to_dict(self):
        return {
            'id': self.id,
            'id_num': self.id_num,
            'normal_location_count': self.at_num_nd,
            'abnormal_location_count': self.at_num_ad,
            'normal_location_ratio': self.calculate_normal_location_ratio(),
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ------------------- 用户常用IP表 ----------------------
class UserIps(db.Model):
    """用户常用IP表"""
    __tablename__ = 'user_ips'

    id = db.Column(db.String(20), primary_key=True)
    id_num = db.Column(db.String(20), nullable=False, comment='身份证号')
    ip_address = db.Column(db.String(45), nullable=False, comment='IP地址')
    access_count = db.Column(db.SmallInteger, nullable=False, default=0, comment='IP访问次数')
    last_seen = db.Column(db.TIMESTAMP, nullable=False, comment='最后一次使用时间')

    def to_dict(self):
        return {
            'id': self.id,
            'id_num': self.id_num,
            'ip_address': self.ip_address,
            'access_count': self.access_count,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

# ------------------- 用户访问成功率统计表 -------------------
class UserAccessSuccessTracker(db.Model):
    """用户访问成功率统计表"""
    __tablename__ = 'user_access_success_tracker'

    id = db.Column(db.String(20), primary_key=True)
    id_num = db.Column(db.String(20), nullable=False, comment='身份证号')
    ast_num_as = db.Column(db.SmallInteger, nullable=False, default=0, comment='访问成功次数')
    ast_num_af = db.Column(db.SmallInteger, nullable=False, default=0, comment='访问失败次数')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def calculate_success_rate(self):
        """计算访问成功率"""
        total = self.ast_num_as + self.ast_num_af
        return self.ast_num_as / total if total > 0 else 0

    def to_dict(self):
        return {
            'id': self.id,
            'id_num': self.id_num,
            'success_count': self.ast_num_as,
            'failure_count': self.ast_num_af,
            'success_rate': self.calculate_success_rate(),
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }


# ------------------- 用户访问时间统计表 -------------------
class UserAccessTimeTracker(db.Model):
    """用户访问时间统计表"""
    __tablename__ = 'user_access_time_tracker'

    id = db.Column(db.String(20), primary_key=True)
    id_num = db.Column(db.String(20), nullable=False, comment='身份证号')
    ap_num_ni = db.Column(db.SmallInteger, nullable=False, default=0, comment='正常时间访问次数')
    ap_num_ui = db.Column(db.SmallInteger, nullable=False, default=0, comment='异常时间访问次数')
    work_time = db.Column(db.Text, nullable=True, comment='正常访问时间，JSON格式存储')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def calculate_normal_time_ratio(self):
        """计算正常时间访问比例"""
        total = self.ap_num_ni + self.ap_num_ui
        return self.ap_num_ni / total if total > 0 else 0

    def get_work_time_list(self):
        """获取正常访问时间列表"""
        try:
            return json.loads(self.work_time) if self.work_time else []
        except json.JSONDecodeError:
            return []

    def set_work_time_list(self, time_list):
        """设置正常访问时间列表"""
        self.work_time = json.dumps(time_list, default=str)

    def to_dict(self):
        return {
            'id': self.id,
            'id_num': self.id_num,
            'normal_time_count': self.ap_num_ni,
            'unusual_time_count': self.ap_num_ui,
            'normal_time_ratio': self.calculate_normal_time_ratio(),
            'work_time': self.get_work_time_list(),
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ------------------- 用户操作行为统计表 -------------------
class UserOperationBehaviorTracker(db.Model):
    """用户操作行为统计表"""
    __tablename__ = 'user_operation_behavior_tracker'

    id = db.Column(db.String(20), primary_key=True)
    id_num = db.Column(db.String(20), nullable=False, comment='身份证号')
    ob_num_view = db.Column(db.SmallInteger, nullable=False, default=0, comment='查看次数')
    ob_num_copy = db.Column(db.SmallInteger, nullable=False, default=0, comment='复制次数')
    ob_num_download = db.Column(db.SmallInteger, nullable=False, default=0, comment='下载次数')
    ob_num_add = db.Column(db.SmallInteger, nullable=False, default=0, comment='新增次数')
    ob_num_revise = db.Column(db.SmallInteger, nullable=False, default=0, comment='修改次数')
    ob_num_delet = db.Column(db.SmallInteger, nullable=False, default=0, comment='删除次数')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def calculate_behavior_score(self, weights=None):
        """计算操作行为评分"""
        if weights is None:
            # 根据设计文档中的操作行为风险等级设置默认权重
            weights = {
                'view_risk': 0.1,
                'copy_download_risk': 0.3,
                'add_modify_delete_risk': 0.6
            }
        
        view_ops = self.ob_num_view
        copy_download_ops = self.ob_num_copy + self.ob_num_download
        modify_ops = self.ob_num_add + self.ob_num_revise + self.ob_num_delet
        
        return (view_ops * weights['view_risk'] + 
                copy_download_ops * weights['copy_download_risk'] +
                modify_ops * weights['add_modify_delete_risk'])

    def to_dict(self):
        return {
            'id': self.id,
            'id_num': self.id_num,
            'view_count': self.ob_num_view,
            'copy_count': self.ob_num_copy,
            'download_count': self.ob_num_download,
            'add_count': self.ob_num_add,
            'revise_count': self.ob_num_revise,
            'delete_count': self.ob_num_delet,
            'behavior_score': self.calculate_behavior_score(),
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ------------------- ICD‑10 码表 -------------------
class ICD10Code(db.Model):
    """
    国际疾病分类第十版（ICD‑10）编码模型
    """
    __tablename__ = 'sys_icd10_codes'
    __table_args__ = (
        db.UniqueConstraint('code', name='uq_icd10_code'),
        db.Index('idx_icd10_chapter', 'chapter'),
        db.Index('idx_icd10_description', 'description')
    )

    # 通用主键
    id = db.Column(db.Integer, primary_key=True)

    # ICD‑10 结构化字段
    chapter        = db.Column(db.String(7),  nullable=False, comment='章/类别，如 A00')
    subcategory    = db.Column(db.String(7),  nullable=True, comment='细分类，如 0、1、9')
    code           = db.Column(db.String(10),  nullable=False, comment='完整编码，如 A000')
    description    = db.Column(db.String(512), nullable=False, comment='官方长描述')
    alt_desc       = db.Column(db.String(512), nullable=True,  comment='备用长描述（如果有）')
    short_desc     = db.Column(db.String(256), nullable=True,  comment='简短描述 / 疾病名称')

    # 统一的审计字段
    created_time   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_time   = db.Column(db.DateTime, default=datetime.utcnow,
                               onupdate=datetime.utcnow)

    # ---------- 工具方法 ----------
    def to_dict(self):
        return {
            "id": self.id,
            "chapter": self.chapter,
            "subcategory": self.subcategory,
            "code": self.code,
            "description": self.description,
            "alt_desc": self.alt_desc,
            "short_desc": self.short_desc,
        }

    @staticmethod
    def search_by_code(keyword: str, limit: int = 10):
        """
        按完整编码或编码前缀模糊查询
        """
        return (ICD10Code.query
                .filter(ICD10Code.code.ilike(f"{keyword}%"))
                .limit(limit)
                .all())

    @staticmethod
    def search_by_text(keyword: str, limit: int = 10):
        """
        按中文/英文描述关键字模糊查询
        """
        pattern = f"%{keyword}%"
        return (ICD10Code.query
                .filter(db.or_(ICD10Code.description.ilike(pattern),
                               ICD10Code.alt_desc.ilike(pattern),
                               ICD10Code.short_desc.ilike(pattern)))
                .limit(limit)
                .all())

    def __repr__(self):
        return f"<ICD10Code {self.code} – {self.short_desc or self.description[:30]}>"

# ------------------- 病种-数据项字段表 -------------------
class DiseaseDataItem(db.Model):
    """病种-数据项字段表"""
    __tablename__ = 'disease_data_item'

    id = db.Column(db.String(20), primary_key=True)
    disease_code = db.Column(db.String(20), db.ForeignKey('sys_icd10_codes.code'), nullable=False, comment='病种代码，ICD-10外键')
    disease_name = db.Column(db.String(200), nullable=False, comment='病种名称')
    description = db.Column(db.String(500), nullable=False, comment='病种描述')
    associated_fields = db.Column(db.Text, nullable=False, comment='数据项列表，JSON格式存储')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # 建立与ICD10Code的关系
    icd_code = db.relationship('ICD10Code', backref='disease_data_items')

    def get_associated_fields_list(self):
        """获取关联数据项列表"""
        try:
            return json.loads(self.associated_fields) if self.associated_fields else []
        except json.JSONDecodeError:
            return []

    def set_associated_fields_list(self, fields_list):
        """设置关联数据项列表"""
        self.associated_fields = json.dumps(fields_list, ensure_ascii=False)

    def to_dict(self):
        return {
            'id': self.id,
            'disease_code': self.disease_code,
            'disease_name': self.disease_name,
            'description': self.description,
            'associated_fields': self.get_associated_fields_list(),
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }