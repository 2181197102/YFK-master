# modules/medical_institutions/models.py
"""
医疗机构相关数据模型
根据数据库设计part2.md中的医疗机构数据库部分实现
"""

from utils.extensions import db
from datetime import datetime
import json


class PatientMedicalRecord(db.Model):
    """患者病历表"""
    __tablename__ = 'patient_medical_record'

    id = db.Column(db.String(20), primary_key=True, comment='病历号')
    patient_id_num = db.Column(db.String(20), nullable=False, comment='患者身份证号')
    patient_name = db.Column(db.String(20), nullable=False, comment='患者姓名')
    patient_sex = db.Column(db.SmallInteger, nullable=False, comment='患者性别，1男2女')
    doctor_code = db.Column(db.String(20), nullable=False, comment='主治医师代码')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.id,  # 病历号
            'patient_id_num': self.patient_id_num,
            'patient_name': self.patient_name,
            'patient_sex': self.patient_sex,
            'patient_sex_text': '男' if self.patient_sex == 1 else '女',
            'doctor_code': self.doctor_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

    def __repr__(self):
        return f"<PatientMedicalRecord {self.id} - {self.patient_name}>"


class MedicalRecordDisease(db.Model):
    """病历-病种表"""
    __tablename__ = 'medical_record_disease'

    id = db.Column(db.String(20), primary_key=True)
    medical_record_num = db.Column(db.String(20), 
                                 db.ForeignKey('patient_medical_record.id'), 
                                 nullable=False, comment='病历号')
    disease_code = db.Column(db.String(20), nullable=False, comment='病种代码')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # 建立与患者病历表的关系
    medical_record = db.relationship('PatientMedicalRecord', backref='diseases')

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'disease_code': self.disease_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

    def __repr__(self):
        return f"<MedicalRecordDisease {self.medical_record_num} - {self.disease_code}>"


class MedicalRecordDataItem(db.Model):
    """病历-数据项表"""
    __tablename__ = 'medical_record_data_item'

    id = db.Column(db.String(20), primary_key=True)
    medical_record_num = db.Column(db.String(20), 
                                 db.ForeignKey('patient_medical_record.id'),
                                 nullable=False, comment='病历号')
    associated_code = db.Column(db.String(20), nullable=False, comment='数据项代码')
    # 动态数据项字段 - 使用JSON存储不同类型的医疗数据
    data_fields = db.Column(db.Text, nullable=True, comment='数据项内容，JSON格式存储')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # 建立与患者病历表的关系
    medical_record = db.relationship('PatientMedicalRecord', backref='data_items')

    def get_data_fields_dict(self):
        """获取数据项内容字典"""
        try:
            return json.loads(self.data_fields) if self.data_fields else {}
        except json.JSONDecodeError:
            return {}

    def set_data_fields_dict(self, fields_dict):
        """设置数据项内容字典"""
        self.data_fields = json.dumps(fields_dict, ensure_ascii=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'associated_code': self.associated_code,
            'data_fields': self.get_data_fields_dict(),
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

    def __repr__(self):
        return f"<MedicalRecordDataItem {self.medical_record_num} - {self.associated_code}>"


class DoctorMedicalRecord(db.Model):
    """医生-病历表"""
    __tablename__ = 'doctor_medical_record'

    id = db.Column(db.String(20), primary_key=True)
    doctor_name = db.Column(db.String(20), nullable=False, comment='医生姓名')
    doctor_code = db.Column(db.String(20), nullable=False, comment='医生代码')
    patient_name = db.Column(db.String(20), nullable=False, comment='病人姓名')
    patient_id_num = db.Column(db.String(20), nullable=False, comment='患者身份证号')
    medical_record_num = db.Column(db.String(20), 
                                 db.ForeignKey('patient_medical_record.id'),
                                 nullable=False, comment='病历号')
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    # 建立与患者病历表的关系
    medical_record = db.relationship('PatientMedicalRecord', backref='doctors')

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_name': self.doctor_name,
            'doctor_code': self.doctor_code,
            'patient_name': self.patient_name,
            'patient_id_num': self.patient_id_num,
            'medical_record_num': self.medical_record_num,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

    def __repr__(self):
        return f"<DoctorMedicalRecord Dr.{self.doctor_name} - {self.medical_record_num}>"
