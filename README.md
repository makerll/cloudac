# 掘金社区自动签到脚本

一个功能完善的掘金社区自动签到脚本，支持每天随机时间签到，包含防检测功能，可在GitHub Action上自动运行。

## 功能特性

- ✅ 自动签到功能
- ✅ 随机时间签到（避免固定时间执行被检测）
- ✅ 防检测机制（随机User-Agent、真实请求头模拟）
- ✅ 签到状态检查（避免重复签到）
- ✅ GitHub Action自动运行
- ✅ 详细的执行日志

## 如何使用

### 1. 获取掘金Cookie

1. 打开浏览器，登录掘金社区
2. 按下 `F12` 打开开发者工具
3. 切换到 `Network` 选项卡
4. 刷新页面，找到任意一个请求
5. 在请求头中找到 `Cookie` 字段，复制其值

### 2. 本地测试

1. 克隆本仓库到本地
2. 编辑 `juejin_sign.py` 文件，将 `COOKIE` 变量替换为你获取的Cookie
3. 安装依赖：`pip install requests`
4. 运行脚本：`python juejin_sign.py`

### 3. GitHub Action配置

1. Fork本仓库到你的GitHub账号
2. 进入仓库页面，点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`，创建一个名为 `JUEJIN_COOKIE` 的secret，值为你获取的Cookie
4. 进入 `Actions` 选项卡，启用Workflow
5. 脚本会在每天随机时间自动运行

## 防检测机制

脚本包含以下防检测措施：

1. **随机时间延迟**：脚本启动后会随机等待1-300秒
2. **随机User-Agent**：每次请求使用不同的浏览器User-Agent
3. **真实请求头模拟**：包含完整的请求头信息，模拟真实浏览器
4. **请求间隔随机**：不同请求之间有随机延迟
5. **GitHub Action随机运行**：每3小时运行一次，配合脚本内随机延迟

## 脚本原理

1. 调用掘金API `https://api.juejin.cn/growth_api/v1/get_today_status` 检查今天是否已签到
2. 如果未签到，调用 `https://api.juejin.cn/growth_api/v1/check_in` 执行签到
3. 输出签到结果和获得的矿石数量

## 注意事项

1. **Cookie有效期**：掘金的Cookie有一定有效期，过期后需要重新获取并更新
2. **账号安全**：请勿将Cookie分享给他人，Cookie包含你的登录信息
3. **合理使用**：建议不要过于频繁地运行脚本，以免被系统检测
4. **GitHub Action限制**：GitHub Action有一定的运行时间限制，本脚本设计为快速执行

## 故障排查

如果脚本运行失败，可能的原因：

1. Cookie过期或无效
2. 网络连接问题
3. 掘金API变更

## 许可证

本项目采用 MIT 许可证

---

**使用说明**：本脚本仅用于学习和个人使用，请勿用于任何违反掘金社区规定的行为。
