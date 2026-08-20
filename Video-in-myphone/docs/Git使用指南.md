# Git 使用指南

> 面向初学者的实用 Git 手册，涵盖日常开发全流程，以及 AI 辅助编程时的版本管理最佳实践。

---

## 一、核心概念

| 概念 | 说明 |
|------|------|
| **仓库 (Repository)** | 项目的根目录，包含 `.git` 文件夹，记录所有版本历史 |
| **提交 (Commit)** | 一次代码快照，相当于一个备份点，有唯一 ID |
| **暂存区 (Staging)** | `git add` 后文件进入暂存区，准备提交 |
| **分支 (Branch)** | 独立的开发线，默认是 `main`，可以新建分支实验功能 |
| **HEAD** | 当前所在的版本指针 |
| **远程仓库 (Remote)** | GitHub/Gitee 等云端仓库，`origin` 是默认别名 |

---

## 二、初始化与配置

```bash
# 初始化仓库（在项目目录下执行）
git init

# 配置用户名和邮箱（第一次使用 Git 时配置，全局生效）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 查看配置
git config --list
```

---

## 三、日常操作速查

### 3.1 查看状态

```bash
git status          # 查看当前文件状态（哪些改了、哪些没提交）
git diff            # 查看具体改了什么内容（未暂存的修改）
git diff --staged   # 查看已暂存的修改
```

### 3.2 提交代码

```bash
git add .               # 把所有修改加入暂存区
git add 文件名.py        # 只添加指定文件
git commit -m "提交说明"  # 提交，引号内写这次改了什么
```

**提交说明写法建议**：
- `feat: 新增xxx功能`
- `fix: 修复xxxbug`
- `refactor: 重构xxx代码`
- `docs: 更新文档`
- `chore: 杂项（配置、依赖等）`

### 3.3 查看历史

```bash
git log                  # 完整提交历史
git log --oneline        # 简洁版，一行一条
git log --oneline --graph # 带分支图形
git show 版本号           # 查看某次提交的具体改动
```

### 3.4 撤销与回退

```bash
git checkout -- 文件名     # 撤销单个文件的修改（恢复到上次提交状态）
git restore 文件名         # 同上，Git 2.23+ 推荐写法
git reset HEAD 文件名      # 把文件从暂存区撤回来（不删修改）
git reset --hard 版本号     # 回退到指定版本（会丢失之后的修改，谨慎！）
git reset --hard HEAD~1    # 回退到上一个版本
```

> ⚠️ `git reset --hard` 会永久丢弃修改，执行前确认已备份或已提交。

### 3.5 分支操作

```bash
git branch                # 查看所有分支
git branch 新分支名         # 创建分支
git checkout 分支名         # 切换分支
git switch 分支名           # 同上，Git 2.23+ 推荐
git checkout -b 新分支名     # 创建并切换到新分支
git merge 分支名            # 把指定分支合并到当前分支
git branch -d 分支名        # 删除分支
```

### 3.6 远程仓库（GitHub）

```bash
git remote add origin 仓库地址   # 关联远程仓库
git remote -v                    # 查看远程仓库地址
git push -u origin main          # 第一次推送（-u 记录上游分支）
git push                         # 之后推送
git pull                         # 拉取远程最新代码并合并
git clone 仓库地址                # 克隆远程仓库到本地
```

---

## 四、AI 辅助编程的 Git 工作流

### 4.1 为什么 AI 修改前要备份？

AI 生成的代码可能：
- 引入 bug 或破坏现有功能
- 修改了你不想改的文件
- 输出不符合预期，需要回退
- 多次迭代后想对比哪个版本更好

**每次让 AI 大改代码前，先 commit 一个稳定版本，改坏了随时回退。**

### 4.2 标准工作流

```
当前代码稳定 → git commit 备份 → 让 AI 修改 → 测试 → 满意就 commit → 不满意就 reset 回退
```

具体步骤：

```bash
# 1. 确认当前状态干净
git status

# 2. 提交当前稳定版本
git add .
git commit -m "backup: AI修改前备份"

# 3. 让 AI 修改代码（在对话中发送修改需求）

# 4. 修改完成后测试
#    满意 → git add . && git commit -m "feat: AI完成xxx修改"
#    不满意 → git reset --hard HEAD  （回退到备份前）
```

### 4.3 用分支隔离 AI 实验（推荐）

大改时新建分支，不影响主分支：

```bash
# 新建实验分支并切换
git checkout -b ai-experiment

# 让 AI 随便改，改完测试
# 满意 → 合并回主分支
git checkout main
git merge ai-experiment
git branch -d ai-experiment

# 不满意 → 直接删掉分支，主分支毫发无损
git checkout main
git branch -D ai-experiment
```

---

## 五、AI 修改代码前的通用提示词模板

### 5.1 基础版（直接用）

```
我已经用 git commit 备份了当前代码。请帮我修改以下内容：
【描述你的需求】

要求：
1. 只修改需要改的文件，不要动无关代码
2. 保持现有代码风格和命名规范
3. 修改完成后列出改动了哪些文件、每个文件改了什么
4. 如果有潜在风险或需要注意的地方，请说明
```

### 5.2 完整版（大改时用）

```
当前项目已 git 提交备份，版本号：【填 git log --oneline 看到的版本号】

项目背景：
【简要说明项目是做什么的、用了什么技术栈】

需要实现的功能/修改：
【详细描述需求】

现有相关代码：
【粘贴相关文件代码，或说明在哪个文件的哪个函数】

要求：
1. 保持项目整体架构不变，只在需要的地方修改
2. 新增的函数/变量命名要清晰，加必要注释
3. 不要引入新的依赖库，除非必须并说明理由
4. 修改后给出完整的文件内容（不要只给片段）
5. 列出所有改动文件清单和改动摘要
6. 说明如何测试修改是否生效
```

### 5.3 让 AI 自己检查 Git 状态（高级）

```
在修改代码前，请先执行 git status 和 git log --oneline -5，
确认当前工作区状态。如果有未提交的修改，先提醒我提交备份。
确认干净后再开始修改。
```

> 注意：此提示词需要 AI 有命令行执行权限（如当前的 Agent 模式），普通对话 AI 无法执行命令。

---

## 六、常见问题

### Q: 我忘了提交，AI 把代码改坏了怎么办？
A: 如果还没关闭编辑器，试试 `Ctrl+Z` 撤销。如果已经保存了，看编辑器的"本地历史记录"（VS Code 有 Timeline 功能）。以后养成 AI 改之前先 commit 的习惯。

### Q: commit 说明写错了能改吗？
A: 可以，`git commit --amend -m "新说明"` 可以修改最近一次提交的说明。（已经 push 到远程的不建议改）

### Q: 不小心 commit 了不该传的文件（如 rewind.db）怎么办？
A: 
```bash
git rm --cached rewind.db   # 从 Git 追踪中移除，但不删本地文件
echo "rewind.db" >> .gitignore
git commit -m "chore: 移除数据库文件追踪"
```

### Q: 本地和远程冲突了怎么办？
A: 先 `git pull` 拉取远程代码，Git 会自动合并，冲突的文件会标记 `<<<<<<<` 和 `>>>>>>>`，手动解决后 `git add .` + `git commit`。

---

## 七、最佳实践总结

1. **小步提交**：每次完成一个小功能就 commit，不要攒一大堆再提交
2. **写清楚说明**：commit message 要能看懂改了什么，别写"更新""修改"这种废话
3. **AI 改前必备份**：大改前 commit 或新建分支
4. **主分支保持稳定**：实验性功能在分支上做，没问题再合并
5. **定期 push**：本地 commit 后及时 push 到 GitHub，防止电脑挂了丢代码
6. **.gitignore 要配好**：数据库、缓存、打包产物、个人配置都不要传
