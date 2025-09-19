# initial_data/11_whitelist_data.py
"""
初始化IP白名单和工作时间白名单数据
"""

from modules.data_management.models import IPWhitelist, WorkingTimeWhitelist
from datetime import time


def insert_data(db):
    """插入白名单初始数据"""
    
    # 1. 插入IP白名单数据
    ip_whitelist_data = [
        {
            'ip_address': '127.0.0.1',
            'description': '本地回环地址',
            'is_active': True
        },
        {
            'ip_address': '192.168.0.0/16',
            'description': '内网地址段',
            'is_active': True
        },
        {
            'ip_address': '10.0.0.0/8',
            'description': '内网地址段',
            'is_active': True
        },
        {
            'ip_address': '172.16.0.0/12',
            'description': '内网地址段',
            'is_active': True
        }
    ]
    
    for ip_data in ip_whitelist_data:
        existing_ip = IPWhitelist.query.filter_by(ip_address=ip_data['ip_address']).first()
        if not existing_ip:
            ip_record = IPWhitelist(**ip_data)
            db.session.add(ip_record)
            print(f"Added IP whitelist: {ip_data['ip_address']}")
    
    # 2. 插入工作时间白名单数据
    working_time_data = [
        {
            'day_of_week': 0,  # 周一
            'start_time': time(9, 0, 0),  # 09:00:00
            'end_time': time(17, 0, 0),  # 17:00:00
            'description': '周一工作时间',
            'is_active': True
        },
        {
            'day_of_week': 1,  # 周二
            'start_time': time(9, 0, 0),
            'end_time': time(17, 0, 0),
            'description': '周二工作时间',
            'is_active': True
        },
        {
            'day_of_week': 2,  # 周三
            'start_time': time(9, 0, 0),
            'end_time': time(17, 0, 0),
            'description': '周三工作时间',
            'is_active': True
        },
        {
            'day_of_week': 3,  # 周四
            'start_time': time(9, 0, 0),
            'end_time': time(17, 0, 0),
            'description': '周四工作时间',
            'is_active': True
        },
        {
            'day_of_week': 4,  # 周五
            'start_time': time(9, 0, 0),
            'end_time': time(17, 0, 0),
            'description': '周五工作时间',
            'is_active': True
        },
        {
            'day_of_week': 5,  # 周六
            'start_time': time(9, 0, 0),
            'end_time': time(12, 0, 0),
            'description': '周六上午工作时间',
            'is_active': True
        }
    ]
    
    for time_data in working_time_data:
        existing_time = WorkingTimeWhitelist.query.filter_by(
            day_of_week=time_data['day_of_week'],
            start_time=time_data['start_time'],
            end_time=time_data['end_time']
        ).first()
        if not existing_time:
            time_record = WorkingTimeWhitelist(**time_data)
            db.session.add(time_record)
            print(f"Added working time whitelist: {time_data['description']}")
    
    # 事务提交由 db_test_and_init.py 处理
    print("Whitelist data initialization completed")
