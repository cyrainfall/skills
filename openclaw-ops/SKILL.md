---
name: openclaw-ops
description: "OpenClaw (Clawdbot/Moltbot) AI 智能体框架的安装、配置、部署和日常运维操作指南。当用户提及 OpenClaw、Clawdbot、Moltbot、openclaw 命令、Gateway 网关、通道配置（WhatsApp/Telegram/Discord/飞书）、ClawHub 技能市场、AI 助手部署时触发此技能。"
---

# OpenClaw 操作指南

## 概述

OpenClaw（原 Clawdbot/Moltbot）是开源多通道 AI 智能体框架，支持 WhatsApp、Telegram、Discord、Slack、飞书等平台接入，兼容 Claude、GPT、DeepSeek、Ollama、通义千问等模型。

- 官方仓库: `https://github.com/openclaw/openclaw`
- 官方文档: `https://docs.openclaw.ai`
- 技能市场: `https://clawhub.ai`

## 环境要求

- **Node.js >= 22**（推荐 pnpm）
- **系统**: macOS / Windows / Linux
- **硬件**: 最低 2GB RAM
- 可选: Docker（沙箱功能需要）

## 安装方式

### 方式一: 一键脚本（推荐）

```bash
# macOS/Linux
curl -fsSL https://openclaw.ai/install.sh | bash

# Windows PowerShell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

### 方式二: npm/pnpm

```bash
npm i -g openclaw
# 或
pnpm add -g openclaw

openclaw onboard --install-daemon  # 初始化 + 开机自启
```

### 方式三: 源码（开发模式）

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install && pnpm ui:build && pnpm build
pnpm openclaw onboard --install-daemon
```

## 初始化配置

运行 `openclaw onboard` 进入交互式向导：

1. 选择 AI 模型供应商，输入 API Key
2. 配置 Gateway 端口（默认 18789）
3. 可选安装预设技能
4. 完成后访问 `http://127.0.0.1:18789/chat`

配置文件位置：`~/.openclaw/openclaw.json`

最小配置示例：
```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-6"
  }
}
```

## 核心 CLI 命令速查

### 基础操作

| 命令 | 说明 |
|------|------|
| `openclaw --version` | 查看版本 |
| `openclaw tui` | 终端交互界面 |
| `openclaw dashboard` | 网页管理控制台 |
| `openclaw status` | 查看运行状态 |
| `openclaw restart` | 重启服务（改配置后必执行） |
| `openclaw stop` | 停止服务 |
| `openclaw update` | 更新到最新版 |

### 网关 Gateway

| 命令 | 说明 |
|------|------|
| `openclaw gateway` | 启动网关 |
| `openclaw gateway --port 18789` | 指定端口启动 |
| `openclaw gateway --verbose` | 详细日志模式 |
| `openclaw gateway restart` | 重启网关 |

### 模型管理

| 命令 | 说明 |
|------|------|
| `openclaw models list` | 列出已配置模型 |
| `openclaw models set <模型>` | 切换默认模型 |
| `openclaw models auth login --provider <供应商>` | OAuth 登录 |
| `openclaw models auth paste-token --provider <供应商>` | Token 认证 |

### 通道管理

| 命令 | 说明 |
|------|------|
| `openclaw channels list` | 查看已配置通道 |
| `openclaw channels status` | 通道实时状态 |
| `openclaw channels add` | 交互式添加通道 |
| `openclaw channels add --channel <名称> --token <TOKEN>` | 非交互式添加 |
| `openclaw channels remove --channel <名称>` | 移除通道 |
| `openclaw channels login` | 登录通道（如 WhatsApp 扫码） |
| `openclaw channels logout` | 登出通道 |

支持平台: whatsapp, telegram, discord, slack, googlechat, signal, imessage, msteams, mattermost, feishu

### Agent 操作

| 命令 | 说明 |
|------|------|
| `openclaw agent --message "任务"` | 派发任务 |
| `openclaw agent --message "任务" --thinking high` | 高思考深度 |
| `openclaw message send --to <号码> --message "内容"` | 主动发消息 |

### 诊断排错

```bash
openclaw doctor          # 全面健康检查
openclaw doctor --fix    # 自动修复
openclaw status --deep   # 深度状态检测
openclaw logs            # 查看运行日志
```

**标准排查流程**: `doctor` -> `logs` -> `status --deep` -> `doctor --fix` -> `restart`

### 技能管理

| 命令 | 说明 |
|------|------|
| `openclaw skills list` | 列出已安装技能 |
| `openclaw skills install <技能名>` | 安装技能 |
| `clawhub search <关键词>` | 搜索社区技能 |
| `clawhub install <技能名>` | 安装社区技能 |
| `clawhub sync --all` | 批量更新技能 |

### 插件管理

| 命令 | 说明 |
|------|------|
| `openclaw plugins list` | 查看可用插件 |
| `openclaw plugins enable <名>` | 启用插件 |
| `openclaw plugins disable <名>` | 禁用插件 |
| `openclaw plugins install <名>` | 安装新插件 |

## 聊天斜杠命令

在对话窗口中使用 `/` 命令：

| 命令 | 说明 |
|------|------|
| `/new` | 新建会话 |
| `/new 任务描述` | 新建会话并带任务 |
| `/compact` | 压缩上下文（省 Token） |
| `/model <模型名>` | 实时切换模型 |
| `/cost` | 查看 Token 消耗和费用 |
| `/approve` / `/deny` | 批准/拒绝操作 |
| `/cancel` | 取消当前任务 |
| `/undo` | 撤销上一步 |
| `/skills` | 查看已加载技能 |
| `/memory` | 查看长期记忆 |
| `/sessions list` | 列出历史会话 |

## 关键文件路径

| 路径 | 说明 |
|------|------|
| `~/.openclaw/openclaw.json` | 主配置文件 |
| `~/.openclaw/workspace/` | 默认工作目录 |
| `~/.openclaw/workspace/AGENTS.md` | 核心提示词文件 |
| `~/.openclaw/skills/` | 全局技能目录 |
| `~/.openclaw/agents/<ID>/USER.md` | 用户偏好文件 |
| `~/.openclaw/agents/<ID>/memory/` | 长期记忆目录 |

> Windows 中 `~` 等于 `%USERPROFILE%`

## 常见问题与故障排查

### 问题一：大模型 API 返回空内容（No reply from agent）

**症状**: Agent 会话记录中 `"content":[],"usage":{"input":0,"output":0}`，大模型无回复。

**根因**: 使用 OpenAI 兼容模式（`openai-completions`）时，OpenClaw 配置系统会自动在 `baseUrl` 后追加 `/chat/completions`，而 OpenAI Node SDK 在发送请求时也会追加 `/chat/completions`，导致最终请求 URL 出现路径重复：

```
配置的 baseUrl:  https://api.example.com/v2/chat/completions
实际请求 URL:    https://api.example.com/v2/chat/completions/chat/completions  ← 重复
```

**解决方案**:

1. 在 `~/.openclaw/openclaw.json` 中，`baseUrl` 只填到 API 根路径（不含 `/chat/completions`）：
   ```json
   {
     "modelProviders": [{
       "baseUrl": "https://api.example.com/v2",
       "apiType": "openai-completions"
     }]
   }
   ```
2. 同步检查 `~/.openclaw/agents/main/agent/models.json`，确保其中的 `baseUrl` 也不含重复路径。
3. 修改后执行 `openclaw restart` 重启服务。

---

### 问题二：Discord Bot 收到消息但不回复（fetch failed）

**症状**: Gateway 日志显示 Discord WebSocket 连接正常、消息已接收、Agent 生成了回复，但发送回复时报错：

```
final reply failed: TypeError: fetch failed
discord typing failed target=...
failed to fetch bot identity: TypeError: fetch failed
```

**根因**: 在中国大陆等需要代理才能访问 Discord API 的网络环境中，OpenClaw 的 Discord 通道配置了 `proxy` 字段，OpenClaw 也正确为自己的 REST 请求创建了 ProxyAgent。但底层依赖库 `@buape/carbon` 的 `RequestClient` 类直接使用 `globalThis.fetch`，完全绕过了代理配置。WebSocket 连接不受影响（OpenClaw 单独为其配置了 HttpsProxyAgent），但所有 REST API 调用（发消息、设置打字状态、获取 Bot 身份等）都失败。

**解决方案（Preload 模块 — 不修改源码，版本更新安全）**:

1. 创建代理预加载模块 `~/.openclaw/discord-proxy-preload.mjs`：

```javascript
/**
 * Discord Proxy Preload Module
 * 通过 NODE_OPTIONS="--import <path>" 预加载
 * 在 OpenClaw 启动前将 globalThis.fetch 替换为代理感知版本
 * 仅对 Discord 域名走代理，其他请求（如国内大模型 API）不受影响
 */
import { createRequire } from 'node:module';

// 使用 OpenClaw 自带的 undici 依赖（无需额外安装）
const require = createRequire('<openclaw安装路径>/package.json');
const { ProxyAgent, fetch: undiciFetch } = require('undici');

const PROXY_URL = 'http://127.0.0.1:7890';  // 改为你的代理地址
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

2. 创建启动脚本 `~/.openclaw/start-gateway.bat`（Windows）：

```batch
@echo off
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
set NO_PROXY=你的大模型API域名,localhost,127.0.0.1
set NODE_OPTIONS=--import file:///C:/Users/<用户名>/.openclaw/discord-proxy-preload.mjs
openclaw gateway --port 18789 --verbose %*
```

3. 以后通过 `start-gateway.bat` 启动 Gateway 即可，无需手动设置环境变量。

**验证成功标志**:
- 启动日志出现 `[discord-proxy-preload] globalThis.fetch patched for Discord domains via ...`
- 不再出现 `fetch failed` 错误
- Discord Bot 正常回复消息

**为什么不直接修改源码**: 修改 `@buape/carbon` 或 OpenClaw 的 bundle 文件虽然也能解决，但每次 `openclaw update` 后修改会被覆盖。Preload 模块方案利用标准 Node.js 机制，完全独立于 OpenClaw 源码，版本更新不受影响。

---

### 问题三：代理环境下大模型 API 被代理拦截

**症状**: 配置了 HTTP_PROXY 后，国内大模型 API（如讯飞星火、通义千问）请求也走了代理，导致延迟高或连接失败。

**解决方案**: 在启动脚本中设置 `NO_PROXY` 排除国内 API 域名：

```batch
set NO_PROXY=maas-api.cn-huabei-1.xf-yun.com,.xf-yun.com,.aliyuncs.com,localhost,127.0.0.1
```

上述 Preload 模块方案天然解决此问题：只有 Discord 域名走代理，其他所有请求使用原始 fetch。

## 更多参考

- 完整命令参考: [reference.md](reference.md)
- 实战使用示例: [examples.md](examples.md)
