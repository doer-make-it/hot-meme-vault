# 热梗素材库 (hot-meme-vault)

> 把零散的互联网热梗/表情包/段子，变成可检索、可复用的素材库。

面向内容创作者（短视频、公众号、混剪、科普等）的素材管理工作流。**采集 → 命名入库 → 打标 → 检索 → 复用**，五步闭环，越用越厚越好找。

## 适合谁

- 做短视频/混剪，常需要按情绪或场景找素材的人
- 表情包存了一堆但永远找不到那张的人
- 想把"刷到就存"的习惯变成结构化素材库的人

## 核心特性

- **多源采集**：抖音 / B站 / 微博 / 小红书 / Reddit / 即刻，统一入库
- **标准化命名**：`YYYYMMDD_平台_梗名_序号.ext`，永不重名、可排序
- **六维标签**：情绪 / 场景 / 类型 / 来源 / 时间 / 热度，组合检索
- **本地索引**：Python 脚本扫描素材目录生成 `index.json`，离线可搜
- **导出复用**：检索结果一键导出路径清单，喂给剪辑或脚本生成

## 快速开始

```bash
# 1. 建素材目录
mkdir -p vault/{images,videos,texts}

# 2. 把素材按命名规范放进去（见 references/naming.md）

# 3. 建索引
python scripts/index_vault.py vault/

# 4. 检索
python scripts/search.py --tags "情绪:无语,场景:职场" vault/
```

## 目录结构

```
hot-meme-vault/
├── SKILL.md                 # 工作流主文档（WorkBuddy skill 入口）
├── README.md                # 本文件
├── LICENSE                  # MIT
├── references/
│   ├── sources.md           # 采集源清单 + 各源采集方式
│   ├── taxonomy.md          # 六维标签体系
│   └── naming.md            # 命名规范
└── scripts/
    ├── index_vault.py       # 扫描目录生成 index.json
    └── search.py            # 按标签/关键词检索
```

## 为什么不用 Eagle / Billfish / Notion

- 那些工具强，但要钱或要登录云
- 本方案零依赖、纯本地、脚本可改、索引是可读 JSON
- 适合"就想用文件系统管素材、偶尔脚本检索一下"的人

## 许可证

MIT，自用为主，顺便开源。
