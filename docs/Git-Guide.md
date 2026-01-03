# Git 实战技巧手册 🛠️

本文档整理了在 Agent 开发过程中常用的 Git 高级技巧，包括大文件处理和规范化提交指南。

---

## Git 大文件处理技巧 (LFS) 🐘

GitHub 对单个文件的大小有限制（普通上传 < 100MB）。如果项目中包含大模型权重 (`.bin`, `.pth`) 或大型数据集 (`.jsonl`, `.csv`)，必须使用 **Git LFS (Large File Storage)**。

### 🚀 快速配置流程

如果你已经安装了 git，通常可以直接使用 LFS。

1.  **初始化 LFS**
    在仓库根目录下运行（每个仓库只需运行一次）：
    ```bash
    git lfs install
    ```

2.  **追踪大文件**
    告诉 Git 哪些文件需要用 LFS 管理。例如，要追踪所有的 `.jsonl` 文件：
    ```bash
    git lfs track "*.jsonl"
    ```
    > ⚠️ **注意**：这会生成一个 `.gitattributes` 文件，**务必**将这个文件也提交到 Git。

3.  **正常提交**
    就像平常一样添加和提交代码，LFS 会自动处理背后的上传逻辑：
    ```bash
    git add .gitattributes
    git add my_large_dataset.jsonl
    git commit -m "chore: 配置 LFS 并添加数据集"
    git push origin main
    ```

### ⚠️ 常见报错处理
如果推送时遇到 `GH001: Large files detected` 错误，说明你试图用普通方式上传了大文件。
**解决办法**：
1.  **撤销上一次 commit**（保留代码修改）：`git reset --soft HEAD~1`
2.  **重新配置 LFS**：`git lfs track "*.你的大文件后缀"`
3.  **重新 add 并 commit**。

---

## Git 提交规范 (Commit Best Practices) 📝

清晰的提交记录是项目的“历史书”。推荐使用业界通用的 **Conventional Commits** 规范。

### 📏 标准格式
```text
<类型>(<范围>): <描述>

<正文> (可选，用于详细解释原因)

```

### 🏷️ 常用类型 (Type)

| 类型 | 含义 | 示例 |
| --- | --- | --- |
| **feat** | 新功能 (Feature) | `feat(client): 适配 Qwen-Max 模型` |
| **fix** | 修复 Bug | `fix(server): 修复天气参数解析错误` |
| **docs** | 文档变更 | `docs: 更新 README 项目索引` |
| **style** | 格式调整 (不影响代码逻辑) | `style: 删除多余空行` |
| **refactor** | 代码重构 | `refactor: 重构工具调用逻辑` |
| **chore** | 构建/工具变动 | `chore: 更新 .gitignore 规则` |

### ✅ 好的提交示例

**示例 1：简单提交**

```bash
git commit -m "docs: 新增 Git 实战技巧文档"

```

**示例 2：带详细说明的提交**

```bash
git commit -m "feat(server): 实现 Mock 模式

无需依赖真实 API Key 即可返回模拟天气数据，
方便本地离线调试 MCP 协议。"

```

### ❌ 坏的提交示例

* `git commit -m "update"` (毫无信息量)
* `git commit -m "fix bug"` (修了什么 bug？)
* `git commit -m "123"` (敷衍了事)

---

## 常用救命命令 🚑

这里列出几个在开发中“后悔药”级别的命令：

* **强制覆盖远程仓库** (慎用，仅限个人项目)：
```bash
git push -f origin main

```


* **撤销最近一次 commit** (保留代码修改，重新提交)：
```bash
git reset --soft HEAD~1

```


* **彻底放弃本地修改** (慎用，会丢失未提交的工作)：
```bash
git checkout .

```


* **修改最近一次 commit 的注释** (写错字时用)：
```bash
git commit --amend -m "新的提交说明"

```
