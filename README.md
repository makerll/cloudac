# ⛏️ Juejin Auto Sign

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-blue?logo=github-actions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.10-green?logo=python)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-Automation-brightgreen?logo=selenium)](https://www.selenium.dev/)

🇨🇳 [中文](#中文) | 🇺🇸 [English](#english)

---

## 中文

### 📖 项目简介

这是一个使用 **Selenium** 实现的掘金社区自动签到脚本，通过 GitHub Actions 每天自动运行。它可以：

- ✅ 自动签到领取矿石
- 🎁 签到后自动进行免费抽奖（1次/天）
- 📊 获取用户统计信息（连续签到天数、累计签到天数、矿石总数）
- 💎 精确记录今日获得矿石数量（签到+抽奖）
- 📧 发送精美邮件通知，包含详细统计和抽奖结果

### ✨ 主要特性

- **完全模拟浏览器**：使用 Selenium 无头模式，自动处理所有动态参数（msToken、a_bogus 等）
- **智能页面导航**：自动从签到页面切换到抽奖页面
- **精确数据提取**：通过正则表达式准确获取签到天数、矿石数量等信息
- **抽奖结果识别**：能识别具体奖品名称和矿石数量
- **邮件通知**：清新优雅的 HTML 邮件模板，包含四宫格统计卡片
- **多语言支持**：中英文双语 README 和代码注释

### 🛠️ 技术栈

- Python 3.10
- Selenium + ChromeDriver
- GitHub Actions
- WebDriver Manager
- SMTP (邮件发送)

### 📁 文件结构
.
├── .github/
│ └── workflows/
│ └── sign.yml # GitHub Actions 工作流配置
├── juejin_selenium.py # 主脚本
└── README.md # 项目说明

text

### 🚀 快速开始

#### 1. Fork 本仓库

点击右上角的 **Fork** 按钮，将仓库复制到你的 GitHub 账号下。

#### 2. 获取掘金 Cookie

1. 打开浏览器（Chrome/Edge），**无痕模式**访问 [https://juejin.cn/](https://juejin.cn/)
2. 登录你的掘金账号
3. 按 `F12` 打开开发者工具，点击 `Network`（网络）标签
4. 刷新页面，在请求列表中找到任意请求（如 `home`）
5. 在请求头中找到 `cookie:` 字段，**右键复制完整 Cookie 值**

#### 3. 配置 GitHub Secrets

在你的仓库中，进入 **Settings** → **Secrets and variables** → **Actions**，点击 **New repository secret** 添加以下密钥：

| Name | Description | Required |
|------|-------------|----------|
| `JUEJIN_COOKIE` | 掘金 Cookie（从浏览器复制） | ✅ 是 |
| `EMAIL_FROM` | 发件邮箱地址（如：`your_email@163.com`） | ✅ 是 |
| `EMAIL_PASSWORD` | 邮箱授权码（不是登录密码！） | ✅ 是 |
| `EMAIL_TO` | 收件邮箱地址（默认同 `EMAIL_FROM`） | ❌ 否 |
| `SMTP_SERVER` | SMTP 服务器地址（默认 `smtp.163.com`） | ❌ 否 |
| `SMTP_PORT` | SMTP 端口（默认 `465`） | ❌ 否 |

> **注意**：邮箱授权码需要在邮箱设置中获取，以 163 邮箱为例：设置 → POP3/SMTP/IMAP → 开启 SMTP 服务 → 获取授权码。

#### 4. 启用 GitHub Actions

1. 进入仓库的 **Actions** 标签页
2. 点击 **"I understand my workflows, go ahead and enable them"**
3. 在左侧工作流列表中点击 **"Juejin Auto Sign - Selenium"**
4. 点击 **"Run workflow"** 可以手动测试运行

#### 5. 查看运行结果

- 每次运行后，你都会收到一封邮件通知
- 邮件中包含：连续签到天数、累计签到天数、矿石总数、今日获得矿石、签到详情和抽奖结果
- 可以在 Actions 页面查看详细运行日志

### ⏰ 定时任务

脚本默认每天 **北京时间 08:00** 自动运行（对应 UTC 时间 00:00）。如需修改时间，可以编辑 `.github/workflows/sign.yml` 中的 `cron` 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 时间 00:00（北京时间 08:00）
🧪 本地测试
如果你想在本地运行测试：

bash
# 1. 克隆仓库
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# 2. 安装依赖
pip install selenium webdriver-manager requests

# 3. 安装 Chrome 浏览器（如果还没有）
# macOS: brew install --cask google-chrome
# Ubuntu: sudo apt install google-chrome-stable

# 4. 设置环境变量并运行
export JUEJIN_COOKIE="your_cookie_here"
export EMAIL_FROM="your_email@163.com"
export EMAIL_PASSWORD="your_auth_code"
python juejin_selenium.py
⚠️ 注意事项
Cookie 会过期，如果发现签到失败，请重新获取 Cookie 并更新到 Secrets

邮箱授权码请妥善保管，不要泄露

GitHub Actions 免费额度足够日常使用，无需担心费用

如果抽奖接口变化，脚本可能需要相应调整

📸 效果预览
邮件通知示例：

text
┌─────────────────────────────────┐
│      ⛏️ 掘金签到                  │
├─────────────────────────────────┤
│ 连续：5天    累计：1464天         │
│ 矿石：1097074 今日：66矿石        │
├─────────────────────────────────┤
│ ✍️ 签到状态                       │
│ ✅ 签到成功                       │
│ 获得 66 矿石                      │
├─────────────────────────────────┤
│ 🎲 免费抽奖                       │
│ 🎁 获得 66 矿石                   │
├─────────────────────────────────┤
│ 每日自动执行 · 结果实时推送        │
└─────────────────────────────────┘
📄 许可证
MIT License

🤝 贡献
欢迎提交 Issue 或 Pull Request 来改进这个项目！

English
📖 Introduction
This is a Selenium-based auto sign-in script for Juejin community, running daily via GitHub Actions. It can:

✅ Auto sign in to claim ore points

🎁 Auto lottery draw after sign-in (once per day)

📊 Fetch user statistics (consecutive days, total days, total ore)

💎 Accurately record today's earned ore (sign-in + lottery)

📧 Send beautiful email notifications with detailed stats and lottery results

✨ Features
Full Browser Simulation: Uses Selenium headless mode, automatically handles all dynamic parameters (msToken, a_bogus, etc.)

Smart Navigation: Automatically switches from sign-in page to lottery page

Precise Data Extraction: Accurately extracts sign-in days, ore counts using regex

Prize Recognition: Identifies specific prize names and ore amounts

Email Notifications: Clean and elegant HTML email template with stats cards

Bilingual Support: Chinese and English README with code comments

🛠️ Tech Stack
Python 3.10

Selenium + ChromeDriver

GitHub Actions

WebDriver Manager

SMTP (Email Sending)

📁 File Structure
text
.
├── .github/
│   └── workflows/
│       └── sign.yml          # GitHub Actions workflow config
├── juejin_selenium.py         # Main script
└── README.md                  # Documentation
🚀 Quick Start
1. Fork this Repository
Click the Fork button in the top-right corner to copy this repository to your GitHub account.

2. Get Juejin Cookie
Open browser (Chrome/Edge) in incognito mode and visit https://juejin.cn/

Log in to your Juejin account

Press F12 to open Developer Tools, click the Network tab

Refresh the page, find any request (e.g., home)

In the request headers, find the cookie: field, right-click and copy the full Cookie value

3. Configure GitHub Secrets
In your repository, go to Settings → Secrets and variables → Actions, click New repository secret to add the following:

Name	Description	Required
JUEJIN_COOKIE	Juejin Cookie (copied from browser)	✅ Yes
EMAIL_FROM	Sender email (e.g., your_email@163.com)	✅ Yes
EMAIL_PASSWORD	Email auth code (not your login password!)	✅ Yes
EMAIL_TO	Recipient email (defaults to EMAIL_FROM)	❌ No
SMTP_SERVER	SMTP server (default smtp.163.com)	❌ No
SMTP_PORT	SMTP port (default 465)	❌ No
Note: The email auth code must be obtained from your email provider's settings. For 163 email: Settings → POP3/SMTP/IMAP → Enable SMTP → Get auth code.

4. Enable GitHub Actions
Go to the Actions tab of your repository

Click "I understand my workflows, go ahead and enable them"

In the left sidebar, click "Juejin Auto Sign - Selenium"

Click "Run workflow" to manually test

5. Check Results
You'll receive an email notification after each run

Email contains: consecutive days, total days, total ore, today's ore, sign-in details, and lottery results

You can view detailed logs in the Actions tab

⏰ Schedule
The script runs daily at 08:00 Beijing Time (UTC 00:00). To change the schedule, edit the cron expression in .github/workflows/sign.yml:

yaml
schedule:
  - cron: '0 0 * * *'  # UTC 00:00 (Beijing 08:00)
🧪 Local Testing
To test locally:

bash
# 1. Clone repository
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# 2. Install dependencies
pip install selenium webdriver-manager requests

# 3. Install Chrome browser (if not already)
# macOS: brew install --cask google-chrome
# Ubuntu: sudo apt install google-chrome-stable

# 4. Set environment variables and run
export JUEJIN_COOKIE="your_cookie_here"
export EMAIL_FROM="your_email@163.com"
export EMAIL_PASSWORD="your_auth_code"
python juejin_selenium.py
⚠️ Notes
Cookies expire; if sign-in fails, get a new cookie and update the Secret

Keep your email auth code secure

GitHub Actions free tier is sufficient for daily use

Script may need adjustments if the lottery interface changes

📸 Preview
Email Notification Example:

text
┌─────────────────────────────────┐
│      ⛏️ Juejin Auto Sign         │
├─────────────────────────────────┤
│ Consecutive: 5   Total: 1464    │
│ Ore: 1097074     Today: 66      │
├─────────────────────────────────┤
│ ✍️ Sign Status                   │
│ ✅ Success                       │
│ Earned 66 ore                    │
├─────────────────────────────────┤
│ 🎲 Free Lottery                  │
│ 🎁 Won 66 ore                    │
├─────────────────────────────────┤
│ Daily Auto Run · Real-time Push │
└─────────────────────────────────┘
📄 License
MIT License

🤝 Contributing
Issues and Pull Requests are welcome!
