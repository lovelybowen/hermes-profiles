# 完整示例：检测可编辑开发分支

演示“检查依赖来源”模式（阶段 1，步骤 5d）。

## 症状

后台工作者每次调用都会崩溃：

```
Traceback ...
  File "core/session.py", line 456, in _create_node
    cursor.execute("""INSERT INTO thought_nodes
    (id, content, node_type, timestamp, confidence, source_file, ...)
sqlite3.OperationalError: table thought_nodes has no column named confidence
```

## 调查路径

1. **阅读堆栈跟踪：**错误发生在第三方库 `core/session.py` 的第 456 行，它试图插入数据库中不存在的 `confidence` 列。

2. **检查模式：**`sqlite3 brain.db ".schema thought_nodes"` 确认实际表中没有 `confidence` 列。模式包含 `id, content, node_type, timestamp, source_file, decayed, ...`，但不包含 `confidence`。

3. **检查来源：**`python3 -c "import core.session; print(core.session.__file__)"` 显示库从 `/private/tmp/some-fork/core/session.py` 加载，而非从 site-packages 加载。

4. **检查依赖来源：**`pip show cashew-brain` 显示：
   - `Editable project location: /private/tmp/some-fork`
   - `Version: 1.0.0`
   - 这是临时目录中的 `pip install -e` 开发副本。

5. **与上游比较：**`pip index versions <package>` 显示 PyPI 上有较新版本。安装的开发副本较旧且含有未合并变更。

## 修复

最初的直觉是修改开发副本中的迁移代码，将其视为代码缺陷。正确判断是开发副本不应存在于此。修复方式如下：

```bash
pip uninstall <package> -y
pip install <package>          # install from PyPI
python3 -c "import <module>; print(<module>.__file__)"
# → site-packages/<module>/  ✓ 生产路径
```

切换到生产版本后，INSERT 不再引用 `confidence`，开发分支的模式漂移消失。

## 关键教训

开发分支在 INSERT 语句中增加了 `confidence` 列，但没有编写对应的 `ALTER TABLE ADD COLUMN` 迁移。这是未维护分支产生的典型模式漂移。症状看似代码缺陷，根因却是依赖管理，即运行了错误版本的库。

## 验证命令

```bash
# 检查安装来源
pip show <package>

# 检查导入路径
python3 -c "import <module>; print(<module>.__file__)"

# 检查 PyPI 以作比较
pip index versions <package>

# 检查数据库模式是否漂移
sqlite3 <db_path> ".schema <table_name>"
```
