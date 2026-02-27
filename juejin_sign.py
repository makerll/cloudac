#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金社区自动签到脚本 - 终极浏览器模拟版
"""
import os
import requests
import time
import random
import smtplib
import ssl
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL验证警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ==================== 配置 ====================
COOKIE = os.environ.get('JUEJIN_COOKIE', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_TO = os.environ.get('EMAIL_TO', '')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.163.com')

# SMTP端口处理
SMTP_PORT_STR = os.environ.get('SMTP_PORT', '465')
try:
    SMTP_PORT = int(SMTP_PORT_STR) if SMTP_PORT_STR else 465
except ValueError:
    SMTP_PORT = 465

if not EMAIL_TO:
    EMAIL_TO = EMAIL_FROM

# API配置
BASE_URL = "https://api.juejin.cn"
CHECK_IN_URL = f"{BASE_URL}/growth_api/v1/check_in"
GET_STATUS_URL = f"{BASE_URL}/growth_api/v1/get_today_status"
LOTTERY_DRAW_URL = f"{BASE_URL}/growth_api/v1/lottery/draw"
JUEJIN_HOME_URL = "https://juejin.cn/"

# 从Cookie中提取必要的token
def extract_from_cookie(key):
    if key in COOKIE:
        start = COOKIE.find(f'{key}=') + len(f'{key}=')
        end = COOKIE.find(';', start)
        if end == -1:
            return COOKIE[start:]
        return COOKIE[start:end]
    return ''

CSRF_TOKEN = extract_from_cookie('passport_csrf_token')
SESSION_ID = extract_from_cookie('sessionid')
UID_TT = extract_from_cookie('uid_tt')

print(f"提取的CSRF Token: {CSRF_TOKEN[:10] if CSRF_TOKEN else 'None'}...")
print(f"Session ID: {SESSION_ID[:10] if SESSION_ID else 'None'}...")

# 完整的浏览器User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

def check_config():
    """检查配置"""
    missing = []
    if not COOKIE:
        missing.append('JUEJIN_COOKIE')
    if not EMAIL_FROM:
        missing.append('EMAIL_FROM')
    if not EMAIL_PASSWORD:
        missing.append('EMAIL_PASSWORD')
    
    if missing:
        print("缺失配置:", missing)
        return False
    return True

def get_browser_headers():
    """
    获取完整的浏览器请求头
    """
    # 随机选择一个User-Agent
    ua = random.choice(USER_AGENTS)
    
    # 构建完整的请求头
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': COOKIE,
        'Host': 'api.juejin.cn',
        'Origin': 'https://juejin.cn',
        'Pragma': 'no-cache',
        'Referer': 'https://juejin.cn/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': ua,
    }
    
    # 添加CSRF token
    if CSRF_TOKEN:
        headers['x-secsdk-csrf-token'] = CSRF_TOKEN
    
    return headers

def get_china_time():
    china_tz = timezone(timedelta(hours=8))
    return datetime.now(china_tz)

def format_china_time():
    return get_china_time().strftime('%Y-%m-%d %H:%M:%S')

def visit_juejin_home():
    """访问首页获取cookies"""
    try:
        session = requests.Session()
        headers = get_browser_headers()
        response = session.get(JUEJIN_HOME_URL, headers=headers, verify=False, timeout=10)
        print(f"首页状态码: {response.status_code}")
        return session
    except Exception as e:
        print(f"首页访问失败: {e}")
        return None

def get_today_status(session=None):
    """获取签到状态"""
    try:
        headers = get_browser_headers()
        if session:
            response = session.get(GET_STATUS_URL, headers=headers, verify=False, timeout=10)
        else:
            response = requests.get(GET_STATUS_URL, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200 and response.text:
            data = response.json()
            if data.get('err_no') == 0:
                return data.get('data', False)
        return False
    except Exception as e:
        print(f"获取状态异常: {e}")
        return False

def check_in_with_session(session=None):
    """
    使用session执行签到，模拟完整浏览器行为
    """
    try:
        # 构建完整的请求
        headers = get_browser_headers()
        
        # 添加时间戳参数
        timestamp = int(time.time() * 1000)
        url = f"{CHECK_IN_URL}?aid=2608&uuid={SESSION_ID}&spider=0&msToken=&a_bogus="
        
        # 准备请求数据
        data = {}
        
        print(f"发送签到请求到: {url}")
        
        # 使用session或直接请求
        if session:
            response = session.post(url, headers=headers, json=data, verify=False, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=data, verify=False, timeout=10)
        
        print(f"签到状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: '{response.text}'")
        
        if response.status_code == 200 and response.text:
            try:
                result = response.json()
                if result.get('err_no') == 0:
                    print(f"✅ 签到成功!")
                    return True
                else:
                    print(f"❌ 签到失败: {result.get('err_msg')}")
            except:
                print("响应解析失败")
        else:
            print("❌ 签到请求失败 - 空响应")
            
            # 尝试不同的URL格式
            alt_url = f"{BASE_URL}/growth_api/v1/check_in"
            print(f"尝试备用URL: {alt_url}")
            
            alt_headers = headers.copy()
            alt_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
            if session:
                alt_response = session.post(alt_url, headers=alt_headers, data='{}', verify=False, timeout=10)
            else:
                alt_response = requests.post(alt_url, headers=alt_headers, data='{}', verify=False, timeout=10)
            
            print(f"备用请求响应: '{alt_response.text}'")
            
        return False
    except Exception as e:
        print(f"签到异常: {e}")
        return False

def lottery_draw(session=None):
    """抽奖"""
    try:
        headers = get_browser_headers()
        if session:
            response = session.post(LOTTERY_DRAW_URL, headers=headers, json={}, verify=False, timeout=10)
        else:
            response = requests.post(LOTTERY_DRAW_URL, headers=headers, json={}, verify=False, timeout=10)
        
        if response.status_code == 200 and response.text:
            data = response.json()
            if data.get('err_no') == 0:
                return data.get('data', {}).get('lottery_name', '未知')
        return "抽奖失败"
    except:
        return "抽奖失败"

def send_email(subject, content, is_html=False):
    """发送邮件"""
    try:
        if not all([EMAIL_FROM, EMAIL_PASSWORD, SMTP_SERVER]):
            print("邮件配置不完整")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        if is_html:
            msg.attach(MIMEText(content, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=30)
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print(f"✅ 邮件发送成功")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def create_email_html(sign_status, lottery_result):
    """创建邮件HTML"""
    current_time = format_china_time()
    
    status_icon = "✅" if "成功" in sign_status else "❌"
    lottery_icon = "🎁" if lottery_result not in ["抽奖失败", "今天已经抽过奖"] else "⏰" if "已经抽过" in lottery_result else "❌"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Microsoft YaHei'; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="background: #1E80FF; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0;">🎯 掘金签到</h1>
            </div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 15px; padding: 15px; background: #f5f5f5; border-radius: 6px;">
                    <div style="color: #999; font-size: 12px;">📅 时间</div>
                    <div style="font-size: 16px;">{current_time}</div>
                </div>
                <div style="margin-bottom: 15px; padding: 15px; background: #f5f5f5; border-radius: 6px;">
                    <div style="color: #999; font-size: 12px;">✍️ 签到</div>
                    <div style="font-size: 16px;">{status_icon} {sign_status}</div>
                </div>
                <div style="padding: 15px; background: #f5f5f5; border-radius: 6px;">
                    <div style="color: #999; font-size: 12px;">🎲 抽奖</div>
                    <div style="font-size: 16px;">{lottery_icon} {lottery_result}</div>
                </div>
            </div>
            <div style="background: #f5f5f5; padding: 15px; text-align: center; color: #999; font-size: 12px; border-radius: 0 0 8px 8px;">
                <p style="margin: 0;">自动签到系统 | 掘金社区</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    """主函数"""
    print(f"[{format_china_time()}] 开始执行")
    
    if not check_config():
        return
    
    # 随机延迟
    delay = random.randint(1, 30)
    print(f"延迟 {delay} 秒")
    time.sleep(delay)
    
    # 创建session并访问首页
    session = visit_juejin_home()
    if not session:
        session = requests.Session()
    
    time.sleep(random.uniform(1, 3))
    
    # 检查状态
    is_signed = get_today_status(session)
    print(f"今日签到状态: {'已签到' if is_signed else '未签到'}")
    
    if is_signed:
        lottery = lottery_draw(session)
        html = create_email_html("已签到", lottery)
        send_email("掘金签到通知", html, True)
        return
    
    # 执行签到
    print("开始签到...")
    success = check_in_with_session(session)
    
    # 抽奖
    lottery = lottery_draw(session) if success else "未执行抽奖"
    
    # 发送邮件
    status = "签到成功" if success else "签到失败"
    html = create_email_html(status, lottery)
    send_email("掘金签到通知", html, True)

if __name__ == "__main__":
    main()
