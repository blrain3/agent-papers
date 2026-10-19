# agent-papers 第一批离线修复维护报告（MAINTENANCE-BATCH1）

## 一、基线与分支

- 基线提交：`a1f027a94797803209055cbcc727c6a43bb9ce34`（2026-09-16，"Initial commit: 48 arXiv-verified papers on LLM agents and agent systems"）
- 工作分支：`maint/offline-batch1`
- HEAD 提交：`17dee5c3d6238b089f074f5844e2e786d51db03b`（父提交即基线 `a1f027a`）
- 执行者：OpenCode（原 Codex 因限额未开始，未对主分支产生任何改动）
- 未执行：未 push、未开 PR、无真实联网请求、未改动 `gen_readme.py` 字节、未删除人工选文能力

## 二、改动清单（仅授权文件）

| 文件 | 变更要点 |
|------|----------|
| `sources/papers-source.yml` | **新增** 统一人工选文源：48 篇条目，每条 `id`、`expected_title`（规范标题，已知 LaTeX/标点/前缀差异由 `paper_validation.TITLE_ALIASES` 逐 ID 显式处理）、`topics`（仅主线）、`related` 顺序。主线 13 篇 + 关联 35 篇 = 48 篇，顺序与原 `CANDICATES` 一致，保证缓存/生成顺序与原 `papers.yml`/`verified-metadata.json` 字节一致。 |
| `paper_validation.py` | 新增 `SOURCE_CANDIDATES`、`_resolve_source_path()`、`SOURCE_PATH`、`load_source()`、`candidates_from_source()`、`structure_from_source()`，供两脚本复用同一份源，避免循环导入；源路径沿多个候选回退，兼容把脚本拷贝到临时目录运行的情形。 |
| `verify_papers.py` | `CANDIDATES = candidates_from_source()`（由源生成，不再硬编码）；新增 `main(offline=False)` 与 `main_offline()`：`--offline` 只读现有缓存做 `validate_record` 校验，**不发任何网络请求**，输出 `VERIFIED (offline)` / `UNVERIFIED (offline)`，失败不改写旧缓存；网络模式语义不变，输出 `VERIFIED` / `FAIL` / `UNVERIFIED`，网络类异常明确标注 `UNVERIFIED`，不得静默当成功；刷新失败时旧缓存字节不变（原子 `atomic_write`，先临时文件后替换）。 |
| `build_papers.py` | `STRUCTURE = structure_from_source()`（由源生成）；移除对 `verify_papers.CANDICATES` 的导入；期望标题由 `candidates_from_source()` 产出；生成前在临时位置完整产出 `papers.yml`，比较通过才写入，任何异常不落半成品（原子替换，失败后旧文件字节不变）。 |
| `check_links.py` | 本地最小分叉（保留上游 MIT 头注释并追加“Local modification”声明）：`verify=True`、`TIMEOUT=15`、`ATTEMPTS=3`（即最多 2 次重试，等待 1/2 秒）、405/501 回退 GET；区分 `FAIL`（出口码 1，404/410 确认后）与 `UNVERIFIED`（出口码 2，TLS/超时/证书/连接/5xx/访问受限等不算失败退出，但输出明确清单）。 |
| `NOTICE.md` | 补基线日期 `2026-09-16`、`gen_readme.py` 保持逐字节一致、`check_links.py` 自基线起本地修改及差异范围；**未删除上游 MIT 署名与许可**。 |
| `tests/test_offline.py` | **新增** pytest/标准库风格离线测试，共 41 条（原 36 条 + 新增 5 条），覆盖合法全集通过、重复 ID 拒绝、ID 错位拒绝、`title_match=false` 拒绝、同前缀错标题拒绝、别名通过、含 `': '` 与特殊字符标题 YAML 往返、暂存替换失败后旧文件字节不变、生成可重现（两次生成字节相同）、`--offline` 只读缓存及损坏/缺失缓存处理。 |
| `atomic_output.py` / `safe_readme.py` / `requirements.txt` | 新增（原已存在于工作树，本轮纳入提交）：原子写入、安全 README 发布、运行时依赖（PyYAML、requests）。 |
| `README.md` / `papers.yml` / `README.md.template` | 由重新生成产生，且与当前内容**字节一致**（本轮无内容变更）。 |
| `gen_readme.py` | **未改动**；`git diff master -- gen_readme.py` 为空，与上游逐字节一致。 |

## 三、测试清单与结果

运行方式（因系统环境缺少 PyYAML，在仓库内建立 `.venv-tmp`，非全局 `pip install`）：

```sh
python3 -m venv .venv-tmp
.venv-tmp/bin/python -m pip install -r requirements.txt
.venv-tmp/bin/python -m unittest discover -s tests
```

结果：

- **41 条测试全部通过**（`Ran 41 tests ... OK`），其中新增：
  - `SourceUnificationTests.test_source_counts_and_grouping_match_papers_yml`：48 篇/唯一 ID/13 主线/35 关联/分组与 `papers.yml` 一致。
  - `OfflineTests.test_offline_valid_cache_all_verified`：合法缓存全部 `VERIFIED (offline)`，退出码 0。
  - `OfflineTests.test_offline_corrupt_cache_rejected_and_preserved`：损坏缓存拒绝、退出码非 0、旧缓存字节不变。
  - `OfflineTests.test_offline_missing_cache_unverified`：缺失缓存 `UNVERIFIED`，退出码 2。
  - `ReproducibilityTests.test_build_twice_identical_bytes`：两次 `build_papers.py` 生成字节完全相同。
- 所有子进程均阻止真实网络；依赖注入式伪响应，未做真实联网。
- 反例均被拒绝：重复 ID、返回 link 与请求 ID 不一致、`title_match=false`/缺失、year 非 4 位数字、同前缀不同研究内容的错标题、表外标题差异。

## 四、生成产物 diff 结论

```sh
.venv-tmp/bin/python3 build_papers.py && .venv-tmp/bin/python3 gen_readme.py > /tmp/README.gen
diff /tmp/README.gen README.md   # 无差异
```

- `papers.yml` 重新生成后与现有内容字节一致。
- `README.md` 通过 `gen_readme.py` 重新生成后与现有 `README.md` **字节完全一致**。
- `verified-metadata.json` 未被本轮刷新（离线修复），内容未变。
- 连续两次生成 `papers.yml` 字节相同（可重现）。

## 五、未做事项（明确禁止或留至后续另行批准）

- 未 push 任何分支；
- 未开 PR；
- 未进行真实联网请求（verify/check 的原逻辑保留，未新增网络调用路径）；
- 未真实刷新 `verified-metadata.json` 缓存（保持离线，仅读现有缓存）；
- 未改动 `gen_readme.py` 字节；
- 未删除人工选文能力（`sources/papers-source.yml` 由人工维护）；
- 未做 CI 接入或定时任务。

## 六、回滚方式

本批次所有改动已提交于分支 `maint/offline-batch1`（HEAD `17dee5c`，父提交为基线 `a1f027a`）。如需回滚至基线，在仓库根执行：

```sh
git checkout master
```

（或 `git reset --hard a1f027a94797803209055cbcc727c6a43bb9ce34` 仅回退本分支提交，不动 `master`。）

工作树中若仍有未提交杂项（如 `__pycache__/`、`.venv-tmp/`），可手动删除；它们未纳入提交。
