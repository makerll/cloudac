#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金社区自动签到脚本 - 最终版
"""
import os
import requests
import time
import random
import smtplib
import ssl
import json
import urllib.parse
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

try:
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '465'))
except:
    SMTP_PORT = 465

if not EMAIL_TO:
    EMAIL_TO = EMAIL_FROM

# API配置
BASE_URL = "https://api.juejin.cn"
CHECK_IN_URL = f"{BASE_URL}/growth_api/v1/check_in"
GET_STATUS_URL = f"{BASE_URL}/growth_api/v1/get_today_status"
LOTTERY_DRAW_URL = f"{BASE_URL}/growth_api/v1/lottery/draw"
JUEJIN_HOME_URL = "https://juejin.cn/"

def extract_from_cookie(key):
    """从Cookie中提取指定key的值"""
    if key in COOKIE:
        start = COOKIE.find(f'{key}=') + len(f'{key}=')
        end = COOKIE.find(';', start)
        if end == -1:
            return COOKIE[start:]
        return COOKIE[start:end]
    return ''

def extract_uuid():
    """从__tea_cookie_tokens_2608中提取web_id"""
    tea_token = extract_from_cookie('__tea_cookie_tokens_2608')
    if tea_token:
        try:
            decoded = urllib.parse.unquote(tea_token)
            tea_data = json.loads(decoded)
            return tea_data.get('web_id', '7599900289718863423')
        except:
            pass
    return '7599900289718863423'

UUID = extract_uuid()
CSRF_TOKEN = extract_from_cookie('passport_csrf_token')
SESSION_ID = extract_from_cookie('sessionid')

print(f"UUID: {UUID}")
print(f"CSRF Token: {CSRF_TOKEN[:10] if CSRF_TOKEN else 'None'}...")

# ==================== 从浏览器获取的最新参数 ====================
# 签到参数（从之前的请求中获取）
CHECKIN_MS_TOKEN = "Jf-QXRRpn2zPi8juqA06vFa3wG46uN94TZUObbtMVTcwHtk7iY-hbM96MYKGe3rfw3rIntxXopovX-qZPjBs8LVmjPxv508aoQNCtOZY47AQeau4kYfG378_JIkxKQQE"
CHECKIN_A_BOGUS = "QXMm6Og2Msm1Y7VU%2F7kz9bmE1F60YWRQgZEPXDBEWzw-"

# 抽奖参数（从你刚提供的请求中获取）
LOTTERY_MS_TOKEN = "Q0R5r3WP2jlqQ7hXZoZSKzEqqXuLlSrwi4c9WEUOcotFG6HVGyitrf6MU8Phb2q63tP1AHbugVA5vsSMkmJm84T0L8lp_uneYJdq4zulUh6seAvSYYaQpRXUJMGp6IP9"
LOTTERY_A_BOGUS = "djBmkOg2Msm1t7VUMhkz9cfE1Og0YW4agZEPXDIyDtLT"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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

def get_china_time():
    china_tz = timezone(timedelta(hours=8))
    return datetime.now(china_tz)

def format_china_time():
    return get_china_time().strftime('%Y-%m-%d %H:%M:%S')

def get_headers():
    """获取完整的请求头"""
    return {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Content-Type': 'application/json',
        'Cookie': COOKIE,
        'Origin': 'https://juejin.cn',
        'Referer': 'https://juejin.cn/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': random.choice(USER_AGENTS),
        'x-secsdk-csrf-token': CSRF_TOKEN,
        'Priority': 'u=1, i',
    }

def get_checkin_url():
    """构建签到URL"""
    return (f"{CHECK_IN_URL}?aid=2608"
            f"&uuid={UUID}"
            f"&spider=0"
            f"&msToken={CHECKIN_MS_TOKEN}"
            f"&a_bogus={CHECKIN_A_BOGUS}")

def get_lottery_url():
    """构建抽奖URL - 使用抽奖专用的参数"""
    return (f"{LOTTERY_DRAW_URL}?aid=2608"
            f"&uuid={UUID}"
            f"&spider=0"
            f"&msToken={LOTTERY_MS_TOKEN}"
            f"&a_bogus={LOTTERY_A_BOGUS}")

def make_request(url, method='POST', data=None):
    """发送请求"""
    headers = get_headers()
    
    print(f"\n请求URL: {url}")
    print(f"请求方法: {method}")
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, verify=False, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=data or {}, verify=False, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200 and response.text:
            try:
                result = response.json()
                print(f"响应内容: {json.dumps(result, ensure_ascii=False)[:200]}")
                return result
            except:
                print(f"响应内容: '{response.text[:200]}'")
                return None
        else:
            print(f"响应为空或状态码错误")
            return None
            
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def get_today_status():
    """获取今天是否已签到"""
    result = make_request(GET_STATUS_URL, 'GET')
    if result and result.get('err_no') == 0:
        return result.get('data', False)
    return False

def check_in():
    """执行签到"""
    url = get_checkin_url()
    result = make_request(url, 'POST', {})
    
    if result and result.get('err_no') == 0:
        data = result.get('data', {})
        incr_point = data.get('incr_point', 0)
        total_point = data.get('total_point', 0)
        return True, f"获得{incr_point}矿石，当前总{total_point}矿石"
    else:
        error_msg = result.get('err_msg', '未知错误') if result else '请求失败'
        return False, error_msg

def lottery_draw():
    """执行免费抽奖 - 使用抽奖专用参数"""
    url = get_lottery_url()
    result = make_request(url, 'POST', {})
    
    if result and result.get('err_no') == 0:
        lottery_data = result.get('data', {})
        lottery_name = lottery_data.get('lottery_name', '未知奖品')
        print(f"🎉 抽奖成功！获得: {lottery_name}")
        return lottery_name
    else:
        error_msg = result.get('err_msg', '抽奖失败') if result else '请求失败'
        print(f"抽奖结果: {error_msg}")
        if '今天已经抽过奖' in error_msg:
            return "今天已经抽过奖"
        return f"抽奖失败: {error_msg}"

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

def create_email_html(sign_status, sign_detail, lottery_result):
    """创建邮件HTML"""
    current_time = format_china_time()
    
    if "成功" in sign_status or "已签到" in sign_status:
        sign_icon = "✅"
        sign_color = "#52c41a"
    else:
        sign_icon = "❌"
        sign_color = "#ff4d4f"
    
    if "已经抽过" in lottery_result:
        lottery_icon = "⏰"
        lottery_color = "#faad14"
    elif "失败" in lottery_result:
        lottery_icon = "❌"
        lottery_color = "#ff4d4f"
    else:
        lottery_icon = "🎁"
        lottery_color = "#52c41a"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Microsoft YaHei', sans-serif;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #1E80FF, #0066FF);
                color: white;
                padding: 24px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 22px;
            }}
            .content {{
                padding: 24px;
            }}
            .card {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                border-left: 4px solid #1E80FF;
            }}
            .label {{
                color: #6c757d;
                font-size: 13px;
                margin-bottom: 8px;
            }}
            .value {{
                font-size: 16px;
                color: #212529;
                font-weight: 500;
            }}
            .sign-status {{
                color: {sign_color};
                font-size: 18px;
                font-weight: 600;
            }}
            .lottery-status {{
                color: {lottery_color};
                font-size: 16px;
                font-weight: 500;
            }}
            .detail {{
                font-size: 14px;
                color: #6c757d;
                margin-top: 8px;
                padding-top: 8px;
                border-top: 1px dashed #dee2e6;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 16px;
                text-align: center;
                color: #6c757d;
                font-size: 12px;
                border-top: 1px solid #dee2e6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 掘金自动签到</h1>
            </div>
            <div class="content">
                <div class="card">
                    <div class="label">📅 执行时间</div>
                    <div class="value">{current_time}</div>
                </div>
                
                <div class="card">
                    <div class="label">✍️ 签到状态</div>
                    <div class="sign-status">{sign_icon} {sign_status}</div>
                    <div class="detail">{sign_detail}</div>
                </div>
                
                <div class="card">
                    <div class="label">🎲 抽奖结果</div>
                    <div class="lottery-status">{lottery_icon} {lottery_result}</div>
                </div>
            </div>
            <div class="footer">
                <p>🤖 自动签到系统 | 掘金社区</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    """主函数"""
    print(f"[{format_china_time()}] 开始执行掘金签到")
    
    if not check_config():
        return
    
    # 随机延迟
    delay = random.randint(1, 30)
    print(f"随机延迟 {delay} 秒")
    time.sleep(delay)
    
    # 获取状态
    is_signed = get_today_status()
    print(f"今日签到状态: {'已签到' if is_signed else '未签到'}")
    
    # 无论签到状态如何，都执行抽奖
    print("\n开始执行抽奖...")
    lottery_result = lottery_draw()
    
    if is_signed:
        sign_status = "已签到"
        sign_detail = "今天已经签到过了"
    else:
        print("\n开始执行签到...")
        sign_success, sign_detail = check_in()
        sign_status = "签到成功" if sign_success else "签到失败"
        
        # 如果签到成功，再抽一次奖
        if sign_success:
            print("\n签到成功，再次抽奖...")
            time.sleep(random.uniform(1, 2))
            lottery_result = lottery_draw()
    
    # 发送邮件
    html = create_email_html(sign_status, sign_detail, lottery_result)
    send_email("掘金签到通知", html, True)

if __name__ == "__main__":
    main()
