# SpecForge 进度指示器说明

SpecForge 现在提供了详细的进度反馈，让你知道程序正在做什么，而不是一直卡在 "Thinking..." 状态。

## 进度指示器类型

### 1. 多阶段进度条

对于长时间操作（如 API 调用），SpecForge 显示多个阶段的进度：

```
🔗 Connecting to API (Stage: discovery)...
  ↓
📤 Sending your request...
  ↓
🧠 AI is analyzing... (this may take 10-30s for reasoning models)
  ↓
📝 Processing response...
```

每个阶段会自动切换，给你实时反馈。

### 2. URL 获取进度

当你的输入包含 URL 时，会显示获取和分析进度：

```
📥 Fetching https://example.com/article.pdf...
  ↓
  ✓ Fetched and summarized (1234 chars)
```

### 3. 文档生成进度

生成 PRD 和 Tech Spec 时显示详细进度：

```
🔗 Connecting to API for PRD generation...
  ↓
📤 Preparing request...
  ↓
🧠 AI is writing PRD (this may take 20-40s)...
  ↓
📝 Finalizing PRD document...

✓ PRD generated!

  Now generating Tech Spec...

🔗 Connecting to API for Tech Spec...
  ↓
📤 Preparing request...
  ↓
🧠 AI is writing technical specifications...
  ↓
📝 Finalizing Tech Spec document...

✓ Tech Spec generated!
```

## 各阶段的含义

| 图标 | 阶段 | 说明 |
|------|------|------|
| 🔗 | Connecting | 建立 API 连接 |
| 📤 | Sending | 发送你的请求到服务器 |
| 🧠 | AI is thinking | AI 正在分析/生成内容（通常最慢） |
| 📝 | Processing | 处理响应并格式化输出 |
| ✓ | Success | 操作成功完成 |
| ✗ | Failed | 操作失败 |
| 📥 | Fetching | 下载 URL 内容 |

## 预期等待时间

根据不同的操作和模型类型：

### 普通 AI 响应
- **连接**: < 1秒
- **发送**: < 1秒
- **AI 思考**: 5-15秒
- **处理**: < 1秒
- **总计**: 10-20秒

### 推理模型 (o1, gpt-5 等)
- **连接**: < 1秒
- **发送**: < 1秒
- **AI 思考**: 15-40秒（推理模型需要更多时间）
- **处理**: < 1秒
- **总计**: 20-50秒

### 文档生成
- **单个文档 (PRD 或 Tech Spec)**: 20-40秒
- **两个文档**: 40-80秒

### URL 获取
- **网页**: 2-5秒
- **PDF**: 5-15秒（取决于文件大小）

## 如何判断是否卡住

如果进度指示器在某个阶段停留超过以下时间，可能有问题：

| 阶段 | 超时阈值 | 可能原因 |
|------|----------|----------|
| Connecting | 10秒 | 网络问题、API 服务器故障 |
| Sending | 5秒 | 网络问题 |
| AI is thinking | 60秒 | API 服务器过载、模型问题 |
| Processing | 10秒 | 响应数据异常大 |

如果遇到超时，按 `Ctrl+C` 中断，然后检查：
1. 网络连接
2. `.env` 配置
3. API 额度

## 优化建议

如果觉得等待时间太长：

1. **使用更快的模型**
   ```bash
   # 在 .env 中设置
   SPECFORGE_MODEL=anthropic/claude-3-5-sonnet-latest  # 快速响应
   SPECFORGE_MODEL=azure/gpt-4o  # 平衡速度和质量
   ```

2. **避免使用推理模型**
   ```bash
   # 避免使用这些（除非特别需要）:
   # SPECFORGE_MODEL=azure/gpt-5.2-2025-12-11
   # SPECFORGE_MODEL=openai/o1
   ```

3. **减少 URL 数量**
   - 每次最多处理 3 个 URL
   - 优先选择最相关的文档
