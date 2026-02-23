# SpecForge 阶段管理修复说明

## 问题原因

之前 AI 模型会一次性输出所有阶段的内容（Discovery → Definition → Ideation → Delivery），导致：
1. `/status` 命令显示的状态与 AI 输出不一致
2. 用户无法逐步确认每个阶段
3. 工作流状态没有正确推进

## 修复内容

### 1. 强化系统提示词

在 `SYSTEM_PROMPT` 中添加了明确的工作流规则：

```markdown
**CRITICAL WORKFLOW RULES:**

1. **Stay in the current stage**: Only work on the objectives of the current stage.
2. **Complete one stage at a time**: Finish ALL objectives before mentioning the next stage.
3. **Always get explicit confirmation**: After completing a stage, you MUST present a @CHOICE:confirm and WAIT for user confirmation.
4. **Do NOT auto-advance**: Never assume the user is satisfied. Always ask for confirmation.
```

### 2. 每个阶段必须要求确认

每个阶段完成时，AI 必须输出：

```markdown
@CHOICE:confirm
TITLE: Discovery Stage Complete - Confirm to proceed?
1. Yes, personas and competitors look correct, proceed to Definition
2. No, I need to adjust something
@END_CHOICE
```

### 3. 新增手动控制命令

| 命令 | 功能 |
|------|------|
| `/status` | 查看当前阶段和进度 |
| `/next` | 推进到下一阶段（满足条件时） |
| `/goto <stage>` | 手动跳到指定阶段 |
| `confirm` | 确认当前阶段产物 |

## 使用方式

### 推荐流程：逐步确认

```
用户: 构建一个A股短线投资决策Agent

AI: [Discovery 阶段 - 输出用户画像和竞品分析]

@CHOICE:confirm
TITLE: Discovery Stage Complete - Confirm to proceed?
1. Yes, personas and competitors look correct, proceed to Definition
2. No, I need to adjust something
@END_CHOICE

[用户选择 1]

AI: [Definition 阶段 - 输出产品愿景和功能清单]

@CHOICE:confirm
TITLE: Definition Stage Complete - Confirm MVP scope?
1. Yes, this MVP scope is correct, proceed to Ideation
2. No, I need to adjust features or priorities
@END_CHOICE

[用户选择 1]

AI: [Ideation 阶段 - 输出技术方案]

@CHOICE:confirm
TITLE: Ideation Stage Complete - Confirm technical approach?
1. Yes, this technical approach works, proceed to Delivery
2. No, I need to discuss alternatives
@END_CHOICE

[用户选择 1]

AI: [Delivery 阶段 - 输出详细规格]

@CHOICE:confirm
TITLE: Delivery Stage Complete - Ready for export?
1. Yes, specifications look good, ready to export
2. No, I need to refine some specifications
@END_CHOICE
```

### 调试流程：手动跳转

如果 AI 一次性输出了所有内容，你可以手动设置正确阶段：

```
> /goto definition
> /goto ideation
> /goto delivery
```

## 验证修复

使用新版本 SpecForge 时，AI 应该：

1. ✅ 只在当前阶段工作
2. ✅ 完成当前阶段后输出 @CHOICE:confirm
3. ✅ 等待用户选择 "Yes" 后才进入下一阶段
4. ✅ 用户选择 "No" 时询问需要调整什么

## 示例对比

### 修复前（错误）

```
AI: 完成了 Discovery、Definition、 Ideation 和 Delivery 所有阶段。
    现在可以导出 PRD 和 Tech Spec 了。

> /status
Current Stage: DISCOVERY  ← 状态不一致！
```

### 修复后（正确）

```
AI: [完成 Discovery 阶段，输出用户画像和竞品分析]

@CHOICE:confirm
TITLE: Discovery Stage Complete - Confirm to proceed?
1. Yes, proceed to Definition
2. No, need adjustments
@END_CHOICE

[用户选择 1]

> /status
Current Stage: DEFINITION  ← 状态已同步！
```

## 向后兼容

- 旧的会话文件仍然可以加载
- 新命令 `/next`、`/goto` 可选使用
- AI 会自动遵循新的工作流规则
