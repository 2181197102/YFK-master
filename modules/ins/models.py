# modules/auth/models.py
from utils.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ----------------------- 病历表 -----------------------
class ins_record(db.Model):
    __tablename__ = 'ins_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # 姓名字段
    age = db.Column(db.Integer, nullable=False)  # 年龄字段
    gender = db.Column(db.String(10), nullable=False)  # 性别字段
    id_card = db.Column(db.String(18), unique=False, nullable=False)  # 身份证号码，作为唯一标识
    doctor_code = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'id_card': self.id_card,
            'doctor_code': self.doctor_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历-病种表 -----------------------
class ins_record_disease(db.Model):
    __tablename__ = 'ins_record_disease'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)  # 身份证号码，作为唯一标识
    disease_code = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'disease_code': self.disease_code,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 病历-数据项表 -----------------------
class ins_record_data(db.Model):
    __tablename__ = 'ins_record_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)  # 身份证号码，作为唯一标识
    data_code1 = db.Column(db.String(18), unique=False, nullable=False)
    data_code2 = db.Column(db.String(18), unique=False, nullable=False)
    data_code3 = db.Column(db.String(18), unique=False, nullable=False)
    data_code4 = db.Column(db.String(18), unique=False, nullable=False)
    data_code5 = db.Column(db.String(18), unique=False, nullable=False)
    data_code6 = db.Column(db.String(18), unique=False, nullable=False)
    data_code7 = db.Column(db.String(18), unique=False, nullable=False)
    data_code8 = db.Column(db.String(18), unique=False, nullable=False)
    data_code9 = db.Column(db.String(18), unique=False, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_num': self.medical_record_num,
            'data_code1': self.data_code1,
            'data_code2': self.data_code2,
            'data_code3': self.data_code3,
            'data_code4': self.data_code4,
            'data_code5': self.data_code5,
            'data_code6': self.data_code6,
            'data_code7': self.data_code7,
            'data_code8': self.data_code8,
            'data_code9': self.data_code9,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'updated_time': self.updated_time.isoformat() if self.updated_time else None
        }

# ----------------------- 医生-病历表 -----------------------
class ins_doctor_record(db.Model):
    __tablename__ = 'ins_doctor_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_name = db.Column(db.String(100), nullable=False)  # 姓名字段
    doctor_code = db.Column(db.String(18), unique=False, nullable=False)
    patient_name = db.Column(db.String(18), unique=False, nullable=False)
    patient_id_num = db.Column(db.String(18), unique=False, nullable=False)
    medical_record_num = db.Column(db.String(18), unique=True, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow, nullable=False)

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