def check_duplicate_results(data):
    """
    检查results数组中是否存在完全相同的记录

    参数:
        data: 包含results列表的字典，即API返回的完整数据结构

    返回:
        1: 如果存在完全相同的记录
        0: 否则
    """
    # 提取results列表
    records = data.get('results', [])

    # 用于存储已见过的记录
    seen_records = set()

    for record in records:
        # 将字典转换为可哈希的元组，以便存入集合
        # 对键进行排序确保比较的一致性
        record_tuple = tuple(sorted(record.items()))

        # 如果该记录已存在于集合中，则说明有重复
        if record_tuple in seen_records:
            return 1

        # 否则将记录加入集合
        seen_records.add(record_tuple)

    # 没有发现重复记录
    return 0


# 示例用法
if __name__ == "__main__":
    # 示例数据
    sample_data = {
        "client_ip": "127.0.0.1",
        "data_codes": [
            "ldl_cholesterol",
            "left_ventricular_ejection_fraction"
        ],
        "institutions": [
            "ins1",
            "ins2"
        ],
        "is_whitelist_ip": True,
        "is_working_time": True,
        "message": "成功查询到10条数据",
        "requested_nums": 5,
        "results": [
            {
                "institution": "ins1",
                "ldl_cholesterol": "3.5046120017126183",
                "left_ventricular_ejection_fraction": "45.69497986133186",
                "medical_record_num": "1"
            },
            {
                "institution": "ins1",
                "ldl_cholesterol": "3.960358053564273",
                "left_ventricular_ejection_fraction": "62.84195032832028",
                "medical_record_num": "2"
            },

            {
                "institution": "ins1",
                "ldl_cholesterol": "3.960358053564273",
                "left_ventricular_ejection_fraction": "62.84195032832028",
                "medical_record_num": "2"
            },
        ],
        "status": "success",
        "total_count": 10
    }

    # 检查重复记录
    result = check_duplicate_results(sample_data)
    print(f"检查结果: {result}")  # 1表示存在完全相同的信息，0表示不存在
