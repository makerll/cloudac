#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金社区自动签到脚本
"""
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

# ==================== 配置区域 ====================
# Cookie配置（从GitHub Action Secrets中获取）
COOKIE = ""  # 从cookie_config.py导入，用于GitHub Action

# 邮件配置（从GitHub Action Secrets中获取）
EMAIL_FROM = ""  # 从cookie_config.py导入，用于GitHub Action
EMAIL_PASSWORD = ""  # 从cookie_config.py导入，用于GitHub Action

# 尝试从外部配置文件导入Cookie和邮件配置（用于GitHub Action）
try:
    from cookie_config import COOKIE, EMAIL_FROM, EMAIL_PASSWORD
except ImportError:
    pass

# 邮件配置
EMAIL_TO = "maker196@163.com"
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465

# API配置
BASE_URL = "https://api.juejin.cn/growth_api/v1/"
CHECK_IN_URL = BASE_URL + "check_in"
GET_STATUS_URL = BASE_URL + "get_today_status"
LOTTERY_DRAW_URL = BASE_URL + "lottery/draw"
JUEJIN_HOME_URL = "https://juejin.cn/"

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
# 获取中国时区时间
def get_china_time():
    """
    获取中国时区（UTC+8）的当前时间
    """
    # 创建UTC+8时区
    china_tz = timezone(timedelta(hours=8))
    return datetime.now(china_tz)

# 格式化中国时区时间
def format_china_time():
    """
    格式化中国时区时间为字符串
    """
    return get_china_time().strftime('%Y-%m-%d %H:%M:%S')

# ==================== 配置区域结束 ====================

def visit_juejin_home():
    """
    访问掘金首页，模拟真实用户行为
    """
    try:
        # 检查Cookie是否为空
        if not COOKIE:
            print("错误：Cookie为空，请检查配置")
            return False
        
        headers = get_random_headers()
        time.sleep(random.uniform(0.5, 2))
        response = requests.get(JUEJIN_HOME_URL, headers=headers, verify=False, timeout=10)
        
        # 打印响应状态（用于调试）
        print(f"访问掘金首页状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("成功访问掘金首页")
            return True
        else:
            print(f"访问掘金首页失败: {response.status_code}")
    except Exception as e:
        print(f"访问掘金首页异常: {str(e)}")
    return False

def get_today_status():
    """
    获取今天是否已签到
    """
    try:
        # 检查Cookie是否为空
        if not COOKIE:
            print("错误：Cookie为空，请检查配置")
            return False
        
        # 使用随机请求头
        headers = get_random_headers()
        # 添加随机延迟
        time.sleep(random.uniform(0.5, 2))
        response = requests.get(GET_STATUS_URL, headers=headers, verify=False, timeout=10)
        
        # 打印响应状态和内容（用于调试）
        print(f"获取签到状态请求状态码: {response.status_code}")
        print(f"获取签到状态响应内容: {response.text[:200]}...")  # 只打印前200个字符
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('err_no') == 0:
                    return data.get('data', False)
                else:
                    error_msg = data.get('err_msg', '未知错误')
                    print(f"获取签到状态失败: {error_msg}")
                    if 'login' in error_msg.lower():
                        print("提示：请检查Cookie是否有效，可能已过期或格式错误")
            except ValueError as e:
                print(f"获取签到状态响应解析失败: {str(e)}")
                print("提示：可能是网络问题或API变更，请稍后重试")
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
        # 检查Cookie是否为空
        if not COOKIE:
            print("错误：Cookie为空，请检查配置")
            return False
        
        # 使用随机请求头
        headers = get_random_headers()
        # 添加随机延迟
        time.sleep(random.uniform(0.5, 2))
        response = requests.post(CHECK_IN_URL, headers=headers, verify=False, timeout=10)
        
        # 打印响应状态、头部和内容（用于调试）
        print(f"签到请求状态码: {response.status_code}")
        print(f"响应Content-Length: {response.headers.get('Content-Length', '未知')}")
        print(f"响应Content-Type: {response.headers.get('Content-Type', '未知')}")
        print(f"响应完整内容: '{response.text}'")  # 打印完整响应内容
        
        if response.status_code == 200:
            # 检查响应内容是否为空
            if not response.text:
                print("错误：响应内容为空")
                return False
            
            try:
                data = response.json()
                if data.get('err_no') == 0:
                    print(f"签到成功！获得矿石: {data.get('data', {}).get('incr_point', 0)}")
                    print(f"当前矿石: {data.get('data', {}).get('total_point', 0)}")
                    return True
                else:
                    error_msg = data.get('err_msg', '未知错误')
                    print(f"签到失败: {error_msg}")
                    if 'login' in error_msg.lower():
                        print("提示：请检查Cookie是否有效，可能已过期或格式错误")
            except ValueError as e:
                print(f"签到响应解析失败: {str(e)}")
                print("提示：可能是网络问题或API变更，请稍后重试")
        else:
            print(f"签到请求失败: {response.status_code}")
    except Exception as e:
        print(f"签到异常: {str(e)}")
    return False

def lottery_draw():
    """
    执行免费抽奖操作
    """
    try:
        # 检查Cookie是否为空
        if not COOKIE:
            print("错误：Cookie为空，请检查配置")
            return "抽奖失败"
        
        headers = get_random_headers()
        time.sleep(random.uniform(0.5, 2))
        response = requests.post(LOTTERY_DRAW_URL, headers=headers, verify=False, timeout=10)
        
        # 打印响应状态、头部和内容（用于调试）
        print(f"抽奖请求状态码: {response.status_code}")
        print(f"响应Content-Length: {response.headers.get('Content-Length', '未知')}")
        print(f"响应Content-Type: {response.headers.get('Content-Type', '未知')}")
        print(f"响应完整内容: '{response.text}'")  # 打印完整响应内容
        
        if response.status_code == 200:
            # 检查响应内容是否为空
            if not response.text:
                print("错误：响应内容为空")
                return "抽奖失败"
            
            try:
                data = response.json()
                if data.get('err_no') == 0:
                    lottery_data = data.get('data', {})
                    lottery_name = lottery_data.get('lottery_name', '未知奖品')
                    print(f"抽奖成功！获得: {lottery_name}")
                    return lottery_name
                else:
                    error_msg = data.get('err_msg', '未知错误')
                    print(f"抽奖失败: {error_msg}")
                    if '今天已经抽过奖' in error_msg or 'already' in error_msg.lower():
                        print("提示：今天已经抽过奖了，无需重复抽奖")
                        return "今天已经抽过奖"
            except ValueError as e:
                print(f"抽奖响应解析失败: {str(e)}")
                print("提示：可能今天已经抽过奖了")
                return "今天已经抽过奖"
        else:
            print(f"抽奖请求失败: {response.status_code}")
    except Exception as e:
        print(f"抽奖异常: {str(e)}")
        print("提示：可能今天已经抽过奖了")
    return "抽奖失败"

def create_email_html(sign_status, lottery_result):
    """
    创建HTML格式的邮件内容
    """
    current_time = format_china_time()
    
    # 根据签到状态设置颜色
    if "成功" in sign_status:
        sign_color = "#52c41a"
        sign_icon = "✅"
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
                border-left: 4px solid #667eea;
            }}
            .info-item:last-child {{
                margin-bottom: 0;
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
            .success {{
                color: {sign_color};
            }}
            .lottery {{
                color: {lottery_color};
            }}
            .footer {{
                background-color: #f9f9f9;
                padding: 15px;
                text-align: center;
                color: #999;
                font-size: 12px;
            }}
            .emoji {{
                font-size: 20px;
                margin-right: 8px;
            }}
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
                        <span class="success">{sign_status}</span>
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">🎲 抽奖结果</div>
                    <div class="info-value lottery">
                        <span class="emoji">{lottery_icon}</span>
                        <span class="lottery">{lottery_result}</span>
                    </div>
                </div>
            </div>
            <div class="footer">
                <p>🤖 自动签到系统 | 掘金社区</p>
                <p>此邮件由系统自动发送，请勿回复</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(subject, content, is_html=False):
    """
    发送邮件通知
    """
    try:
        if not EMAIL_FROM:
            print("邮件配置不完整：未设置发件邮箱，跳过邮件发送")
            return False
        if not EMAIL_PASSWORD:
            print("邮件配置不完整：未设置邮箱密码/授权码，跳过邮件发送")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        if is_html:
            msg.attach(MIMEText(content, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print(f"邮件发送成功: {EMAIL_TO}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        print("提示：邮件发送失败不会影响签到和抽奖功能")
        return False

def main():
    """
    主函数
    """
    print(f"[{format_china_time()}] 开始执行掘金签到")
    
    # 添加随机延迟（1-300秒），模拟真实用户行为
    random_delay = random.randint(1, 300)
    print(f"[{format_china_time()}] 随机延迟 {random_delay} 秒后执行签到")
    time.sleep(random_delay)
    
    # 访问掘金首页
    print("开始访问掘金首页...")
    visit_juejin_home()
    
    # 检查今天是否已签到
    is_signed = get_today_status()
    if is_signed:
        print("今天已经签到过了，无需重复签到")
        lottery_result = lottery_draw()
        html_content = create_email_html("已签到", lottery_result)
        send_email("掘金签到通知", html_content, is_html=True)
        return
    
    # 执行签到
    print("开始执行签到...")
    success = check_in()
    if success:
        print("签到完成！")
        # 执行抽奖
        print("开始执行免费抽奖...")
        lottery_result = lottery_draw()
        
        # 发送邮件通知
        html_content = create_email_html("签到成功", lottery_result)
        send_email("掘金签到通知", html_content, is_html=True)
    else:
        print("签到失败，请检查配置")
        html_content = create_email_html("签到失败", "请检查Cookie配置")
        send_email("掘金签到通知", html_content, is_html=True)

if __name__ == "__main__":
    main()
