# OpenClaw 完整命令参考

## 一、基础操作

```bash
openclaw --version              # 查看版本
openclaw --help                 # 显示帮助
openclaw tui                    # 终端交互界面（推荐新手）
openclaw dashboard              # 打开网页管理控制台
openclaw restart                # 重启服务（修改配置后必须执行）
openclaw stop                   # 停止服务
openclaw update                 # 更新到最新稳定版
openclaw update --channel beta  # 切换到测试版
```

## 二、安装与初始化

```bash
openclaw onboard                   # 启动配置向导
openclaw onboard --install-daemon  # 配置 + 安装为系统服务（开机自启）
openclaw configure                 # 重新进入配置向导
```

## 三、网关 Gateway 管理

网关是 OpenClaw 的通信调度核心。

```bash
openclaw gateway                      # 启动网关
openclaw gateway --port 18789         # 指定端口启动
openclaw gateway --verbose            # 详细日志模式
openclaw gateway restart              # 重启网关
openclaw gateway --token <token>      # 带认证 Token 启动
```

## 四、模型管理

支持 OAuth 和 API Token 两种认证方式。

```bash
openclaw models list                                          # 列出所有已配置模型
openclaw models set <提供商/模型名>                            # 切换默认模型
openclaw models set bailian/qwen3-max                         # 示例：切换到通义千问
openclaw models auth login --provider <提供商>                 # OAuth 方式登录
openclaw models auth paste-token --provider <提供商>           # 粘贴 API Token
```

支持的模型供应商：Anthropic (Claude)、OpenAI (GPT)、Google (Gemini)、阿里百炼 (Qwen)、DeepSeek、MiniMax、Ollama（本地）等。

## 五、通道 Channel 管理

### 查看与添加

```bash
openclaw channels list                                        # 列出已配置通道
openclaw channels status                                      # 实时状态（绿=正常，红=异常）
openclaw channels add                                         # 交互式添加新通道
openclaw channels add --channel telegram --token <BOT_TOKEN>  # 非交互式添加
openclaw channels remove --channel <名称>                      # 移除通道
openclaw channels logs                                        # 查看通道日志
```

### 登录与登出

```bash
openclaw channels login     # 登录（如 WhatsApp Web 扫码配对）
openclaw channels logout    # 登出通道
```

### 支持的通道

| 通道 | 标识 | 备注 |
|------|------|------|
| WhatsApp | `whatsapp` | 扫码配对 |
| Telegram | `telegram` | 需 Bot Token |
| Discord | `discord` | 需 Bot Token |
| Slack | `slack` | 需 Bot Token |
| Google Chat | `googlechat` | 需配置 |
| Signal | `signal` | 端到端加密 |
| iMessage | `imessage` | 仅 macOS |
| MS Teams | `msteams` | 需配置 |
| Mattermost | `mattermost` | 自建 |
| 飞书 | `feishu` | 需插件 |

## 六、Agent 操作与消息

```bash
openclaw agent --message "任务描述"                # 向 Agent 派发任务
openclaw agent --message "分析报告" --thinking high  # 高思考深度模式
openclaw message send --to +1234567890 --message "内容"  # 主动发送消息
openclaw pairing approve <通道> <配对码>            # 批准设备配对
```

## 七、诊断与排错

```bash
openclaw doctor              # 全面健康检查
openclaw doctor --fix        # 健康检查 + 自动修复
openclaw status              # 查看运行状态
openclaw status --deep       # 深度状态检测
openclaw logs                # 查看运行日志
```

### 标准排查流程

```bash
# 出问题按此顺序执行
openclaw doctor          # 1. 全面体检
openclaw logs            # 2. 查看日志
openclaw status --deep   # 3. 深度检查
openclaw doctor --fix    # 4. 自动修复
openclaw restart         # 5. 重启服务
```

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| AI 无回复 | 检查通道配对列表是否已批准 |
| Agent 返回空内容 | 检查 `baseUrl` 是否包含重复的 `/chat/completions` 路径（详见下方说明） |
| Discord bot 不回复 | 代理环境下需使用 Preload 模块解决 `fetch failed`（详见下方说明） |
| Discord typing failed | 同上，`@buape/carbon` 的 REST 请求未走代理 |
| 认证过期 | `openclaw models auth setup-token` |
| 内存异常 | `openclaw memory index` 重建索引 |
| 端口被占 | `openclaw gateway --port <其他端口>` |

### baseUrl 路径重复问题

使用 `openai-completions` API 类型时，OpenClaw 配置系统会自动在 `baseUrl` 后追加 `/chat/completions`，而 OpenAI Node SDK 发送请求时也会追加该路径。如果你在配置中填写了完整路径，会导致双重追加：

```
错误: baseUrl = "https://api.example.com/v2/chat/completions"
结果: 请求 → https://api.example.com/v2/chat/completions/chat/completions

正确: baseUrl = "https://api.example.com/v2"
结果: 请求 → https://api.example.com/v2/chat/completions
```

**修复步骤**:
1. 编辑 `~/.openclaw/openclaw.json`，将 `baseUrl` 修改为不含 `/chat/completions` 的根路径
2. 检查 `~/.openclaw/agents/main/agent/models.json`，同步修正其中的 `baseUrl`
3. 执行 `openclaw restart`

### Discord 代理配置（中国大陆等受限网络）

在需要代理才能访问 Discord API 的环境中，仅在 `openclaw.json` 中配置 `proxy` 字段不够——底层 `@buape/carbon` 库直接使用 `globalThis.fetch`，不走代理。

**问题现象**: WebSocket 连接正常（消息能收到），但 REST API 调用失败（无法发送回复、无法设置打字状态）。

**推荐方案**: 使用 Node.js Preload 模块在启动前拦截 `globalThis.fetch`，仅对 Discord 域名启用代理。

所需文件:
- `~/.openclaw/discord-proxy-preload.mjs` — 代理拦截模块
- `~/.openclaw/start-gateway.bat` — 启动脚本（设置环境变量 + 预加载模块）

此方案不修改任何 OpenClaw 或第三方库的源码，版本更新后无需重新配置。

完整代码和使用方式参见 [SKILL.md](SKILL.md) 中"问题二：Discord Bot 收到消息但不回复"章节。

## 八、技能 Skill 管理

### 本地管理

```bash
openclaw skills list              # 列出已安装技能
openclaw skills install <技能名>   # 安装技能
```

### ClawHub 技能市场

```bash
clawhub search <关键词>       # 搜索社区技能
clawhub install <技能名>      # 安装社区技能
clawhub list                  # 列出已安装技能
clawhub sync --all            # 批量更新所有技能
clawhub update <技能名>       # 更新指定技能
```

## 九、插件 Plugin 管理

```bash
openclaw plugins list              # 查看可用插件
openclaw plugins enable <插件名>    # 启用插件
openclaw plugins disable <插件名>   # 禁用插件
openclaw plugins install <插件名>   # 安装新插件
openclaw plugins doctor            # 检查插件加载错误
```

## 十、沙箱 Sandbox 管理

需要 Docker 支持。

```bash
openclaw sandbox explain               # 查看沙箱配置
openclaw sandbox explain --json        # JSON 格式输出
openclaw sandbox list                  # 列出所有沙箱容器
openclaw sandbox list --browser        # 仅查看浏览器容器
openclaw sandbox recreate --all        # 重建所有容器
openclaw sandbox recreate --all --force  # 强制重建
```

## 十一、浏览器控制

```bash
openclaw browser open <URL>           # 打开网页
openclaw browser snapshot             # DOM 快照
openclaw browser click <元素>          # 点击元素
openclaw browser type <元素> <文字>    # 输入文字
openclaw browser screenshot           # 截取页面截图
openclaw browser close                # 关闭浏览器
openclaw browser console              # 查看控制台日志
```

## 十二、记忆管理

```bash
openclaw memory search "关键词"     # 搜索长期记忆
openclaw memory index               # 重建记忆索引
```

## 十三、配置管理

```bash
openclaw config                    # 查看当前配置（只读）
openclaw config edit               # 编辑配置文件
openclaw config get <key>          # 获取指定配置
openclaw config set <key> <value>  # 设置配置项
```

配置文件路径：
- macOS/Linux: `~/.openclaw/openclaw.json`
- Windows: `%USERPROFILE%\.openclaw\openclaw.json`

## 十四、聊天斜杠命令

在对话窗口中使用，以 `/` 开头。

### 会话管理

| 命令 | 说明 |
|------|------|
| `/new` | 新建会话（清除上下文） |
| `/new 任务描述` | 新建会话并带任务 |
| `/compact` | 压缩上下文（省 Token） |
| `/status` | 查看会话状态 |
| `/help` 或 `/commands` | 显示可用命令 |

### 模型切换

| 命令 | 说明 |
|------|------|
| `/model` | 查看当前模型 |
| `/model <模型名>` | 实时切换模型 |

### 会话历史

| 命令 | 说明 |
|------|------|
| `/sessions list` | 列出历史会话 |
| `/sessions history` | 当前会话详细历史 |
| `/sessions send <ID> <消息>` | 跨会话通信 |
| `/sessions spawn <任务>` | 创建子会话 |

### 执行控制

| 命令 | 说明 |
|------|------|
| `/approve` | 批准待确认操作 |
| `/deny` | 拒绝待确认操作 |
| `/cancel` | 取消当前任务 |
| `/undo` | 撤销上一步 |

### 信息查询

| 命令 | 说明 |
|------|------|
| `/cost` | 查看 Token 消耗和费用 |
| `/version` | 查看版本 |
| `/ping` | 测试连接 |
| `/skills` | 查看已加载技能 |
| `/memory` | 查看长期记忆 |
| `/forget <内容>` | 删除指定记忆 |

## 十五、关键文件路径

| 路径 | 说明 |
|------|------|
| `~/.openclaw/openclaw.json` | 主配置文件（API Key、模型设置） |
| `~/.openclaw/workspace/` | 默认工作目录 |
| `~/.openclaw/workspace/AGENTS.md` | 核心提示词定义文件 |
| `~/.openclaw/workspace/USER.md` | 用户偏好文件 |
| `~/.openclaw/workspace/MEMORY.md` | 记忆文件 |
| `~/.openclaw/workspace/SOUL.md` | 人格定义文件 |
| `~/.openclaw/skills/` | 全局技能目录 |
| `~/.openclaw/agents/<ID>/USER.md` | Agent 用户偏好 |
| `~/.openclaw/agents/<ID>/memory/` | 长期记忆存储 |
| `~/.openclaw/agents/<ID>/cron/jobs.json` | 定时任务配置 |
| `~/.openclaw/agents/<ID>/sessions/` | 会话记录存档 |

> Windows 中 `~` 等于 `%USERPROFILE%`

## 十六、安全注意事项

- 默认 DM 策略要求未知发送者通过配对验证
- 如需开放公共消息，设置 `dmPolicy="open"`
- 入站 DM 视为不可信，建议最小化权限
- API Key 存储在本地 `openclaw.json`，勿泄露
