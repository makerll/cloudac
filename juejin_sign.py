#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金社区自动签到脚本
"""
import requests
import time
import random
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL验证警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ==================== 配置区域 ====================
# Cookie配置（从浏览器中获取）
COOKIE = "_tea_utm_cache_2608=undefined; __tea_cookie_tokens_2608=%257B%2522web_id%2522%253A%25227599900289718863423%2522%252C%2522user_unique_id%2522%253A%25227599900289718863423%2522%252C%2522timestamp%2522%253A1769489691101%257D; passport_csrf_token=a3ea02965f1f21234f48f9652534d256; passport_csrf_token_default=a3ea02965f1f21234f48f9652534d256; n_mh=nM1xhw_Z4qLv3wYKe_o_Lfp-bU-qyPh9U8jfmNE5dWs; sid_guard=86e9e3ba4acaf2c8591f8c1259f22cdb%7C1769489700%7C31536000%7CWed%2C+27-Jan-2027+04%3A55%3A00+GMT; uid_tt=a054b99f6496a17ff35d6b4eafcc7bda; uid_tt_ss=a054b99f6496a17ff35d6b4eafcc7bda; sid_tt=86e9e3ba4acaf2c8591f8c1259f22cdb; sessionid=86e9e3ba4acaf2c8591f8c1259f22cdb; sessionid_ss=86e9e3ba4acaf2c8591f8c1259f22cdb; session_tlb_tag=sttt%7C16%7ChunjukrK8shZH4wSWfIs2__________m7UkD9BpjNy7D0EDmZ6woEp9gmv1KW-h8nuncb_kZYcA%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KDAzMjViY2ZhODFiZGNhNTVjZjIyNzYzNWRmOTJmYTY2Y2Y3Njk3YjUKFwjdxqDA_fWdAxCkiuHLBhiwFDgCQO8HGgJsZiIgODZlOWUzYmE0YWNhZjJjODU5MWY4YzEyNTlmMjJjZGI; ssid_ucp_v1=1.0.0-KDAzMjViY2ZhODFiZGNhNTVjZjIyNzYzNWRmOTJmYTY2Y2Y3Njk3YjUKFwjdxqDA_fWdAxCkiuHLBhiwFDgCQO8HGgJsZiIgODZlOWUzYmE0YWNhZjJjODU5MWY4YzEyNTlmMjJjZGI; csrf_session_id=d45dfcace40fa551baf07e6cb08f42a5; _tea_utm_cache_576092=undefined"  # 本地测试时使用的Cookie

# 尝试从外部配置文件导入Cookie（用于GitHub Action）
try:
    from cookie_config import COOKIE
except ImportError:
    pass

# API配置
BASE_URL = "https://api.juejin.cn/growth_api/v1/"
CHECK_IN_URL = BASE_URL + "check_in"
GET_STATUS_URL = BASE_URL + "get_today_status"

# 随机User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0'
]

# 获取随机请求头
def get_random_headers():
    """
    获取随机请求头
    """
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type': 'application/json',
        'Cookie': COOKIE,
        'User-Agent': random.choice(USER_AGENTS),
        'Referer': 'https://juejin.cn/',
        'Origin': 'https://juejin.cn',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
    }
# ==================== 配置区域结束 ====================

def get_today_status():
    """
    获取今天是否已签到
    """
    try:
        # 使用随机请求头
        headers = get_random_headers()
        # 添加随机延迟
        time.sleep(random.uniform(0.5, 2))
        response = requests.get(GET_STATUS_URL, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('err_no') == 0:
                return data.get('data', False)
            else:
                print(f"获取签到状态失败: {data.get('err_msg')}")
        else:
            print(f"获取签到状态请求失败: {response.status_code}")
    except Exception as e:
        print(f"获取签到状态异常: {str(e)}")
    return False

def check_in():
    """
    执行签到操作
    """
    try:
        # 使用随机请求头
        headers = get_random_headers()
        # 添加随机延迟
        time.sleep(random.uniform(0.5, 2))
        response = requests.post(CHECK_IN_URL, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('err_no') == 0:
                print(f"签到成功！获得矿石: {data.get('data', {}).get('incr_point', 0)}")
                print(f"当前矿石: {data.get('data', {}).get('total_point', 0)}")
                return True
            else:
                print(f"签到失败: {data.get('err_msg')}")
        else:
            print(f"签到请求失败: {response.status_code}")
    except Exception as e:
        print(f"签到异常: {str(e)}")
    return False

def main():
    """
    主函数
    """
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始执行掘金签到")
    
    # 添加随机延迟（1-300秒），模拟真实用户行为
    random_delay = random.randint(1, 300)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 随机延迟 {random_delay} 秒后执行签到")
    time.sleep(random_delay)
    
    # 检查今天是否已签到
    is_signed = get_today_status()
    if is_signed:
        print("今天已经签到过了，无需重复签到")
        return
    
    # 执行签到
    success = check_in()
    if success:
        print("签到完成！")
    else:
        print("签到失败，请检查配置")

if __name__ == "__main__":
    main()
