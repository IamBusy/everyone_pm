# SpecForge 键盘导航交互功能

SpecForge 现在支持真正的键盘导航选择，使用 `questionary` 库实现，体验类似 Claude Code。

## 交互方式

### 单选 (使用箭头键)

```
┌─────────────────────────────────────────────┐
│ What type of product are you building?      │
│                                             │
│   ➤  Mobile app (iOS/Android)              │
│      Web application                        │
│      Desktop software                       │
│      API/Backend service                    │
│      Other (type custom input)...           │
│                                             │
│   Use arrow keys, Enter to select          │
└─────────────────────────────────────────────┘
```

**操作方式：**
- ↑↓ 箭头键：在选项间上下移动
- Enter：确认选择当前高亮的选项
- Esc：取消

### 多选 (使用空格键)

```
┌─────────────────────────────────────────────┐
│ Select all features you need:               │
│                                             │
│   ➤  User authentication                   │
│      Real-time updates                     │
│      File uploads                          │
│      Payment processing                    │
│                                             │
│   Use arrows, Space to select, Enter       │
└─────────────────────────────────────────────┘
```

**操作方式：**
- ↑↓ 箭头键：在选项间上下移动
- Space：选中/取消选中当前选项（显示 ✓）
- Enter：确认所有已选项
- Esc：取消

选中状态显示：
```
☑ User authentication    ← 已选中
☐ Real-time updates     ← 未选中
☑ File uploads          ← 已选中
```

### 确认选择

```
┌─────────────────────────────────────────────┐
│ Focus on B2B or B2C?                         │
│                                             │
│   ➤  B2B (Business-to-Business)            │
│      B2C (Business-to-Consumer)             │
│                                             │
│   Use arrow keys, Enter to select          │
└─────────────────────────────────────────────┘
```

## 快捷键参考

| 按键 | 单选 | 多选 | 说明 |
|------|------|------|------|
| ↑↓ | ✓ | ✓ | 在选项间移动 |
| Space | - | ✓ | 选中/取消选中 |
| Enter | ✓ | ✓ | 确认选择 |
| Esc | ✓ | ✓ | 取消操作 |
| Ctrl+C | ✓ | ✓ | 中断程序 |

## 完整交互流程示例

### Discovery 阶段

```
AI: 让我了解您的产品定位。

┌─────────────────────────────────────────────┐
│ 这个Agent主要服务哪类用户优先（MVP）？       │
│                                             │
│   ➤  个人短线（盘后复盘+明日计划，追求省时） │
│      半职业/职业短线（更强调证据链、可回测） │
│      先做两者通用（风险是MVP变大、交付慢）   │
│      Other (type custom input)...           │
│                                             │
│   Use arrow keys, Enter to select          │
└─────────────────────────────────────────────┘
```

**操作：**
1. 按 ↓ 2 次，移动到"半职业/职业短线"
2. 按 Enter 确认

```
AI: 好的，面向职业短线交易者。

┌─────────────────────────────────────────────┐
│ 核心功能需求（多选）:                        │
│                                             │
│   ➤  舆情分析（新闻、社交媒体、研报）        │
│      量化数据分析（价格、量能、资金流）       │
│      交易策略推荐（明日前瞻）                │
│      风险控制（仓位管理、止损建议）          │
│      回测系统（验证策略有效性）              │
│                                             │
│   Use arrows, Space to select, Enter       │
└─────────────────────────────────────────────┘
```

**操作：**
1. 第一个选项已高亮，按 Space 选中（显示 ✓）
2. 按 ↓ 移到"量化数据分析"，按 Space 选中
3. 按 ↓ 移到"交易策略推荐"，按 Space 选中
4. 按 ↓ 移到"风险控制"，按 Space 选中
5. 按 Enter 确认

```
选中结果：
☑ 舆情分析
☑ 量化数据分析
☑ 交易策略推荐
☑ 风险控制

AI: 明确了，MVP将包含这4个核心模块...
```

## 与其他工具的对比

### vs 传统 CLI 工具

| 特性 | 传统工具 | SpecForge |
|------|----------|-----------|
| 输入方式 | 输入数字或文字 | 箭头键选择 |
| 错误风险 | 高（拼写错误） | 无（无法选错） |
| 速度 | 慢（需要完整输入） | 快（3-5秒完成） |
| 发现选项 | 需要听AI说完 | 直接看到所有选项 |

### vs Claude Code

| 特性 | Claude Code | SpecForge |
|------|-------------|-----------|
| 箭头导航 | ✓ | ✓ |
| 多选支持 | ✓ | ✓ |
| 自定义输入 | ✓ | ✓ |
| 上下文 | 编程 | 产品设计 |

## 高级功能

### 自定义输入选项

如果所有预设选项都不合适，选择 "Other..." 会进入输入模式：

```
┌─────────────────────────────────────────────┐
│ What type of product?                       │
│                                             │
│      Mobile app                             │
│      Web application                        │
│   ➤  Other (type custom input)...          │
│                                             │
│   Use arrow keys, Enter to select          │
└─────────────────────────────────────────────┘
```

选择 "Other..." 后：
```
Enter your custom input: > Browser extension for note-taking
```

### 取消操作

按 `Esc` 或 `Ctrl+C` 可以取消当前选择：
- `Esc`: 返回空字符串（跳过此选择）
- `Ctrl+C`: 可能会中断整个程序（慎用）

## 技术实现

SpecForge 使用 [questionary](https://questionary.readthedocs.io/) 库实现：

```python
import questionary

result = questionary.select(
    "Choose an option",
    choices=[
        "Option 1",
        "Option 2",
        "Option 3",
    ],
).ask()
```

**优势：**
- 跨平台支持（Linux、macOS、Windows）
- 支持各种终端
- 美观的默认样式
- 可扩展定制

## 最佳实践

### 为用户设计选择时

1. **限制选项数量**: 3-7 个最佳
2. **清晰的标签**: 1-10 个词
3. **逻辑排序**: 最常用的放前面
4. **提供"Other"选项**: 覆盖边缘情况

### 示例：好的选择设计

```
❌ 不好的设计:
选择你的技术栈:
1. Python
2. JavaScript
3. Java
4. C++
5. Go
6. Rust
7. Ruby
8. PHP
9. Swift
10. Kotlin
... (20+ 选项)

✅ 好的设计:
选择你的技术栈:
1. Python (适合数据分析、AI)
2. JavaScript/TypeScript (Web 应用)
3. Go (高并发后端)
4. Other...
```

### 使用场景建议

**✅ 适合使用选择：**
- 平台选择（iOS/Android/Web）
- 功能优先级排序
- 目标用户细分
- 技术栈选择
- Yes/No 确认

**❌ 不适合使用选择：**
- 产品名称/品牌名
- 具体的数值设置
- 需要解释的概念
- 自由文本描述
