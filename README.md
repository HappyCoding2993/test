# Codex 功能测试仓库

这是一个用于快速验证当前 Codex 常见能力的最小代码仓，覆盖：

- 代码生成与重构
- 命令行运行与参数解析
- 单元测试执行
- JSON 持久化读写

## 项目结构

- `app/task_manager.py`：核心逻辑（任务增删改查、JSON 存储）
- `app/cli.py`：命令行入口
- `tests/test_task_manager.py`：核心单元测试

## OpenSpec（先定义需求与范围）

在动手改代码前，请先阅读 `openspec/` 下文档：

- `openspec/spec.md`：需求定义与验收标准
- `openspec/change_scope.md`：本次变更范围（In/Out Scope）

建议先评审 OpenSpec，再执行下述快速开始步骤。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m app.cli add "验证 Codex 能力"
python -m app.cli list
```

## 可用于测试 Codex 的示例任务

1. 新增 `due_date` 字段并更新测试
2. 增加 `done --id` 命令并保证数据持久化
3. 将存储从 JSON 替换为 SQLite
4. 增加 GitHub Actions 测试流程

