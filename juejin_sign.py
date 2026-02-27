#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金社区自动签到脚本 - 最终修复版
"""
import os
import requests
import time
import random
import smtplib
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL验证警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ==================== 从环境变量读取配置 ====================
COOKIE = os.environ.get('JUEJIN_COOKIE', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_TO = os.environ.get('EMAIL_TO', '')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.163.com')

# 处理SMTP_PORT
SMTP_PORT_STR = os.environ.get('SMTP_PORT', '465')
try:
    SMTP_PORT = int(SMTP_PORT_STR) if SMTP_PORT_STR else 465
except ValueError:
    print(f"警告: SMTP_PORT 值 '{SMTP_PORT_STR}' 无效，使用默认值 465")
    SMTP_PORT = 465

# 如果EMAIL_TO为空，默认使用EMAIL_FROM
if not EMAIL_TO:
    EMAIL_TO = EMAIL_FROM

# API配置
BASE_URL = "https://api.juejin.cn/growth_api/v1/"
CHECK_IN_URL = BASE_URL + "check_in"
GET_STATUS_URL = BASE_URL + "get_today_status"
LOTTERY_DRAW_URL = BASE_URL + "lottery/draw"
JUEJIN_HOME_URL = "https://juejin.cn/"

# 从Cookie中提取CSRF token
def extract_csrf_token():
    """从Cookie中提取CSRF token"""
    if 'passport_csrf_token=' in COOKIE:
        start = COOKIE.find('passport_csrf_token=') + len('passport_csrf_token=')
        end = COOKIE.find(';', start)
        if end == -1:
            return COOKIE[start:]
        return COOKIE[start:end]
    return ''

CSRF_TOKEN = extract_csrf_token()
print(f"提取的CSRF Token: {CSRF_TOKEN[:10]}...")  # 只打印前10位

# 随机User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
]

def check_config():
    """检查必要的配置是否都存在"""
    missing_configs = []
    
    if not COOKIE:
        missing_configs.append('JUEJIN_COOKIE')
    if not EMAIL_FROM:
        missing_configs.append('EMAIL_FROM')
    if not EMAIL_PASSWORD:
        missing_configs.append('EMAIL_PASSWORD')
    
    if missing_configs:
        print("错误：以下配置缺失，请在GitHub Secrets中设置：")
        for config in missing_configs:
            print(f"  - {config}")
        return False
    
    print(f"邮件配置: FROM={EMAIL_FROM}, TO={EMAIL_TO}, SERVER={SMTP_SERVER}, PORT={SMTP_PORT}")
    print(f"Cookie长度: {len(COOKIE)}")
    return True

# 获取随机请求头 - 添加了所有必要的头信息
def get_random_headers():
    """
    获取随机请求头 - 包含CSRF token
    """
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
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
        'Sec-Fetch-Site': 'same-site',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    # 添加CSRF token（如果存在）
    if CSRF_TOKEN:
        headers['x-secsdk-csrf-token'] = CSRF_TOKEN
        headers['X-CSRF-Token'] = CSRF_TOKEN  # 有些API用这个
    
    return headers

# 获取中国时区时间
def get_china_time():
    china_tz = timezone(timedelta(hours=8))
    return datetime.now(china_tz)

def format_china_time():
    return get_china_time().strftime('%Y-%m-%d %H:%M:%S')

def visit_juejin_home():
    """访问掘金首页"""
    try:
        headers = get_random_headers()
        time.sleep(random.uniform(0.5, 2))
        response = requests.get(JUEJIN_HOME_URL, headers=headers, verify=False, timeout=10)
        print(f"访问掘金首页状态码: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"访问掘金首页异常: {str(e)}")
        return False

def get_today_status():
    """获取今天是否已签到"""
    try:
        headers = get_random_headers()
        time.sleep(random.uniform(0.5, 2))
        response = requests.get(GET_STATUS_URL, headers=headers, verify=False, timeout=10)
        
        print(f"获取签到状态请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('err_no') == 0:
                return data.get('data', False)
            else:
                print(f"获取签到状态失败: {data.get('err_msg')}")
        return False
    except Exception as e:
        print(f"获取签到状态异常: {str(e)}")
        return False

def check_in():
    """执行签到操作 - 使用完整的请求头"""
    try:
        headers = get_random_headers()
        time.sleep(random.uniform(0.5, 2))
        
        # 打印请求头（调试用，隐藏敏感信息）
        debug_headers = {k: v[:20] + '...' if k in ['Cookie', 'x-secsdk-csrf-token'] else v 
                        for k, v in headers.items()}
        print(f"请求头: {debug_headers}")
        
        # 发送POST请求，带空JSON body
        response = requests.post(
            CHECK_IN_URL, 
            headers=headers, 
            json={},  # 空JSON对象
            verify=False, 
            timeout=10
        )
        
        print(f"签到请求状态码: {response.status_code}")
        print(f"响应Headers: {dict(response.headers)}")
        print(f"响应内容: '{response.text}'")
        
        if response.status_code == 200 and response.text:
            try:
                data = response.json()
                if data.get('err_no') == 0:
                    incr_point = data.get('data', {}).get('incr_point', 0)
                    total_point = data.get('data', {}).get('total_point', 0)
                    print(f"✅ 签到成功！获得矿石: {incr_point}, 当前矿石: {total_point}")
                    return True
                else:
                    print(f"❌ 签到失败: {data.get('err_msg')}")
                    if '请先登录' in data.get('err_msg', ''):
                        print("提示：Cookie可能已过期")
            except ValueError as e:
                print(f"响应解析失败: {str(e)}")
        else:
            print(f"❌ 签到请求失败: 状态码={response.status_code}, 响应为空")
            
            # 如果失败，尝试使用不同的请求方式
            print("尝试备用签到方式...")
            alt_response = requests.post(
                CHECK_IN_URL,
                headers=headers,
                data='{}',  # 字符串格式的JSON
                verify=False,
                timeout=10
            )
            print(f"备用方式响应: '{alt_response.text}'")
        
        return False
    except Exception as e:
        print(f"签到异常: {str(e)}")
        return False

def lottery_draw():
    """执行免费抽奖"""
    try:
        headers = get_random_headers()
        time.sleep(random.uniform(0.5, 2))
        response = requests.post(LOTTERY_DRAW_URL, headers=headers, json={}, verify=False, timeout=10)
        
        print(f"抽奖请求状态码: {response.status_code}")
        
        if response.status_code == 200 and response.text:
            data = response.json()
            if data.get('err_no') == 0:
                lottery_name = data.get('data', {}).get('lottery_name', '未知奖品')
                print(f"🎉 抽奖成功！获得: {lottery_name}")
                return lottery_name
            else:
                error_msg = data.get('err_msg', '未知错误')
                print(f"抽奖失败: {error_msg}")
                if '今天已经抽过奖' in error_msg:
                    return "今天已经抽过奖"
        return "抽奖失败"
    except Exception as e:
        print(f"抽奖异常: {str(e)}")
        return "抽奖失败"

def create_email_html(sign_status, lottery_result):
    """创建HTML邮件内容"""
    current_time = format_china_time()
    
    # 根据签到状态设置颜色和图标
    if "成功" in sign_status:
        sign_color = "#52c41a"
        sign_icon = "✅"
    elif "已签到" in sign_status:
        sign_color = "#faad14"
        sign_icon = "⏰"
    else:
        sign_color = "#ff4d4f"
        sign_icon = "❌"
    
    # 根据抽奖结果设置颜色
    if "已经抽过奖" in lottery_result:
        lottery_color = "#faad14"
        lottery_icon = "⏰"
    elif "失败" in lottery_result:
        lottery_color = "#ff4d4f"
        lottery_icon = "❌"
    else:
        lottery_color = "#52c41a"
        lottery_icon = "🎁"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #1E80FF 0%, #0060FF 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 20px;
                font-weight: bold;
            }}
            .content {{
                padding: 20px;
            }}
            .info-item {{
                margin-bottom: 15px;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 6px;
                border-left: 4px solid #1E80FF;
            }}
            .info-label {{
                font-size: 12px;
                color: #999;
                margin-bottom: 6px;
            }}
            .info-value {{
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }}
            .success {{ color: {sign_color}; }}
            .lottery {{ color: {lottery_color}; }}
            .footer {{
                background-color: #f9f9f9;
                padding: 15px;
                text-align: center;
                color: #999;
                font-size: 12px;
            }}
            .emoji {{ font-size: 20px; margin-right: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 掘金签到通知</h1>
            </div>
            <div class="content">
                <div class="info-item">
                    <div class="info-label">📅 执行时间</div>
                    <div class="info-value">{current_time}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">✍️ 签到状态</div>
                    <div class="info-value success">
                        <span class="emoji">{sign_icon}</span>
                        <span>{sign_status}</span>
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">🎲 抽奖结果</div>
                    <div class="info-value lottery">
                        <span class="emoji">{lottery_icon}</span>
                        <span>{lottery_result}</span>
                    </div>
                </div>
            </div>
            <div class="footer">
                <p>🤖 自动签到系统 | 掘金社区</p>
                <p>此邮件由系统自动发送</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(subject, content, is_html=False):
    """发送邮件"""
    try:
        if not all([EMAIL_FROM, EMAIL_PASSWORD, SMTP_SERVER]):
            print("邮件配置不完整，跳过邮件发送")
            return False
        
        print(f"正在连接SMTP服务器: {SMTP_SERVER}:{SMTP_PORT}")
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        if is_html:
            msg.attach(MIMEText(content, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print(f"✅ 邮件发送成功: {EMAIL_TO}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        return False

def main():
    """主函数"""
    print(f"[{format_china_time()}] 开始执行掘金签到")
    
    # 检查配置
    if not check_config():
        return
    
    # 添加随机延迟
    random_delay = random.randint(1, 60)  # 减少延迟时间便于测试
    print(f"[{format_china_time()}] 随机延迟 {random_delay} 秒")
    time.sleep(random_delay)
    
    # 访问掘金首页
    print("开始访问掘金首页...")
    visit_juejin_home()
    
    # 检查今天是否已签到
    is_signed = get_today_status()
    if is_signed:
        print("今天已经签到过了")
        lottery_result = lottery_draw()
        html_content = create_email_html("已签到", lottery_result)
        send_email("掘金签到通知", html_content, is_html=True)
        return
    
    # 执行签到
    print("开始执行签到...")
    success = check_in()
    
    if success:
        print("签到完成！")
        lottery_result = lottery_draw()
        html_content = create_email_html("签到成功", lottery_result)
    else:
        print("签到失败")
        html_content = create_email_html("签到失败", "请检查Cookie配置")
    
    send_email("掘金签到通知", html_content, is_html=True)

if __name__ == "__main__":
    main()
