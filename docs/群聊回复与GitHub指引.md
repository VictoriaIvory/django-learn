# 群聊回复 & GitHub 指引

> 对应 `README.md` 第 6 节的两项待办：**回复组长**、**GitHub 上传进度**。

---

## 一、先回复组长（10 分钟，别拖）

组长原话是「请回复收到」，并要求把 **GitHub 账号 id** 报给他。可以直接发：

```
收到。这几项我在推进：
1. Linux：还在评估，我这台是联想拯救者 Y7000P，新硬件，先做启动盘试运行再决定是否双系统，不冒险动现有系统。
2. DeepSeek / agent：还没接入，这周内申请。
3. conda：目前用的是 venv 虚拟环境，正在补 conda，两种都会。
4. git：已装好，Django 项目正在往 GitHub 推，推到后把仓库链接发群里。

Django 这边已经跑通了一个投票系统的练习项目：
本地能启动，5 个自动化测试全过，覆盖 MVT、路由、模板、ORM、admin。
这周我会把它扩展成一个自己想做的小应用并优化前端，再部署上线。

GitHub: https://github.com/VictoriaIvory
```

**为什么这样说**：组长关心的不是你「都做完了」，而是你有没有在动、卡在哪、什么时候能交。把「已完成 / 进行中 / 下一步」说清楚，比一句「收到了」有用得多。

---

## 二、GitHub 账号

| 项目 | 值 |
| --- | --- |
| 用户名 | `VictoriaIvory` |
| 主页 | <https://github.com/VictoriaIvory> |
| 提交邮箱 | `299710516+VictoriaIvory@users.noreply.github.com` |

> **为什么用 noreply 邮箱而不是 QQ 邮箱**
> 提交记录里的邮箱对全世界可见。用 noreply 地址，GitHub 一样会正确归到你账号名下，
> 但别人看不到你的 QQ 号。这是 GitHub 官方推荐做法，设置位置：
> **Settings → Emails → Keep my email addresses private**，
> 下方会直接给出你那串专属 noreply 地址。

---

## 三、本机已经做好的配置

```powershell
# Git 便携版位置（免管理员安装）
C:\Users\Victoria\PortableGit\cmd\git.exe

# 已写入用户 PATH，新开的终端直接可用
git --version        # git version 2.56.0.windows.4

# 身份配置
git config --global user.name  "ChenChenghong"
git config --global user.email "299710516+VictoriaIvory@users.noreply.github.com"

# Windows 下两个必设项
git config --global core.autocrlf true   # 换行符自动转换，避免跨系统乱码
git config --global core.quotepath false # 中文文件名正常显示，不显示成 \344\275\240
```

---

## 四、把项目推上 GitHub 的完整流程

### 4.1 建远程仓库

打开 <https://github.com/new>：

| 字段 | 填什么 |
| --- | --- |
| Repository name | `django-learn` |
| Description | Django 5.2 投票系统练习项目 |
| 可见性 | **Public** |
| Add a README / .gitignore / license | **全部不要勾** |

> **为什么不能勾**：勾了会自动生成提交记录，和你本地历史冲突，push 会被拒绝
> （报 `rejected — fetch first`）。空仓库才是对的。

### 4.2 关联远程并推送

```powershell
cd D:\Code\python\django-learn
git remote add origin https://github.com/VictoriaIvory/django-learn.git
git push -u origin main
```

第一次 push 会弹出浏览器让你登录 GitHub 并点 **Authorize**，
授权信息由 Git Credential Manager 存进 Windows 凭据管理器，之后不用再登。

### 4.3 日常提交（以后每次改完都这样）

```powershell
git status                    # 看改了哪些文件
git add -A                    # 全部加入暂存区
git commit -m "说明这次改了什么"
git push                      # 推到 GitHub
```

---

## 五、常见报错速查

| 报错 | 原因 | 解决 |
| --- | --- | --- |
| `rejected — fetch first` | 远程仓库不是空的（勾了 README） | 删掉仓库重回，或 `git pull --rebase origin main` |
| `GH007: push would publish a private email` | 用了被 GitHub 设为私有的邮箱 | 改用 noreply 地址：`git commit --amend --reset-author` |
| `fatal: not a git repository` | 不在项目目录 | `cd D:\Code\python\django-learn` |
| `src refspec main does not match any` | 还没提交过 | 先 `git add -A` + `git commit` |
| `Permission denied (publickey)` | 用了 SSH 但没配密钥 | 改用 HTTPS 地址（`https://...`，别用 `git@...`） |
| 中文文件名显示成 `\344\275\240` | 未设 quotepath | `git config --global core.quotepath false` |
| 启动了却报「缺少 DJANGO_SECRET_KEY」 | 没建 `.env` | `Copy-Item .env.example .env`，再填密钥 |

---

## 六、检查清单

- [x] 安装 Git
- [x] 配置用户名 / 邮箱
- [x] `git init` + 确认 `.env`、`venv/`、`db.sqlite3` 未被跟踪
- [ ] 创建远程仓库 `django-learn`
- [ ] 首次 `git push`
- [ ] 把仓库链接发到群里
