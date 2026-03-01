#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金社区自动签到脚本 - Selenium 完整版
每天先点击签到，再去抽免费抽奖1次
"""
import os
import time
import random
import smtplib
import ssl
import re
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

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

# 掘金URL
JUEJIN_URL = "https://juejin.cn/"
USER_PAGE_URL = "https://juejin.cn/user/center/signin"

def check_config():
    """检查必要的配置"""
    missing = []
    if not COOKIE:
        missing.append('JUEJIN_COOKIE')
    if not EMAIL_FROM:
        missing.append('EMAIL_FROM')
    if not EMAIL_PASSWORD:
        missing.append('EMAIL_PASSWORD')
    if missing:
        print("错误：以下配置缺失：", missing)
        return False
    return True

def get_china_time():
    """获取中国时间"""
    china_tz = timezone(timedelta(hours=8))
    return datetime.now(china_tz)

def format_china_time():
    """格式化中国时间"""
    return get_china_time().strftime('%Y-%m-%d %H:%M:%S')

def setup_driver():
    """配置Chrome浏览器选项"""
    chrome_options = Options()
    
    # 无头模式
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 禁用自动化控制标志
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 使用 webdriver-manager 自动管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 隐藏 webdriver 属性
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def parse_cookie_string(cookie_str):
    """将Cookie字符串解析为Selenium需要的格式"""
    cookies = []
    for item in cookie_str.split('; '):
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({
                'name': name,
                'value': value,
                'domain': '.juejin.cn'
            })
    return cookies

def add_cookies_to_driver(driver, cookie_str):
    """向浏览器添加Cookie"""
    driver.get(JUEJIN_URL)
    time.sleep(2)
    
    cookies = parse_cookie_string(cookie_str)
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"添加cookie {cookie['name']} 失败: {e}")
    
    print(f"已添加 {len(cookies)} 个cookie")
    driver.refresh()
    time.sleep(3)

def get_user_stats(driver):
    """获取用户统计信息：连续签到天数、累计签到天数、矿石总数"""
    stats = {'连续签到': '0', '累计签到': '0', '矿石总数': '0', '今日获得': '0'}

    try:
        # 获取页面所有可见文本
        page_text = driver.find_element(By.TAG_NAME, 'body').text

        # 连续签到
        match = re.search(r'(\d+)\s*连续签到天数', page_text)
        if match:
            stats['连续签到'] = match.group(1)

        # 累计签到
        match = re.search(r'(\d+)\s*累计签到天数', page_text)
        if match:
            stats['累计签到'] = match.group(1)

        # 矿石总数
        match = re.search(r'(\d+)\s*当前矿石数', page_text)
        if match:
            stats['矿石总数'] = match.group(1)

        # 今日获得（稍后从签到结果更新）
        
    except Exception as e:
        print(f"获取用户统计信息时出错: {e}")

    return stats

def check_sign_status(driver):
    """检查今日是否已签到，并返回签到按钮"""
    try:
        # 优先检查是否已显示“今日已签到”状态标签
        signed_elements = driver.find_elements(By.XPATH, '//*[contains(text(), "今日已签到")]')
        for element in signed_elements:
            if element.is_displayed():
                print("检测到'今日已签到'状态标签")
                return True, None

        # 查找可点击的签到按钮
        button_selectors = [
            '//button[contains(text(), "签到")]',
            '//button[contains(text(), "立即签到")]',
            '//div[@role="button" and contains(text(), "签到")]',
            '.signin-btn',
            '.check-in-btn',
        ]

        for selector in button_selectors:
            try:
                if selector.startswith('//'):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)

                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        tag_name = element.tag_name.lower()
                        if tag_name in ['button', 'a'] or element.get_attribute('role') == 'button':
                            print(f"找到可点击的签到按钮: {element.text}")
                            return False, element
            except:
                continue

        print("未找到明确的签到按钮，假设已签到")
        return True, None

    except Exception as e:
        print(f"检查签到状态时出错: {e}")
        return False, None

def perform_sign(driver, sign_button):
    """执行签到操作"""
    try:
        if not sign_button:
            return False, "未找到签到按钮"

        # 滚动到按钮位置
        driver.execute_script("arguments[0].scrollIntoView(true);", sign_button)
        time.sleep(1)

        # 点击签到
        try:
            sign_button.click()
        except:
            driver.execute_script("arguments[0].click();", sign_button)

        print("已点击签到按钮")
        time.sleep(3)

        # 获取签到奖励
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        match = re.search(r'获得[^\d]*(\d+)[^\d]*矿石', page_text)
        if match:
            reward = f"获得 {match.group(1)} 矿石"
        else:
            reward = "签到成功"

        return True, reward

    except Exception as e:
        print(f"执行签到异常: {e}")
        return False, f"签到异常: {str(e)}"

def switch_to_lottery_tab(driver):
    """切换到幸运抽奖菜单"""
    try:
        # 查找并点击"幸运抽奖"标签
        lottery_tab_selectors = [
            '//*[contains(text(), "幸运抽奖")]',
            '//div[@role="tab" and contains(text(), "幸运抽奖")]',
            '.lottery-tab',
            '//*[contains(@class, "tab") and contains(text(), "抽奖")]'
        ]
        
        for selector in lottery_tab_selectors:
            try:
                if selector.startswith('//'):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed():
                        print(f"找到幸运抽奖标签: {element.text}")
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1)
                        
                        try:
                            element.click()
                        except:
                            driver.execute_script("arguments[0].click();", element)
                        
                        print("已切换到幸运抽奖页面")
                        time.sleep(3)  # 等待抽奖页面加载
                        return True
            except:
                continue
        
        print("未找到幸运抽奖标签")
        return False
        
    except Exception as e:
        print(f"切换抽奖标签异常: {e}")
        return False

def check_lottery_available(driver):
    """检查是否有免费抽奖机会，并返回抽奖按钮"""
    try:
        # 先切换到抽奖页面
        if not switch_to_lottery_tab(driver):
            return False, "无法切换到抽奖页面"
        
        # 获取页面文本检查抽奖次数
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        
        # 检查免费抽奖次数
        if '免费抽奖次数：0次' in page_text:
            print("免费抽奖次数已用完")
            return False, "今天已经抽过奖"
        
        if '免费抽奖次数：1次' in page_text:
            print("检测到免费抽奖次数：1次")
        
        # 查找抽奖按钮
        lottery_selectors = [
            '//*[contains(text(), "去抽奖")]',
            '//*[contains(text(), "免费抽奖")]',
            '//button[contains(text(), "抽奖")]',
            '.lottery-btn',
            '.draw-btn',
            '//div[contains(@class, "draw") and contains(@class, "btn")]',
        ]
        
        for selector in lottery_selectors:
            try:
                if selector.startswith('//'):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"找到抽奖按钮: {element.text}")
                        return True, element
            except:
                continue
        
        # 检查是否已显示抽奖结果
        if '恭喜' in page_text and ('抽中' in page_text or '中奖' in page_text):
            print("检测到已抽过奖的记录")
            return False, "今天已经抽过奖"
        
        return False, "未找到抽奖按钮"
        
    except Exception as e:
        print(f"检查抽奖状态异常: {e}")
        return False, "检查失败"

def perform_lottery(driver, lottery_element):
    """执行抽奖并获取具体奖品信息（包含矿石数量）"""
    try:
        # 滚动到按钮位置
        driver.execute_script("arguments[0].scrollIntoView(true);", lottery_element)
        time.sleep(1)

        # 点击抽奖
        try:
            lottery_element.click()
        except:
            driver.execute_script("arguments[0].click();", lottery_element)

        print("已点击抽奖按钮")
        time.sleep(3)

        # 获取抽奖结果
        page_text = driver.find_element(By.TAG_NAME, 'body').text

        # === 优先匹配带数字的矿石 ===
        # 匹配 "获得: 66矿石" 或 "获得：66矿石" 或 "获得66矿石"
        ore_match = re.search(r'获得[：:]\s*(\d+)\s*矿石', page_text)
        if ore_match:
            ore_count = ore_match.group(1)
            print(f"🎉 抽中获得 {ore_count} 矿石")
            return f"获得 {ore_count} 矿石"

        # 匹配 "恭喜XXX抽中66矿石"
        ore_match2 = re.search(r'抽中[“”]?(\d+)\s*矿石', page_text)
        if ore_match2:
            ore_count = ore_match2.group(1)
            return f"获得 {ore_count} 矿石"

        # 匹配 "随机矿石" 但可能包含数量
        if "随机矿石" in page_text:
            # 尝试找附近的数字
            nearby_text = page_text[max(0, page_text.find("随机矿石")-20):page_text.find("随机矿石")+20]
            num_match = re.search(r'(\d+)', nearby_text)
            if num_match:
                return f"获得 {num_match.group(1)} 矿石"
            return "获得随机矿石"

        # 匹配其他奖品格式
        prize_match = re.search(r'恭喜[^，,\n]+抽中[“”]?([^“”\n]+)[”"]?', page_text)
        if prize_match:
            prize = prize_match.group(1).strip()
            return f"获得: {prize}"

        prize_match = re.search(r'获得[：:]\s*([^\n，。,.]+)', page_text)
        if prize_match:
            prize = prize_match.group(1).strip()
            return f"获得: {prize}"

        # 常见奖品关键词
        common_prizes = ['盲盒', '小夜灯', '耳机', '兑换券', '唇膏']
        for prize in common_prizes:
            if prize in page_text:
                return f"获得: {prize}"

        if '谢谢参与' in page_text:
            return "谢谢参与"

        return "抽奖完成"

    except Exception as e:
        print(f"执行抽奖异常: {e}")
        return f"抽奖异常: {str(e)}"

def send_email(subject, content, is_html=False):
    """发送邮件通知"""
    try:
        if not all([EMAIL_FROM, EMAIL_PASSWORD, SMTP_SERVER]):
            print("邮件配置不完整，跳过邮件发送")
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

def create_email_html(sign_status, sign_detail, lottery_result, user_stats):
    """创建HTML邮件内容 - 清新优雅紧凑版"""
    current_time = format_china_time()

    # 签到状态
    if "成功" in sign_status:
        sign_badge = "✨ 签到成功"
        sign_color = "#10b981"  # 翠绿色
    elif "已签到" in sign_status:
        sign_badge = "📌 今日已签"
        sign_color = "#3b82f6"  # 清爽蓝色
    else:
        sign_badge = "⚠️ 签到异常"
        sign_color = "#ef4444"  # 红色

    # 抽奖结果
    if "获得" in lottery_result:
        lottery_icon = "🎁"
        lottery_badge = "恭喜中奖"
        lottery_color = "#8b5cf6"  # 紫色
    elif "谢谢参与" in lottery_result:
        lottery_icon = "🍀"
        lottery_badge = "谢谢参与"
        lottery_color = "#6b7280"  # 灰色
    elif "已经抽过" in lottery_result:
        lottery_icon = "⏰"
        lottery_badge = "今日已抽"
        lottery_color = "#f59e0b"  # 橙色
    else:
        lottery_icon = "❓"
        lottery_badge = "抽奖完成"
        lottery_color = "#6b7280"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 16px;
            }}
            .card {{
                max-width: 480px;
                width: 100%;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 32px;
                box-shadow: 0 20px 40px -12px rgba(0, 20, 40, 0.25);
                overflow: hidden;
                transition: transform 0.2s;
            }}
            .card:hover {{
                transform: translateY(-2px);
            }}
            
            /* 头部 */
            .header {{
                padding: 24px 24px 16px;
                background: linear-gradient(112deg, #ffffff 0%, #f9fafc 100%);
                border-bottom: 1px solid rgba(0, 0, 0, 0.03);
            }}
            .title-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
            }}
            .title {{
                font-size: 20px;
                font-weight: 600;
                background: linear-gradient(135deg, #1e293b, #0f172a);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.3px;
            }}
            .date-badge {{
                font-size: 13px;
                color: #64748b;
                background: #f1f5f9;
                padding: 4px 10px;
                border-radius: 40px;
                font-weight: 500;
            }}
            .sub-title {{
                font-size: 13px;
                color: #64748b;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .dot {{
                width: 4px;
                height: 4px;
                background: #cbd5e1;
                border-radius: 50%;
            }}
            
            /* 统计卡片网格 */
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
                padding: 20px 24px;
                background: #ffffff;
            }}
            .stat-item {{
                background: #f8fafc;
                border-radius: 20px;
                padding: 14px 12px;
                border: 1px solid #f1f5f9;
                transition: all 0.2s;
            }}
            .stat-item:hover {{
                border-color: #cbd5e1;
                background: #ffffff;
            }}
            .stat-label {{
                font-size: 12px;
                color: #64748b;
                margin-bottom: 6px;
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            .stat-value {{
                font-size: 22px;
                font-weight: 600;
                color: #0f172a;
                line-height: 1.2;
            }}
            .stat-unit {{
                font-size: 12px;
                font-weight: 400;
                color: #94a3b8;
                margin-left: 2px;
            }}
            
            /* 内容区域 */
            .content {{
                padding: 8px 24px 24px;
            }}
            
            /* 状态卡片 */
            .status-card {{
                background: #ffffff;
                border-radius: 24px;
                padding: 18px;
                margin-bottom: 12px;
                border: 1px solid #f1f5f9;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
            }}
            .status-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
            }}
            .status-title {{
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
                letter-spacing: 0.3px;
            }}
            .status-badge {{
                font-size: 12px;
                padding: 4px 10px;
                border-radius: 30px;
                background: #f1f5f9;
                color: #475569;
            }}
            .status-main {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .status-icon {{
                width: 40px;
                height: 40px;
                background: {sign_color}10;
                border-radius: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 22px;
            }}
            .status-info {{
                flex: 1;
            }}
            .status-line {{
                font-weight: 600;
                font-size: 16px;
                color: {sign_color};
                margin-bottom: 4px;
            }}
            .status-desc {{
                font-size: 13px;
                color: #64748b;
            }}
            
            /* 抽奖卡片 */
            .lottery-card {{
                background: linear-gradient(105deg, {lottery_color}05, #ffffff);
                border-radius: 24px;
                padding: 18px;
                border: 1px solid {lottery_color}20;
            }}
            .lottery-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 12px;
            }}
            .lottery-title {{
                font-size: 13px;
                font-weight: 500;
                color: #64748b;
            }}
            .lottery-badge {{
                font-size: 12px;
                padding: 4px 10px;
                border-radius: 30px;
                background: {lottery_color}10;
                color: {lottery_color};
                font-weight: 500;
            }}
            .lottery-content {{
                display: flex;
                align-items: center;
                gap: 14px;
            }}
            .lottery-icon {{
                width: 44px;
                height: 44px;
                background: {lottery_color}15;
                border-radius: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 26px;
            }}
            .lottery-info {{
                flex: 1;
            }}
            .lottery-result {{
                font-weight: 600;
                font-size: 18px;
                color: {lottery_color};
                margin-bottom: 2px;
            }}
            .lottery-note {{
                font-size: 12px;
                color: #94a3b8;
            }}
            
            /* 底部 */
            .footer {{
                padding: 16px 24px 20px;
                text-align: center;
                border-top: 1px solid #f1f5f9;
                background: #ffffff;
            }}
            .footer-text {{
                font-size: 12px;
                color: #94a3b8;
                line-height: 1.6;
            }}
            .footer-icon {{
                margin: 0 4px;
                color: #cbd5e1;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <!-- 头部 -->
            <div class="header">
                <div class="title-row">
                    <span class="title">⛏️ 掘金签到</span>
                    <span class="date-badge">{current_time}</span>
                </div>
                <div class="sub-title">
                    <span>每日自动签到</span>
                    <span class="dot"></span>
                    <span>免费抽奖1次</span>
                </div>
            </div>
            
            <!-- 统计卡片网格 - 紧凑设计 -->
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">📅 连续</div>
                    <div class="stat-value">{user_stats['连续签到']}<span class="stat-unit">天</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">📊 累计</div>
                    <div class="stat-value">{user_stats['累计签到']}<span class="stat-unit">天</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">💎 矿石</div>
                    <div class="stat-value">{user_stats['矿石总数']}<span class="stat-unit">个</span></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">✨ 今日</div>
                    <div class="stat-value">{user_stats['今日获得']}<span class="stat-unit">矿石</span></div>
                </div>
            </div>
            
            <!-- 内容区域 -->
            <div class="content">
                <!-- 签到状态卡片 -->
                <div class="status-card">
                    <div class="status-header">
                        <span class="status-title">✍️ 签到状态</span>
                        <span class="status-badge">{sign_badge}</span>
                    </div>
                    <div class="status-main">
                        <div class="status-icon" style="background: {sign_color}10;">{"✅" if "成功" in sign_status or "已签到" in sign_status else "⚠️"}</div>
                        <div class="status-info">
                            <div class="status-line">{sign_status}</div>
                            <div class="status-desc">{sign_detail}</div>
                        </div>
                    </div>
                </div>
                
                <!-- 抽奖结果卡片 - 突出显示 -->
                <div class="lottery-card">
                    <div class="lottery-header">
                        <span class="lottery-title">🎲 免费抽奖</span>
                        <span class="lottery-badge">{lottery_badge}</span>
                    </div>
                    <div class="lottery-content">
                        <div class="lottery-icon" style="background: {lottery_color}15;">{lottery_icon}</div>
                        <div class="lottery-info">
                            <div class="lottery-result">{lottery_result}</div>
                            <div class="lottery-note">今日免费机会已使用</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 底部 -->
            <div class="footer">
                <div class="footer-text">
                    <span class="footer-icon">⚡</span> 每日自动执行 · 结果实时推送 <span class="footer-icon">⚡</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    """主函数"""
    start_time = format_china_time()
    print(f"[{start_time}] 开始执行掘金签到 (Selenium版)")

    if not check_config():
        return

    driver = None
    sign_status = "失败"
    sign_detail = "未知错误"
    lottery_result = "未执行"
    user_stats = {'连续签到': '0', '累计签到': '0', '矿石总数': '0', '今日获得': '0'}

    try:
        # 随机延迟
        delay = random.randint(5, 20)
        print(f"随机延迟 {delay} 秒")
        time.sleep(delay)

        # 启动浏览器
        print("正在启动Chrome浏览器...")
        driver = setup_driver()

        # 添加Cookie
        print("正在添加Cookie...")
        add_cookies_to_driver(driver, COOKIE)

        # 进入签到页面
        print(f"正在访问签到页面: {USER_PAGE_URL}")
        driver.get(USER_PAGE_URL)
        time.sleep(5)

        # === 获取签到前的初始数据（用于对比） ===
        print("正在获取签到前用户统计信息...")
        initial_stats = get_user_stats(driver)
        print(f"签到前统计: {initial_stats}")

        # 检查签到状态
        is_signed, sign_button = check_sign_status(driver)
        print(f"今日签到状态: {'已签到' if is_signed else '未签到'}")

        if not is_signed and sign_button:
            # 情况1：未签到 → 先签到，再抽奖
            print("开始执行签到...")
            sign_success, sign_reward = perform_sign(driver, sign_button)

            if sign_success:
                # 更新今日获得矿石数
                if "获得" in sign_reward:
                    reward_numbers = re.findall(r'\d+', sign_reward)
                    if reward_numbers:
                        user_stats['今日获得'] = reward_numbers[0]
                        print(f"今日签到获得: {user_stats['今日获得']} 矿石")

                sign_status = "签到成功"
                sign_detail = sign_reward
                print(f"✅ {sign_status}: {sign_detail}")

                # 签到成功 → 去抽奖
                print("\n=== 签到完成，开始执行抽奖 ===")
                lottery_available, lottery_element = check_lottery_available(driver)

                if lottery_available and lottery_element:
                    print("发现免费抽奖机会，开始抽奖...")
                    lottery_result = perform_lottery(driver, lottery_element)
                    
                    # 如果是矿石，累加到今日获得
                    if "矿石" in lottery_result:
                        ore_match = re.search(r'(\d+)', lottery_result)
                        if ore_match:
                            lottery_ore = int(ore_match.group(1))
                            current_ore = int(user_stats['今日获得'] or 0)
                            user_stats['今日获得'] = str(current_ore + lottery_ore)
                            print(f"今日抽奖获得: {lottery_ore} 矿石，累计: {user_stats['今日获得']}")
                else:
                    lottery_result = lottery_element if isinstance(lottery_element, str) else "今天已经抽过奖"
                    print(f"抽奖状态: {lottery_result}")
            else:
                sign_status = "签到失败"
                sign_detail = sign_reward
                print(f"❌ {sign_status}")
                lottery_result = "签到失败，未抽奖"

        else:
            # 情况2：已签到 → 只抽奖（如果还没抽的话）
            sign_status = "已签到"
            sign_detail = "今日已完成签到"
            print(f"✅ {sign_status}")
            
            print("\n=== 今日已签到，检查抽奖机会 ===")
            lottery_available, lottery_element = check_lottery_available(driver)

            if lottery_available and lottery_element:
                print("发现免费抽奖机会，开始抽奖...")
                lottery_result = perform_lottery(driver, lottery_element)
                
                # 如果是矿石，累加到今日获得
                if "矿石" in lottery_result:
                    ore_match = re.search(r'(\d+)', lottery_result)
                    if ore_match:
                        lottery_ore = int(ore_match.group(1))
                        user_stats['今日获得'] = str(lottery_ore)
                        print(f"今日抽奖获得: {lottery_ore} 矿石")
            else:
                lottery_result = lottery_element if isinstance(lottery_element, str) else "今天已经抽过奖"
                print(f"抽奖状态: {lottery_result}")

        # === 在所有操作完成后，重新获取最新的统计数据 ===
        print("\n=== 操作完成，获取最新统计数据 ===")
        time.sleep(3)  # 等待页面更新
        
        # 重新获取最新数据
        final_stats = get_user_stats(driver)
        print(f"最终统计: {final_stats}")
        
        # 更新 user_stats 为最终数据
        user_stats['连续签到'] = final_stats['连续签到']
        user_stats['累计签到'] = final_stats['累计签到']
        user_stats['矿石总数'] = final_stats['矿石总数']
        # 今日获得保持不变（已经在过程中累加）

        print(f"\n最终结果 - 签到: {sign_status}, 抽奖: {lottery_result}")

    except Exception as e:
        error_msg = str(e)
        print(f"执行过程中出现异常: {error_msg}")
        sign_detail = f"异常: {error_msg[:100]}"
        if driver:
            try:
                driver.save_screenshot("error.png")
                print("已保存错误截图")
            except:
                pass

    finally:
        # 关闭浏览器
        if driver:
            driver.quit()
            print("浏览器已关闭")

        # 发送邮件
        html_content = create_email_html(sign_status, sign_detail, lottery_result, user_stats)
        send_email("掘金签到通知", html_content, is_html=True)

        end_time = format_china_time()
        print(f"[{end_time}] 执行完成")

if __name__ == "__main__":
    main()


