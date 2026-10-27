# PR #56 code-review 修正 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修掉 PR #56 `/code-review medium` 的 1–7、9、10 項（第 8 項不處理），每項先寫失敗測試。

**Architecture:** 全部在 `scripts/subtitle_ocr.py`（分支 `claude/segmented-ocr`，worktree `D:\development\watch-video-seg`）。鎖判斷、`plan.json` 參數比對、原子寫入、下載、CLI 檢查各自是獨立的小函式，不動 `ocr_range` 與合併邏輯。

**Tech Stack:** Python 3 標準庫、`unittest`（`tests/test_subtitle_ocr.py`，以 `import subtitle_ocr as so` 載入）。

**Spec:** PR #56 的 code-review 發現（使用者 2026-10-27 同意範圍：1–7、9、10）；原 spec `.scratch/segmented-ocr/spec.md`。

## Global Constraints

- 回覆與註解的說明文字用繁體中文；程式識別字維持英文；程式碼註解沿用檔內既有風格（英文、短）。
- 絕不印出或寫入任何 API key。
- 每個 Task 結束時 `python3 -m unittest discover -s tests` 全綠（開始時 254 個）。
- 在 worktree 動手前先 `git branch --show-current`，必須是 `claude/segmented-ocr`；不要碰主工作區 `D:\development\watch-video`。
- 第 8 項（每段重建程序池）不處理。
- Commit 訊息結尾加 `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`；**push 要等使用者說「commit 並 push」**。

## Review Focus

- 兩個程序同時判定同一把鎖過期（A 先接手建了新鎖，B 再 rename）→ B 不能把 A 的新鎖弄掉（Task 1）。
- 舊版 `plan.json` 沒有 `params` 欄位 → 續跑照舊可用，不誤報不符（Task 2）。
- 下載中途失敗留下半截檔 → 下次要重新下載，不能被當成已完成（Task 4）。
- `--segment-min 0` 搭配 `--seg-dir`：不報錯，只警告（Task 3）。
- 鎖檔內容壞掉（空檔）→ 仍視為過期（既有測試，不可退步）。

---

### Task 1: 鎖判斷、接手競態、status（項目 2、3、5）

**Files:**
- Modify: `scripts/subtitle_ocr.py:389-417`（`lock_is_stale`、`claim_segment`）、`:463-485`（`status_report`）
- Test: `tests/test_subtitle_ocr.py`（`Locks`、`Progress`）

**Interfaces:**
- Produces: `lock_is_stale(path, ttl=LOCK_TTL, now=time.time, alive=pid_alive) -> bool`（規則改變，簽名不變）；`status_report(out, seg_dir=None, ttl=LOCK_TTL) -> list[str]`。

規則：壞檔／空檔 → 過期；同一台機器（`host == socket.gethostname()`）→ **只看 pid 是否還活著**（活著就不算過期，不管多舊）；別台機器 → 只看年齡 `now() - time > ttl`。

- [ ] **Step 1: 改寫既有測試並新增失敗測試（`Locks`）**
  - 改 `test_lock_older_than_ttl_is_taken_over`：鎖檔改手寫 `{"pid": 1, "host": "elsewhere", "time": 1000}`，斷言 `claim_segment(d, 0, ttl=60, now=lambda: 1050)` 為 False、`now=lambda: 1100` 為 True。
  - 改 `test_lock_from_another_host_is_only_judged_by_age`：保持原樣即可（確認仍通過）。
  - 新增 `test_old_lock_of_a_live_process_on_this_machine_is_respected`：`so.claim_segment(d, 0, now=lambda: 1000)` 後，`so.claim_segment(d, 0, ttl=60, now=lambda: 10 ** 6, alive=lambda pid: True)` 必為 False。
  - 新增 `test_takeover_never_removes_a_lock_created_in_between`：第一次呼叫 `alive` 時把鎖檔換成活程序的新鎖（`{"pid": os.getpid(), "host": socket.gethostname(), "time": now}`）並回傳 False，之後的呼叫回傳 True；斷言 `claim_segment(d, 0, alive=that)` 為 False，且 `lock_path(d, 0)` 仍存在、內容 pid 是 `os.getpid()`。（測試檔需 `import socket`。）
- [ ] **Step 2: 新增失敗測試（`Progress`）** `test_status_does_not_call_a_dead_lock_running`：照 `test_status_partway_lists_running_and_waiting` 的做法造出缺第 600 段，鎖檔寫 `{"pid": 4194301, "host": socket.gethostname(), "time": time.time()}`；斷言 `lines` 中沒有 `running:` 開頭的行，`waiting:` 行含 `0:10:00-0:20:00`。同時把既有那支測試的 `(sd / "seg_00600.lock").write_text("x")` 改成 `so.claim_segment(sd, 600)`（活鎖）。
- [ ] **Step 3: 跑測試確認失敗**
  Run: `python3 -m unittest tests.test_subtitle_ocr.Locks tests.test_subtitle_ocr.Progress -v`
  Expected: 新增的 3 支 FAIL，其餘 PASS。
- [ ] **Step 4: 改 `lock_is_stale`** 依上面規則；同機判斷用 `info.get("host") == socket.gethostname()`。
- [ ] **Step 5: 改 `claim_segment` 的接手流程**：不再直接 `os.rename(path, ...)` 到最終名稱，而是先把鎖檔 rename 成 `f"{path}.grab.{os.getpid()}"`（原子取得），再對這個取得的檔案呼叫 `lock_is_stale`；過期 → 丟棄（改名成 `.stale.…` 或刪除該暫存檔）後 `continue`；不過期（抓到別人剛建的活鎖）→ `os.rename` 還回 `path`，還不回去（`OSError`）也直接 `return False`。
- [ ] **Step 6: 改 `status_report`** 簽名加 `ttl=LOCK_TTL`；`running` 只算鎖存在且 `not lock_is_stale(lockfile, ttl)`，過期的鎖歸入 `waiting`。`cmd_status` 傳 `getattr(args, "lock_ttl", LOCK_TTL)`（若 `status` 子命令沒有此參數就用預設，不新增參數）。
- [ ] **Step 7: 跑測試確認通過**
  Run: `python3 -m unittest discover -s tests`
  Expected: `OK`。
- [ ] **Step 8: Commit** `git add scripts/subtitle_ocr.py tests/test_subtitle_ocr.py && git commit -m "subtitle_ocr：鎖以 pid 為準、接手不誤搬新鎖、status 不把死鎖當執行中"`

---

### Task 2: 續跑比對參數與原子寫入（項目 1、4）

**Files:**
- Modify: `scripts/subtitle_ocr.py:333-337`（`write_atomic`）、`:427-434`（`run_segmented`）、`cmd_run` 呼叫處
- Test: `tests/test_subtitle_ocr.py`（`Segments`）

**Interfaces:**
- Produces: `class PlanMismatch(RuntimeError)`；`run_segmented(out, seg_dir, segments, ocr_segment, log=say, every=None, ttl=LOCK_TTL, params=None)`。`plan.json` 多存 `"params": params`。
- `cmd_run` 組 `params = {"video": str(args.video), "model": args.model, "every": args.every, "crop": args.crop, "start": args.start, "end": args.end}` 傳入，並 `except so.PlanMismatch as e` → `print(str(e), file=sys.stderr)`、`return 2`。

- [ ] **Step 1: 寫失敗測試**
  - `test_rerun_with_different_params_is_refused`：用 `params={"model": "v4"}` 跑完一輪，再用 `params={"model": "v5"}` 呼叫 → `assertRaises(so.PlanMismatch)`，且 `calls` 沒增加；訊息含 `model`。
  - `test_rerun_with_same_params_still_resumes`：同 params 跑兩次，第二次不呼叫 ocr。
  - `test_plan_without_params_from_an_older_run_is_accepted`：先手寫 `plan.json`（只有 `out/every/segments`），再帶 `params={"model": "v5"}` 跑 → 不丟例外。
  - `test_write_atomic_uses_a_tmp_name_per_process`：`mock.patch("subtitle_ocr.os.replace")` 捕捉第一個引數；斷言它含 `str(os.getpid())` 且以 `.tmp` 結尾；另外不 patch 時寫完資料夾內沒有 `*.tmp`。
- [ ] **Step 2: 跑測試確認失敗**
  Run: `python3 -m unittest tests.test_subtitle_ocr.Segments -v` → 新增 4 支 FAIL。
- [ ] **Step 3: `write_atomic`** tmp 檔名改 `f"{path}.{os.getpid()}.tmp"`。
- [ ] **Step 4: `run_segmented`** 開頭若 `plan.json` 存在且其 `params` 非 None、`params` 參數非 None 且兩者不相等 → `raise PlanMismatch("…")`，訊息列出不同的鍵（舊值→新值）與「換參數請用新的 --out 或刪掉 <seg_dir>」。通過後才寫新 `plan.json`（含 `params`）。
- [ ] **Step 5: `cmd_run`** 組 `params`、傳入、處理 `PlanMismatch`（見 Interfaces）。
- [ ] **Step 6: 跑全套** `python3 -m unittest discover -s tests` → `OK`。
- [ ] **Step 7: Commit** `git commit -m "subtitle_ocr：續跑先比對 plan.json 參數；原子寫入 tmp 檔名帶 pid"`

---

### Task 3: CLI 檢查（項目 6、9、10）

**Files:**
- Modify: `scripts/subtitle_ocr.py`（`--segment-min` 的 `add_argument`、`cmd_run`）
- Test: `tests/test_subtitle_ocr.py`（新類別 `CliChecks`）

**Interfaces:**
- Produces: `segment_min_arg(text: str) -> int`（argparse `type=`，負數丟 `argparse.ArgumentTypeError`）；`check_video(video) -> None`（不是檔案就 `sys.exit("video not found: …")`）。

- [ ] **Step 1: 寫失敗測試**
  - `test_negative_segment_min_is_rejected`：`so.segment_min_arg("-5")` 丟 `argparse.ArgumentTypeError`；`so.segment_min_arg("0") == 0`、`so.segment_min_arg("10") == 10`。
  - `test_missing_video_stops_before_background_start`：`mock.patch("subtitle_ocr.start_background")`；呼叫 `so.cmd_run(Namespace(background=True, video="no/such.mp4", out="o.json", seg_dir=None, raw_argv=[]))` → `assertRaises(SystemExit)`，`start_background` 沒被呼叫。
  - `test_seg_dir_with_single_pass_warns`：暫存空檔當影片；patch `subtitle_ocr.ocr_range` 回 `{}`、`subtitle_ocr.video_duration` 不會被呼叫（`segment_min=0`）；`Namespace(background=False, low_priority=False, segment_min=0, seg_dir="x", video=<檔>, out=<檔>, workers=1, every=3, crop="c", model="v5", start=None, end=None)`；捕捉 stderr 斷言含 `--seg-dir` 與 `ignored`。
- [ ] **Step 2: 跑測試確認失敗**
  Run: `python3 -m unittest tests.test_subtitle_ocr.CliChecks -v` → 3 支 FAIL。
- [ ] **Step 3: 實作** `segment_min_arg`、`check_video`；`--segment-min` 改 `type=segment_min_arg`；`cmd_run` 一開始（`background` 分支之前）呼叫 `check_video(args.video)`；單次模式（`not step_min`）分支內若 `args.seg_dir` 則 `print("warning: --seg-dir is ignored with --segment-min 0 (single pass writes only --out, no resume)", file=sys.stderr)`。
- [ ] **Step 4: 跑全套** → `OK`。
- [ ] **Step 5: Commit** `git commit -m "subtitle_ocr：--segment-min 擋負數、背景啟動前檢查影片、單次模式忽略 --seg-dir 時警告"`

---

### Task 4: 模型下載先寫暫存檔（項目 7）

**Files:**
- Modify: `scripts/subtitle_ocr.py:144-157`（`v5_paths`）
- Test: `tests/test_subtitle_ocr.py`（`Models`）

**Interfaces:**
- Produces: `download_file(url: str, dest: Path, retrieve=None) -> None`：`retrieve` 預設 `urllib.request.urlretrieve`；先下載到 `dest` 同資料夾的 `dest.name + ".part"`，成功且大小 > 0 才 `os.replace` 成 `dest`；失敗時刪掉 `.part` 並讓例外往上丟。`v5_paths` 改呼叫它。

- [ ] **Step 1: 寫失敗測試**
  - `test_failed_download_leaves_no_model_file`：`retrieve` 先寫半截 bytes 再 `raise OSError("net")` → `assertRaises(OSError)`；`dest` 與 `dest.name + ".part"` 都不存在。
  - `test_good_download_lands_under_the_final_name`：`retrieve` 寫 `b"onnx"` → `dest.read_bytes() == b"onnx"`，沒有 `.part`。
  - `test_empty_download_is_an_error`：`retrieve` 寫空檔 → `assertRaises(OSError)`，`dest` 不存在。
- [ ] **Step 2: 跑測試確認失敗**
  Run: `python3 -m unittest tests.test_subtitle_ocr.Models -v` → 3 支 FAIL（`download_file` 不存在）。
- [ ] **Step 3: 實作** `download_file`，`v5_paths` 的下載行改 `download_file(base + name, dest)`。
- [ ] **Step 4: 跑全套** → `OK`。
- [ ] **Step 5: Commit** `git commit -m "subtitle_ocr：模型先下載到 .part 再改名，中斷不留壞檔"`

---

### Task 5: 文件、全套測試、PR 內文

**Files:**
- Modify: `docs/subtitle-ocr-vs-whisper.md`（鎖過期規則、續跑參數比對、`--seg-dir` 與 `--segment-min 0`）；PR #56 內文

- [ ] **Step 1:** `grep` 文件中描述鎖「30 分鐘」「過期」的句子，改成：同一台機器看 pid（活著就不算過期），不同機器才看 30 分鐘；並加一句「換 `--model`／`--every`／`--crop`／`--start`／`--end`／影片時，續跑會拒絕（exit 2），請換新的 `--out` 或刪除 `.segs`」。
- [ ] **Step 2:** 全套 `python3 -m unittest discover -s tests` → `OK`（記下測試數）。
- [ ] **Step 3: Commit** `git commit -m "文件：鎖過期規則與續跑參數比對"`
- [ ] **Step 4:** 等使用者說「commit 並 push」再 `git push`；之後用 `gh pr edit 56 --body-file` 更新 PR 內文：Summary 加「code-review 修正」一節（1–7、9、10）、Evidence 更新測試數、Merge Danger 加「續跑改為拒絕參數不符（exit 2）」。第 8 項寫成「不處理（mobile 模型僅 16 MB，影響小）」。
