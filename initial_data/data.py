from modules.ins.models import *
from datetime import datetime
import random

MEDICAL_RECORD_EXAMPLES = [
    "I10", "I25.1", "E10", "J44"
]
time = [5, 4, 5, 5]

similarlist = [0.2, 0.1, 0.4, 0.3]
sensitivelist = [[0.8, 0.6, 0.8, 0.8, 0.2], [0.4, 0.8, 0.8, 0.8], [0.1, 0.8, 0.6, 0.2, 0.1], [0.2, 0.2, 0.6, 0.6, 0.6]]


def insert_data(db):
    """为每个病种从data_code1到data_code9中随机选择一个字段，创建新记录"""
    print("  - 正在为病种添加数据项…")

    # 定义所有可能的data_code字段
    data_code_fields = [['HYP_HX',
                         'CRP',
                         'BIO_FBG',
                         'BIO_PBG',
                         'SHS_EXP'],
                         ['HR',
                         'BP',
                         'BG',
                         'BL_LIPID'],
                         ['EXE_FREQ_WK',
                         'INS_DOS_PER',
                         'O2_DUR',
                         'DRUNK_MARK',
                         'STAP_INTAKE_D'],
                         ['SMK_START_AGE',
                         'SMK_QUIT_AGE',
                         'PFT_TLC',
                         'PFT_FRC',
                         'PFT_DLCO']
                         ]
    i = 0
    for disease_code in MEDICAL_RECORD_EXAMPLES:
        # 随机选择一个data_code字段
        # selected_fields = random.sample(data_code_fields, time[i])
        # similar = random.sample(similarlist, 1)

        for j in range(time[i]):
            data_code = data_code_fields[i][j]
            sensitive = sensitivelist[i][j]
            # 创建记录，只设置选中的data_code字段
            record = Disease_data(
                disease_code=disease_code,
                data_code=data_code,
                similar=similarlist[i],
                sensitive=sensitive,
                created_time=datetime.utcnow(),
                updated_time=datetime.utcnow(),
            )

            db.session.add(record)
        i = i + 1
        print(f"    已为病种 '{disease_code}' 添加 {data_code} 数据项")
