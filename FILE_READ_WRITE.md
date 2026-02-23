# SpecForge 文件读写功能

SpecForge 现在支持读取现有文档和生成新文档到文件，解决导出为空的问题。

## 新增功能

### 1. 加载现有文档 (`--file`)

启动时加载现有的 PRD 或 Tech Spec：

```bash
# 加载现有文档继续工作
specforge new --file ./my_project/PRD.md

# 或使用短选项
specforge new -f ./my_project/TECH_SPEC.md
```

**功能：**
- 自动读取文件内容
- 根据文件名自动设置工作流阶段
- PRD.md → Definition 阶段
- TECH_SPEC.md / TECHSPEC.md → Delivery 阶段
- 将内容发送给 AI 进行分析

### 2. 读取文件命令 (`/read`)

在会话中读取任何文件：

```bash
> /read ./requirements.txt
> /read ./existing_prd.md
> /read ./notes.txt
```

**功能：**
- 读取文件内容
- 自动发送给 AI 分析
- AI 可以基于文件内容回答问题或生成新文档

### 3. 写入文件命令 (`/write`)

生成 PRD 或 Tech Spec 到指定文件：

```bash
> /write prd ./my_project/PRD.md
> /write techspec ./my_project/TECH_SPEC.md
```

**功能：**
- 基于当前会话内容生成文档
- 自动创建父目录
- 显示生成的字符数
- 与 `/export` 不同，可以单独生成一种文档

## 命令对比

| 命令 | 用途 | 输出 |
|------|------|------|
| `/export <dir>` | 导出完整文档集 | PRD.md + TECH_SPEC.md |
| `/write prd <path>` | 单独生成 PRD | 指定路径的 PRD.md |
| `/write techspec <path>` | 单独生成 Tech Spec | 指定路径的 TECH_SPEC.md |
| `/read <path>` | 读取并分析文件 | AI 分析结果 |

## 使用场景

### 场景 1: 继续完善现有 PRD

```bash
# 启动时加载现有 PRD
specforge new --file ./my_project/PRD.md

✅ Loaded PRD.md (5234 characters)
╭─────────────────────────────────────────────┐
│ emoji: 🎯 Stage: DEFINITION                  │
└─────────────────────────────────────────────┘

> 我需要增加一个新功能：用户通知系统

AI: 好的，我来帮你增加这个功能到 PRD 中...

> /write prd ./my_project/PRD.md

✓ Written to: ./my_project/PRD.md (6150 characters)
```

### 场景 2: 基于 Tech Spec 生成 PRD

```bash
# 启动并加载 Tech Spec
specforge new --file ./my_project/TECH_SPEC.md

> 请基于这个技术方案生成 PRD

AI: [生成 PRD...]

> /write prd ./my_project/PRD.md
```

### 场景 3: 分析需求文档

```bash
> /read ./requirements.txt

✅ Loaded requirements.txt (1234 characters) - Sending to AI for analysis...

AI: 我已经分析了你的需求文档...
```

### 场景 4: 逐步生成文档

```bash
# 先生成 PRD
> /write prd ./my_project/PRD.md

# 稍后生成 Tech Spec
> /write techspec ./my_project/TECH_SPEC.md
```

## 修复的导出问题

### 问题原因

之前的 `generate_artifact` 使用了 `max_tokens=1600`，这对推理模型（如 gpt-5）来说太小，导致：
- 推理模型消耗所有 token 进行"思考"
- 没有剩余 token 生成实际输出
- 导出的文件为空

### 解决方案

1. **增加默认 max_tokens**: 从 1600 提升到 8000
2. **推理模型特殊处理**: 检测到推理模型时自动使用 40000 tokens
3. **提供 `/write` 命令**: 可以单独生成一种文档，更容易调试

### 验证修复

```bash
# 检查生成的文件是否为空
wc -l ./my_project/PRD.md
# 应该显示行数，而不是 0

cat ./my_project/PRD.md | head -20
# 应该看到文档内容
```

## 完整命令参考

| 命令 | 格式 | 说明 |
|------|------|------|
| `--file` | `--file <path>` 或 `-f <path>` | 启动时加载现有文档 |
| `/read` | `/read <path>` | 读取文件让 AI 分析 |
| `/write` | `/write prd\|techspec <path>` | 生成文档到指定路径 |
| `/export` | `/export <dir>` | 导出 PRD + Tech Spec |
| `/status` | `/status` | 查看当前阶段 |
| `/next` | `/next` | 推进到下一阶段 |
| `/goto` | `/goto <stage>` | 跳到指定阶段 |
| `/exit` | `/exit` | 退出会话 |

## 示例工作流

```bash
# 1. 加载现有 Tech Spec 继续工作
specforge new --file ./my_project/TECH_SPEC.md

# 2. 读取需求文档
> /read ./new_requirements.txt

# 3. 请求 AI 基于新需求更新文档
> 请根据刚才的需求文档更新 Tech Spec

# 4. 写入更新后的文档
> /write techspec ./my_project/TECH_SPEC_v2.md

# 5. 验证内容
> /read ./my_project/TECH_SPEC_v2.md
> 请总结这个文档的主要变更
```
