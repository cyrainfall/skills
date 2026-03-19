# OpenClaw 实战示例

## 场景一：从零安装部署

### macOS/Linux 快速部署

```bash
# 1. 一键安装
curl -fsSL https://openclaw.ai/install.sh | bash

# 2. 脚本自动引导配置，按提示选择：
#    - AI 供应商（如 Anthropic）
#    - 输入 API Key
#    - Gateway 端口（默认 18789）

# 3. 安装完成后自动打开 http://127.0.0.1:18789/chat
```

### Windows 快速部署

```powershell
# 1. PowerShell 安装
iwr -useb https://openclaw.ai/install.ps1 | iex

# 2. 如用 npm 安装
npm i -g openclaw
openclaw onboard --install-daemon
```

### 源码开发模式

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build
pnpm build
pnpm openclaw onboard --install-daemon
pnpm gateway:watch  # 开发热重载
```

## 场景二：配置 AI 模型

### 使用 Claude

```bash
openclaw models auth login --provider anthropic
# 浏览器弹出 OAuth 认证页面，完成后自动配置
```

### 使用通义千问（百炼平台）

```bash
openclaw models auth paste-token --provider bailian
# 输入百炼平台 API Key
openclaw models set bailian/qwen3-max
```

### 使用本地 Ollama

```bash
# 先确保 Ollama 运行中
openclaw models set ollama/llama3
```

### 查看可用模型并切换

```bash
openclaw models list
# 输出：
# * anthropic/claude-opus-4-6 (当前)
#   openai/gpt-4o
#   bailian/qwen3-max

openclaw models set openai/gpt-4o
```

## 场景三：接入聊天通道

### 接入 Telegram

```bash
# 1. 在 Telegram 找 @BotFather 创建 Bot，获取 Token
# 2. 添加通道
openclaw channels add --channel telegram --token <YOUR_BOT_TOKEN>

# 3. 验证状态
openclaw channels status
```

### 接入 WhatsApp

```bash
openclaw channels login
# 手机打开 WhatsApp -> 设置 -> 已关联设备 -> 关联设备 -> 扫码
```

### 接入 Discord

```bash
# 1. 在 Discord Developer Portal 创建 Bot
# 2. 添加通道
openclaw channels add --channel discord --token <BOT_TOKEN>
```

### 接入飞书

```bash
# 飞书需要先启用插件
openclaw plugins install feishu
openclaw plugins enable feishu
openclaw channels add --channel feishu
```

## 场景四：日常运维操作

### 检查系统状态

```bash
openclaw status
# Gateway: Running (port 18789)
# Channels: 2 active (telegram, whatsapp)
# Model: anthropic/claude-opus-4-6
# Uptime: 3d 14h
```

### 更新版本

```bash
openclaw update
openclaw restart
```

### 完整排查流程

```bash
# AI 突然不回复了
openclaw doctor          # 体检
openclaw logs            # 看日志
openclaw status --deep   # 深度检查
openclaw doctor --fix    # 自动修复
openclaw restart         # 重启
```

### 重建记忆索引

```bash
openclaw memory index
```

## 场景五：技能扩展

### 搜索和安装社区技能

```bash
# 搜索
clawhub search "web scraper"

# 安装
clawhub install web-scraper

# 查看已安装
openclaw skills list
```

### 批量更新技能

```bash
clawhub sync --all
```

### 直接在对话中安装

在 OpenClaw 对话窗口中发送：
> 安装 proactive-agent 技能

AI 会自动调用 ClawHub 完成安装。

## 场景六：自动化任务

### 通过 CLI 派发任务

```bash
# 普通任务
openclaw agent --message "帮我整理今天的邮件摘要"

# 复杂推理任务
openclaw agent --message "分析这份季度报告并生成要点" --thinking high
```

### 主动发送消息

```bash
# 发送到 WhatsApp
openclaw message send --to +8613800000000 --message "会议提醒：下午3点产品评审"
```

### 设备配对授权

```bash
# 批准新设备接入
openclaw pairing approve whatsapp ABC123
```

## 场景七：浏览器自动化

```bash
# 打开网页
openclaw browser open https://example.com

# 截图
openclaw browser screenshot

# 自动填写表单
openclaw browser type "#username" "admin"
openclaw browser type "#password" "***"
openclaw browser click "#login-btn"

# 获取页面结构
openclaw browser snapshot

# 关闭
openclaw browser close
```

## 场景八：对话中高效操作

```
# 开始新任务
/new 帮我写一份项目周报

# 上下文太长时压缩
/compact

# 切换到更强模型处理复杂问题
/model claude-opus-4-6

# 查看费用
/cost

# 创建子会话并行处理
/sessions spawn 同时帮我查一下竞品分析

# 查看历史会话
/sessions list
```

## 场景九：配置文件手动编辑

```bash
openclaw config edit
```

常见配置项（`~/.openclaw/openclaw.json`）：

```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-6"
  },
  "gateway": {
    "port": 18789
  },
  "channels": {
    "telegram": {
      "token": "YOUR_BOT_TOKEN"
    }
  },
  "dmPolicy": "pairing"
}
```

## 场景十：沙箱环境管理

```bash
# 查看沙箱状态
openclaw sandbox explain

# 重建出问题的沙箱
openclaw sandbox recreate --all

# 强制重建（跳过确认）
openclaw sandbox recreate --all --force
```

## 场景十一：解决 Discord Bot 不回复（代理环境）

适用于中国大陆等需要代理才能访问 Discord API 的网络环境。

### 问题诊断

```bash
# 启动 Gateway 并查看日志
openclaw gateway --port 18789 --verbose

# 日志中出现以下错误说明是此问题：
# final reply failed: TypeError: fetch failed
# discord typing failed target=...
# failed to fetch bot identity: TypeError: fetch failed
#
# 同时 WebSocket 连接正常：
# discord gateway: WebSocket connection opened
# messagesReceived: 18
```

### 解决步骤

**第一步: 创建代理预加载模块**

创建文件 `~/.openclaw/discord-proxy-preload.mjs`：

```javascript
import { createRequire } from 'node:module';

// 修改为你的 OpenClaw 安装路径
const require = createRequire('E:/node-v22.20.0-win-x64/node_modules/openclaw/package.json');
const { ProxyAgent, fetch: undiciFetch } = require('undici');

const PROXY_URL = 'http://127.0.0.1:7890';  // 修改为你的代理地址
const PROXY_DOMAINS = [
  'discord.com', 'discordapp.com',
  'discord.gg', 'cdn.discordapp.com'
];
const proxyAgent = new ProxyAgent(PROXY_URL);
const originalFetch = globalThis.fetch;

function shouldProxy(urlStr) {
  try {
    const url = typeof urlStr === 'string' ? new URL(urlStr)
      : urlStr instanceof URL ? urlStr
      : urlStr?.url ? new URL(urlStr.url) : null;
    if (!url) return false;
    return PROXY_DOMAINS.some(d =>
      url.hostname === d || url.hostname.endsWith('.' + d)
    );
  } catch { return false; }
}

globalThis.fetch = function patchedFetch(input, init) {
  if (shouldProxy(input)) {
    return undiciFetch(input, { ...init, dispatcher: proxyAgent });
  }
  return originalFetch.call(globalThis, input, init);
};

console.log('[discord-proxy-preload] globalThis.fetch patched for Discord domains via', PROXY_URL);
```

**第二步: 创建启动脚本**

创建文件 `~/.openclaw/start-gateway.bat`：

```batch
@echo off
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
set NO_PROXY=maas-api.cn-huabei-1.xf-yun.com,.xf-yun.com,localhost,127.0.0.1
set NODE_OPTIONS=--import file:///C:/Users/HP/.openclaw/discord-proxy-preload.mjs
E:\node-v22.20.0-win-x64\openclaw.cmd gateway --port 18789 --verbose %*
```

> 注意：修改以上路径和代理地址为你自己的实际值。

**第三步: 使用启动脚本启动**

```bash
# 以后用此脚本替代直接运行 openclaw gateway
~/.openclaw/start-gateway.bat
```

### 验证成功

```
# 启动日志应出现：
[discord-proxy-preload] globalThis.fetch patched for Discord domains via http://127.0.0.1:7890
logged in to discord as 1477603419329003550 (cyx_clawbot)

# 不再出现 "fetch failed" 错误
# Discord Bot 正常收发消息
```

### 原理说明

OpenClaw 使用 `@buape/carbon` 库与 Discord 通信。该库的 `RequestClient` 直接调用 `globalThis.fetch`，不使用 OpenClaw 配置的代理。而 WebSocket 连接由 OpenClaw 自行管理，已正确配置了 `HttpsProxyAgent`。

Preload 模块利用 Node.js 的 `--import` 机制，在 OpenClaw 启动前替换 `globalThis.fetch`，仅对 Discord 域名启用代理转发，国内大模型 API 等其他请求不受影响。此方案不修改任何源码，版本更新后依然有效。

## 场景十二：配置讯飞星火等 OpenAI 兼容大模型

### 配置示例

在 `~/.openclaw/openclaw.json` 中添加模型供应商：

```json
{
  "modelProviders": [{
    "name": "xfyun",
    "baseUrl": "https://maas-api.cn-huabei-1.xf-yun.com/v2",
    "apiKey": "YOUR_API_KEY",
    "apiType": "openai-completions",
    "models": [{
      "name": "xfyun/spark-max",
      "contextWindow": 128000
    }]
  }]
}
```

### 注意事项

- `baseUrl` 只填到 API 根路径，**不要**包含 `/chat/completions`
- `apiType` 使用 `openai-completions`（OpenAI SDK 兼容模式）
- `contextWindow` 根据模型实际支持的上下文长度设置
- 配置后检查 `~/.openclaw/agents/main/agent/models.json`，确认 `baseUrl` 无路径重复
