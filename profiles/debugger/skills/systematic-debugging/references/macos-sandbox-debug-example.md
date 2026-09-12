# 完整示例：Apple Books.app 导入管线（macOS）

演示“macOS 应用故障排查”和“猜测之前先研究”模式（阶段 1 的步骤 6a/6b）。

## 症状

将 EPUB 导入 Apple Books 时静默失败，存在三种失败模式：
1. **静默拖放：**文件落入应用后无任何反应。
2. **在 Finder 中双击：**焦点切换到 Books，但导入从未开始。
3. **文件 → 打开对话框：**选择文件后无任何反应。

没有错误对话框，没有崩溃报告，Books 保持打开且可响应。

## 调查路径

### 阶段 1 - 收集证据

**1. 检查数据库（BKLibrary）**

主资料库数据库位于：
```
~/Library/Containers/com.apple.iBooksX/Data/Documents/BKLibrary/BKLibrary-1-091020131601.sqlite
```

`ZBKLIBRARYASSET` 表跟踪所有图书，关键列包括：
- `ZSTATE`：3=本地文件存在，5=仅云端。
- `ZCONTENTTYPE`：1=电子书，5=书店，6=有声书或其他。
- `ZPATH`：BKAgentService 容器中本地文件的完整路径。
- `ZASSETID` / `ZSTOREID`：Apple Store 标识符。

**2. 检查 XPC 服务（BKAgentService）**

文件存储位于：
```
~/Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks/Books/
```

图书以**未压缩的目录包**存储，即目录具有 `.epub` 扩展名，包含 `META-INF/`、`OEBPS/` 和 `mimetype`。Apple Books 在导入时解压 EPUB 并保存原始目录结构。因此标准 EPUB 工具，例如 Calibre，无法直接读取这些存储内容，必须重新压缩文件并将 `mimetype` 作为第一个条目。

**3. 检查导入队列**

```
~/Library/Containers/com.apple.iBooksX/Data/Library/Caches/Inbox/
```

已拖放或打开但尚未处理的文件会出现在此处，文件可能无限期卡住。

**4. 阅读系统日志**

```bash
log show --predicate 'process == "Books"' --last 30m --style compact
```

关键错误：
```
BKResolveAssetForImportOperation: Unable to access url
BKResolveAssetForImportOperation: User cancelled import of cloud asset.
importBookFromURL: BKResolveAssetForImportOperation failed.
```

“User cancelled”消息具有误导性，它是应用对 NSFileCoordinator 声明失败的内部解释，即 Code=3072 “The operation was cancelled”。其可能原因是沙箱权限问题或 XPC 服务状态损坏。

**5. 检查容器迁移遗留物**

BKAgentService 容器中的 `Data.old/` 目录表明 macOS 更新期间发生了失败的沙箱容器迁移：
```
~/Library/Containers/com.apple.BKAgentService/Data.old/
```

其中可能包含旧容器版本遗留的图书文件和 plist，从而产生孤立状态。

### 根因

用户为释放磁盘空间，从 Books 本地存储文件夹中删除了 EPUB 文件。这破坏了跟踪图书元数据的 CoreData 数据库与实际文件存储之间的一致性，导致三层损坏：

1. **数据库不一致：**条目具有 `ZSTATE=3`，表示本地文件存在，但文件已经消失。
2. **容器迁移幽灵：**操作系统更新遗留的 `Data.old/` 保留了孤立文件。
3. **XPC 服务退化：**BKAgentService 重启后只会处理一次导入，随后静默停止。

### 已测试的解决方案

**部分有效的方法：**
- 删除容器，即 `rm -rf ~/Library/Containers/com.apple.iBooksX/` 和 `BKAgentService/`，图书会从 iCloud 重新下载，但导入管线仍然脆弱。
- 完整终止进程，即 Books + BKAgentService + BooksThumbnail，可成功导入一次，随后又发生退化。

**无效的方法：**
- SQL 层面的数据库修复，CoreData 缓存状态会覆盖变更。
- 重置 TCC 权限，即 `tccutil reset All com.apple.iBooksX`，它会移除文件访问提示。
- 仅终止 BKAgentService，XPC 会带着损坏状态重新启动。

**已确认的变通方案：**
- **iPhone iCloud Drive 方案：**将 EPUB 上传到 iCloud Drive，在 iPhone/iPad 的“文件”应用中打开并分享至 Books。它通过 iCloud 同步到 Mac，完全绕过本地导入管线。
- **重置 iCloud Books 数据：**系统设置 → Apple ID → iCloud → 管理储存空间 → Books → 删除所有数据，强制完全重置 iCloud 同步状态。

## Books.app 导入管线

```
用户拖入 EPUB → Powerbox 创建安全作用域书签
  → Books.app 通过 AppleEvent 接收 URL
  → BKResolveAssetForImportOperation 将文件复制到 Caches/Inbox
  → BKAgentService XPC 从 Inbox 中取走文件
  → BKAgentService 将 EPUB 解压到 Books/ 下的目录包
  → BKAgentService 使用元数据更新 Books.plist
  → BKLibrary CoreData 存储记录资产
  → iCloud 同步推送到其他设备
```

### 故障发生位置

1. 沙箱安全作用域书签失败 → “Unable to access url”，即 TCC 问题。
2. BKAgentService XPC 随时间退化 → 静默导入失败。
3. 数据库与文件一致性破坏 → Books 认为存在实际不存在的文件。
4. iCloud 同步状态损坏 → 出现幽灵条目，跨设备同步失败。

### 诊断快速参考

| 检查项 | 命令 |
|-------|---------|
| 应用日志 | `log show --predicate 'process == "Books"' --last 10m` |
| XPC 日志 | `log show --predicate 'process == "com.apple.BKAgentService"' --last 10m` |
| 数据库状态 | `sqlite3 .../BKLibrary-*.sqlite "SELECT ZSTATE,COUNT(*) FROM ZBKLIBRARYASSET GROUP BY ZSTATE;"` |
| 容器大小 | `du -sh ~/Library/Containers/com.apple.iBooksX/` |
| 导入队列 | `ls ~/Library/Containers/com.apple.iBooksX/Data/Library/Caches/Inbox/` |
| 图书文件 | `ls ~/Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks/Books/` |
| 迁移幽灵 | `ls -d ~/Library/Containers/com.apple.BKAgentService/Data.old 2>/dev/null` |
