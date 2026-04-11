# OpenSpec: 变更范围定义

## In Scope

- 初始化 Python 项目结构与包目录。
- 实现 `TaskManager` 核心能力：add/list/complete/delete。
- 增加 CLI 子命令：`add` / `list` / `done --id` / `delete --id`。
- 增加 pytest 测试：新增、完成持久化、删除。
- 增加 `README.md`、`.gitignore`、`requirements.txt`。
- 增加 OpenSpec 文档用于需求与范围声明。

## Out of Scope

- Web UI 或前端页面。
- 多用户协作与鉴权。
- 远程数据库、云存储、消息队列。
- 完整 CI/CD 与发布流程。
- 复杂任务属性（优先级、标签、截止时间）默认不在首版。

## 变更约束

- 优先保持最小可运行实现，避免过度设计。
- 每个新增能力应能通过测试验证。
- 为后续扩展预留明确入口（模型字段、存储层、命令行子命令）。

