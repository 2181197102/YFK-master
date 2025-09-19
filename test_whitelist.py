#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
白名单功能测试脚本
"""

import requests
import json
from datetime import datetime, time


class WhitelistTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username="admin", password="admin123"):
        """登录获取token"""
        url = f"{self.base_url}/api/auth/login"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('data', {}).get('access_token')
                print(f"登录成功，Token: {self.token[:20]}...")
                return True
            else:
                print(f"登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"登录异常: {str(e)}")
            return False
    
    def get_headers(self):
        """获取请求头"""
        if not self.token:
            raise Exception("请先登录")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_check_status(self):
        """测试白名单状态检查"""
        print("\n=== 测试白名单状态检查 ===")
        url = f"{self.base_url}/api/whitelist/check-status"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"测试异常: {str(e)}")
    
    def test_ip_whitelist(self):
        """测试IP白名单管理"""
        print("\n=== 测试IP白名单管理 ===")
        
        # 获取IP白名单列表
        url = f"{self.base_url}/api/whitelist/ip-whitelist"
        try:
            response = requests.get(url, headers=self.get_headers())
            print(f"获取IP白名单列表:")
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"获取IP白名单异常: {str(e)}")
        
        # 添加IP白名单
        test_ip = "192.168.100.100"
        data = {
            "ip_address": test_ip,
            "description": "测试IP地址",
            "is_active": True
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            print(f"\n添加IP白名单:")
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"添加IP白名单异常: {str(e)}")
    
    def test_working_time_whitelist(self):
        """测试工作时间白名单管理"""
        print("\n=== 测试工作时间白名单管理 ===")
        
        # 获取工作时间白名单列表
        url = f"{self.base_url}/api/whitelist/working-time-whitelist"
        try:
            response = requests.get(url, headers=self.get_headers())
            print(f"获取工作时间白名单列表:")
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"获取工作时间白名单异常: {str(e)}")
        
        # 添加工作时间白名单
        data = {
            "day_of_week": 0,  # 周日
            "start_time": "10:00:00",
            "end_time": "16:00:00",
            "description": "周日测试工作时间",
            "is_active": True
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            print(f"\n添加工作时间白名单:")
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"添加工作时间白名单异常: {str(e)}")
    
    def test_medical_data_access(self):
        """测试医疗数据访问（带白名单检查）"""
        print("\n=== 测试医疗数据访问 ===")
        
        # 测试获取医疗记录数据
        url = f"{self.base_url}/api/medical_record/get_record_data"
        data = {
            "data_code": ["K_FH"],
            "nums": 5,
            "institutions": ["ins1"]
        }
        
        try:
            response = requests.post(url, json=data, headers=self.get_headers())
            print(f"获取医疗记录数据:")
            print(f"状态码: {response.status_code}")
            result = response.json()
            
            # 显示白名单检查结果
            if 'client_ip' in result:
                print(f"客户端IP: {result['client_ip']}")
                print(f"是否在白名单IP: {result['is_whitelist_ip']}")
                print(f"是否在工作时间: {result['is_working_time']}")
            
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"获取医疗数据异常: {str(e)}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始白名单功能测试...")
        
        if not self.login():
            print("登录失败，无法继续测试")
            return
        
        self.test_check_status()
        self.test_ip_whitelist()
        self.test_working_time_whitelist()
        self.test_medical_data_access()
        
        print("\n测试完成！")


if __name__ == "__main__":
    tester = WhitelistTester()
    tester.run_all_tests()
