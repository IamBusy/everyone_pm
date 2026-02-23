# SpecForge 交互式选择功能

SpecForge 现在支持类似 Claude Code 的交互式选择功能，AI 可以输出结构化的选项供你快速选择，大幅提升效率。

## 功能演示

### 传统方式 vs 新方式

#### ❌ 传统方式（需要大量输入）

```
AI: What type of product are you building?

User: I'm building a mobile app for iOS and Android
```

#### ✅ 新方式（选择 + 自定义输入）

```
AI: What type of product are you building?

┌─────────────────────────────────────────────┐
│ What type of product is this?               │
│                                             │
│ 1. Mobile app (iOS/Android)                 │
│ 2. Web application                          │
│ 3. Desktop software                         │
│ 4. API/Backend service                      │
│ 5. Browser extension                        │
│ 0. Other (type your own input)...           │
│                                             │
│ Enter choice number:                        │
└─────────────────────────────────────────────┘

User: > 1
```

## 选择类型

### 1. 单选 (Single Choice)

选择一个选项：

```markdown
@CHOICE:single
TITLE: Select your primary platform
1. iOS
2. Android
3. Web
4. Desktop
OTHER:true
@END_CHOICE
```

显示效果：
```
┌─────────────────────────────────────────────┐
│ Select your primary platform                 │
│                                             │
│ 1. iOS                                      │
│ 2. Android                                  │
│ 3. Web                                      │
│ 4. Desktop                                  │
│ 0. Other (type your own input)...           │
│                                             │
│ Enter choice number:                        │
└─────────────────────────────────────────────┘
```

### 2. 多选 (Multiple Choice)

选择多个选项（用逗号分隔）：

```markdown
@CHOICE:multiple
TITLE: Select all features you need:
1. User authentication
2. Real-time updates
3. File uploads
4. Payment processing
5. Analytics
@END_CHOICE
```

显示效果：
```
┌─────────────────────────────────────────────┐
│ Select all features you need:                │
│                                             │
│ 1. User authentication                       │
│ 2. Real-time updates                         │
│ 3. File uploads                              │
│ 4. Payment processing                        │
│ 5. Analytics                                 │
│                                             │
│ Enter numbers separated by commas:          │
└─────────────────────────────────────────────┘

User: > 1,3,5
```

### 3. 确认 (Confirmation)

简单的 Yes/No 选择：

```markdown
@CHOICE:confirm
TITLE: Focus on B2B or B2C?
1. B2B (Business-to-Business)
2. B2C (Business-to-Consumer)
@END_CHOICE
```

## 实际使用示例

### Discovery 阶段

```
AI: Let me understand your product better.

┌─────────────────────────────────────────────┐
│ Who is your primary target audience?        │
│                                             │
│ 1. Enterprise/business users                │
│ 2. Individual consumers (B2C)               │
│ 3. Developers/technical users               │
│ 4. Students/educators                       │
│ 0. Other (specify)...                       │
└─────────────────────────────────────────────┘

> 1

┌─────────────────────────────────────────────┐
│ What industry vertical?                     │
│                                             │
│ 1. Finance/FinTech                          │
│ 2. Healthcare/Medical                       │
│ 3. E-commerce/Retail                        │
│ 4. SaaS/Productivity                        │
│ 5. Education                                │
│ 0. Other...                                 │
└─────────────────────────────────────────────┘

> 1

AI: Great! So you're building a FinTech solution for
enterprise users. Let me explore the competitive
landscape...
```

### Definition 阶段

```
AI: Now let's define your MVP scope.

┌─────────────────────────────────────────────┐
│ Select MVP features (pick 3-5):             │
│                                             │
│ 1. User authentication (SSO/SAML)           │
│ 2. Real-time data dashboard                 │
│ 3. Alert/notification system                │
│ 4. Report generation & export               │
│ 5. API access for integration              │
│ 6. Multi-tenancy support                    │
│ 7. Audit logging                            │
└─────────────────────────────────────────────┘

> 1,2,3,4

AI: Perfect. Your MVP will focus on authentication,
real-time dashboards, alerts, and reporting.
```

### Ideation 阶段

```
AI: Let's choose the technology stack.

┌─────────────────────────────────────────────┐
│ Frontend framework?                         │
│                                             │
│ 1. React + TypeScript                       │
│ 2. Vue.js + TypeScript                      │
│ 3. Angular + TypeScript                     │
│ 4. Svelte + TypeScript                      │
└─────────────────────────────────────────────┘

> 1

┌─────────────────────────────────────────────┐
│ Backend framework?                          │
│                                             │
│ 1. Node.js + Express/Fastify                │
│ 2. Python + FastAPI/Django                  │
│ 3. Go + Gin/Echo                            │
│ 4. Java + Spring Boot                       │
└─────────────────────────────────────────────┘

> 2

AI: Excellent choice! React + TypeScript frontend
with Python FastAPI backend. Here's why this
combination works well for your use case...
```

## 快捷键

| 输入 | 动作 |
|------|------|
| `1`, `2`, `3`... | 选择对应编号的选项 |
| `1,3,5` | 多选时选择多个选项 |
| `0` | 进入自定义输入模式 |
| `q` | 跳过当前选择 |
| `Enter` | 使用默认选项（如果有） |

## AI 如何生成选择

AI 会根据上下文自动决定何时使用选择：

**应该使用选择的时候：**
- 从有限的选项中选择（平台、框架、功能）
- 2-3 个替代方案确认
- 目标用户细分
- 技术栈选择

**不使用选择的时候：**
- 开放性问题（描述你的产品愿景）
- 需要详细解释的问题
- 需要段落长度输入的内容

## 优势

1. **更快的交互**: 输入一个数字比打字快 10 倍
2. **减少错误**: 不会因为拼写或理解偏差导致误解
3. **更好的发现**: 看到"隐藏"选项（比如"Other"）
4. **保持上下文**: 选择被结构化记录，便于后续引用
5. **类似 Claude Code**: 你已经熟悉的交互模式

## 示例对比

### ❌ 传统对话（慢）

```
User: 构建一个基于AI分析的A股短线投资决策Agent

AI: 我需要了解更多信息。这个Agent的目标用户是谁？
主要功能有哪些？使用什么技术栈？

User: 目标用户是散户投资者，主要功能包括舆情分析、
量化数据分析和交易策略推荐，技术栈希望用Python

AI: 明白了。那么关于舆情分析，您希望分析哪些来源？

User: 主要是新闻、社交媒体和研报

AI: 好的。量化数据方面需要哪些指标？

User: 需要价格、成交量、资金流向、技术指标等

... (来回10多轮对话)
```

### ✅ 交互式选择（快）

```
User: 构建一个基于AI分析的A股短线投资决策Agent

AI: 让我快速了解您的需求。

┌─────────────────────────────────────┐
│ 目标用户？                          │
│ 1. 散户投资者                       │
│ 2. 机构投资者                       │
│ 3. 量化交易团队                     │
│ 0. 其他...                          │
└─────────────────────────────────────┘
> 1

┌─────────────────────────────────────┐
│ 核心功能（多选）:                   │
│ 1. 舆情分析                         │
│ 2. 量化数据分析                     │
│ 3. 交易策略推荐                     │
│ 4. 风险控制                         │
│ 5. 回测系统                         │
└─────────────────────────────────────┘
> 1,2,3

┌─────────────────────────────────────┐
│ 舆情来源（多选）:                   │
│ 1. 新闻媒体                         │
│ 2. 社交媒体                         │
│ 3. 研报                             │
│ 4. 公告                             │
└─────────────────────────────────────┘
> 1,2,3

AI: 完美！我来为散户投资者设计一个包含舆情分析、
量化数据和策略推荐的短线决策助手...
```

**对比结果：**
- 传统方式: ~10 轮对话，~5 分钟
- 交互式选择: ~4 次选择，~1 分钟
- **效率提升: 5 倍**
