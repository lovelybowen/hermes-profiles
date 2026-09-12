# 架构文档 CI 流水线模板

面向不同平台的 CI/CD 流水线模板，用于自动化处理基于 Structurizr 的架构文档——验证、图导出、静态站点生成和部署。

所有模板都使用 **Docker 镜像** `structurizr/cli:latest`，以避免 CI runner 依赖 Java 运行时。

## 流水线阶段（跨平台通用）

每条流水线都遵循相同的逻辑顺序：

```
1. validate  →  structurizr-cli validate -w docs/arch/model/system.dsl
2. inspect   →  structurizr-cli inspect -w docs/arch/model/system.dsl
3. export    →  structurizr-cli export -w docs/arch/model/system.dsl -format mermaid -output site/diagrams
4. site      →  structurizr-cli export -w docs/arch/model/system.dsl -format static -output site
5. deploy    →  平台特定的 Pages 或产物发布
```

并非每次触发都会运行所有阶段。PR 通常只运行第 1-2 阶段（验证）。合并到 main 时运行完整流水线。

---

## 1. GitHub Actions

### 流水线 A：PR 验证（仅第 1-2 阶段）

路径：`.github/workflows/validate-architecture.yml`

```yaml
name: 验证架构文档
on:
  pull_request:
    paths:
      - 'docs/arch/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 验证 Structurizr DSL
        uses: docker://structurizr/cli:latest
        with:
          args: validate -w docs/arch/model/system.dsl

      - name: 检查架构漂移
        uses: docker://structurizr/cli:latest
        with:
          args: inspect -w docs/arch/model/system.dsl
```

### 流水线 B：完整部署到 GitHub Pages（第 1-5 阶段）

路径：`.github/workflows/deploy-architecture-site.yml`

```yaml
name: 部署架构文档
on:
  push:
    branches: [main]
    paths:
      - 'docs/arch/**'

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 验证 Structurizr DSL
        uses: docker://structurizr/cli:latest
        with:
          args: validate -w docs/arch/model/system.dsl

      - name: 检查架构漂移
        uses: docker://structurizr/cli:latest
        with:
          args: inspect -w docs/arch/model/system.dsl

      - name: 导出 Mermaid 图
        uses: docker://structurizr/cli:latest
        with:
          args: export -w docs/arch/model/system.dsl -format mermaid -output site/diagrams

      - name: 导出静态站点
        uses: docker://structurizr/cli:latest
        with:
          args: export -w docs/arch/model/system.dsl -format static -output site

      - name: 上传 Pages 产物
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: 部署到 GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 替代方案：Marketplace Action

社区 action `structurizr/structurizr-cli-action` 将 CLI 包装为专用 action 步骤：

```yaml
- name: 使用 marketplace action 验证
  uses: structurizr/structurizr-cli-action@v1
  with:
    args: validate -w docs/arch/model/system.dsl
```

上述基于 Docker 的方法更具可移植性，并可在 ForgeJo 上以相同方式运行。

---

## 2. GitLab CI

路径：`.gitlab-ci.yml`

```yaml
stages:
  - validate
  - export
  - pages

validate-architecture:
  stage: validate
  image:
    name: structurizr/cli:latest
    entrypoint: [""]
  script:
    - /usr/local/structurizr-cli/structurizr.sh validate -w docs/arch/model/system.dsl
    - /usr/local/structurizr-cli/structurizr.sh inspect -w docs/arch/model/system.dsl
  only:
    changes:
      - docs/arch/**/*
  except:
    - main

export-diagrams:
  stage: export
  image:
    name: structurizr/cli:latest
    entrypoint: [""]
  script:
    - /usr/local/structurizr-cli/structurizr.sh export -w docs/arch/model/system.dsl -format mermaid -output public/diagrams
    - /usr/local/structurizr-cli/structurizr.sh export -w docs/arch/model/system.dsl -format static -output public
  artifacts:
    paths:
      - public
  only:
    - main

pages:
  stage: pages
  script:
    - echo "正在将架构文档发布到 GitLab Pages"
  artifacts:
    paths:
      - public
  only:
    - main
  environment: production
```

**说明：**
- 必须使用 `entrypoint: [""]` 覆盖项，才能将 Structurizr CLI 作为命令而不是长时间运行的进程使用
- GitLab Pages 从 `public/` 目录提供服务——导出步骤直接以 `public/` 为目标
- validate 中的 `except: main` 确保它在功能分支而非主分支上运行（与 `only: changes` 存在冗余，但表达更明确）

---

## 3. ForgeJo (Gitea Actions)

ForgeJo 是 Gitea 的分支。Gitea 1.19+ 内置 **Gitea Actions** 作为 CI/CD 解决方案——它是使用 `act`、兼容 GitHub Actions 的 runner。工作流位于 `.gitea/workflows/`，并使用与 GitHub Actions 相同的语法。

### 流水线 A：PR 验证

路径：`.gitea/workflows/validate-architecture.yml`

```yaml
name: 验证架构文档
on:
  pull_request:
    paths:
      - 'docs/arch/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 验证 Structurizr DSL
        uses: docker://structurizr/cli:latest
        with:
          args: validate -w docs/arch/model/system.dsl

      - name: 检查架构漂移
        uses: docker://structurizr/cli:latest
        with:
          args: inspect -w docs/arch/model/system.dsl
```

### 流水线 B：完整部署（基于产物）

路径：`.gitea/workflows/deploy-architecture.yml`

```yaml
name: 构建架构文档
on:
  push:
    branches: [main]
    paths:
      - 'docs/arch/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 验证 Structurizr DSL
        uses: docker://structurizr/cli:latest
        with:
          args: validate -w docs/arch/model/system.dsl

      - name: 导出 Mermaid 图
        uses: docker://structurizr/cli:latest
        with:
          args: export -w docs/arch/model/system.dsl -format mermaid -output site/diagrams

      - name: 导出静态站点
        uses: docker://structurizr/cli:latest
        with:
          args: export -w docs/arch/model/system.dsl -format static -output site

      - name: 上传产物
        uses: actions/upload-artifact@v4
        with:
          name: architecture-docs
          path: site
```

**部署说明：**Gitea/ForgeJo 并非所有版本都内置 Pages 部署（不同于 GitHub Pages 或 GitLab Pages）。托管所生成静态站点的选项：

1. **手动下载产物**——开发人员从 Actions 运行页面下载
2. **外部托管**——增加通过 rsync/scp 部署到 Web 服务器的步骤：
   ```yaml
   - name: 部署到 Web 服务器
     run: |
       rsync -avz --delete site/ user@server:/var/www/architecture/
   ```
3. **Woodpecker CI**——如果 ForgeJo 实例使用 Woodpecker 而不是 Gitea Actions，请参见下方说明

### Woodpecker CI 替代方案

如果 ForgeJo 实例使用 Woodpecker CI（而不是 Gitea Actions），其 schema 不同：

```yaml
# .woodpecker.yml
pipeline:
  validate:
    image: structurizr/cli:latest
    commands:
      - /usr/local/structurizr-cli/structurizr.sh validate -w docs/arch/model/system.dsl
      - /usr/local/structurizr-cli/structurizr.sh inspect -w docs/arch/model/system.dsl
    when:
      path:
        include: [docs/arch/**]

  export:
    image: structurizr/cli:latest
    commands:
      - /usr/local/structurizr-cli/structurizr.sh export -w docs/arch/model/system.dsl -format mermaid -output site/diagrams
      - /usr/local/structurizr-cli/structurizr.sh export -w docs/arch/model/system.dsl -format static -output site
    when:
      branch: main

  deploy:
    image: alpine:latest
    commands:
      - echo "站点已生成到 ./site——通过 rsync、S3 或下载产物进行部署"
    when:
      branch: main
```

---

## 4. 流水线选择指南

| 情况 | 触发方式 | 阶段 | 流水线 |
|---|---|---|---|
| PR 修改架构文档 | `pull_request` | 1-2（validate + inspect） | 简短验证 |
| 合并到 main | `push main` | 1-5（完整流水线） | 完整部署 |
| 临时手动运行 | `workflow_dispatch` | 1-5（完整流水线） | 完整部署 |

---

## 5. 自定义说明

### 路径范围

所有模板都使用 `docs/arch/**` 作为路径过滤器。应根据实际架构目录进行调整：

| 目录约定 | 路径模式 |
|---|---|
| AaC 标准（`docs/arch/`） | `docs/arch/**` |
| ADR + 文档（`docs/adr/`、`docs/`） | 添加多个路径：`['docs/adr/**', 'docs/model/**']` |
| 根级（`model.dsl` 位于项目根目录） | `*.dsl` |
| 包含多个系统的单体仓库 | `services/*/docs/arch/**` |

### PNG/SVG 导出限制

Structurizr CLI 只能导出 Mermaid、PlantUML、DOT 和静态 HTML。渲染 PNG/SVG 需要无头 Chrome + Puppeteer。脚本位于：

https://github.com/structurizr/puppeteer

这会显著增加 CI 复杂度（安装 Chrome、渲染时间）。对于多数 CI 流水线，包含交互式图（Mermaid）的静态 HTML 站点已经足够。

### vNext 迁移

Structurizr CLI 已弃用，推荐使用新的 vNext 命令。vNext 稳定后：
- 二进制名称可能变化（`structurizr.sh` → `structurizr`）
- 参数语法可能变化（`-workspace` → `--workspace`）
- 流水线结构（validate → export → deploy）和 Docker 镜像（`structurizr/cli`）将保持不变

关注 https://docs.structurizr.com/commands 以获取更新。

### 仅由特定文件类型触发

如果只希望在 DSL 或 ADR 文件发生变化时运行（不包括图像或无关文档）：

```yaml
paths:
  - 'docs/arch/model/**/*.dsl'
  - 'docs/arch/adr/**/*.md'
  - 'docs/arch/src/**/*.adoc'
```

---

## 6. 延伸阅读

- Structurizr CLI 安装：https://docs.structurizr.com/cli/installation
- Structurizr CLI 导出：https://docs.structurizr.com/cli/export
- Structurizr 静态站点：https://docs.structurizr.com/static
- GitHub Actions marketplace（Structurizr）：https://github.com/marketplace/actions/structurizr-cli-action
- Gitea Actions 概览：https://docs.gitea.com/usage/actions/overview
- Woodpecker CI：https://woodpecker-ci.org/
