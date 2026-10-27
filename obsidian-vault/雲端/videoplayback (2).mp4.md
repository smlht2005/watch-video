---
title: "videoplayback (2).mp4"
type: video-note
source: "https://drive.google.com/file/d/1bVcAjmgzoAhVKgMyXApHrQSOl-7_ZoGa/view?usp=drivesdk"
platform: "Drive"
video_id: "view"
uploader: ""
category: "雲端"
date: "2026-10-11"
status: unreviewed
origin_folder: "watch-output/雲端/2026-10-11_Drive_videoplayback-2-mp4__view"
generated_by: watch-archive
aliases:
  - "videoplayback (2).mp4"
tags:
  - "watch-archive"
  - "雲端"
  - "Kind"
  - "Kubernetes-in-Docker"
  - "kubectl"
  - "kubeconfig"
  - "多節點叢集"
  - "control-plane"
  - "worker-node"
  - "extraPortMappings"
  - "kubectl-context"
  - "CI/CD"
---

# videoplayback (2).mp4

## 摘要

**一句話重點：** 這是一支約 8 分鐘的投影片式教學，介紹如何用 Kind 在本機以 Docker 容器建立單節點與多節點 Kubernetes 叢集，並涵蓋安裝、連接埠對應、管理指令與 kubectl context。

| 時間 | 重點 |
|---|---|
| 00:00 | 開場：Kind = Kubernetes in Docker，輕量本機叢集 |
| 00:30 | 什麼是 Kind；優點：建立快、資源少、支援多節點、適合測試 |
| 01:13 | 前置需求：Docker 20.10+、kubectl、2GB RAM、20GB 磁碟 |
| 01:55 | 安裝：Linux（curl/chmod/mv）、macOS（brew）、Windows（choco）；`kind version` |
| 02:36 | `kind create cluster`、`--name`、`kubectl cluster-info --context` |
| 03:21 | 多節點 YAML 設定（1 control-plane + 3 worker）與 `--config` |
| 04:17 | `extraPortMappings`：80→8080、443→8443（TCP） |
| 05:08 | 管理指令：get clusters／get nodes／delete cluster／export 與 get kubeconfig／load docker-image |
| 05:47 | kubectl context：`kind-` 前綴、get/use/current-context |
| 06:45 | 使用情境：本機開發、CI/CD、學習、展示 |
| 07:38 | 片尾按讚動畫（無旁白） |

### 名詞與縮寫
- **Kind**：Kubernetes in Docker，以 Docker 容器當節點的本機叢集工具。
- **control plane／worker node**：控制平面節點／工作節點。
- **kubeconfig／context**：kubectl 連線設定檔／其中的叢集連線組合。
- **extraPortMappings**：把節點容器連接埠對應到主機連接埠，便於從本機存取叢集服務。

### 轉錄校正備註
- 影片旁白為**英文**。初版誤加 `--lang zh`，Whisper 被迫輸出中文而產生大量不通順文字；已改為自動語言偵測重新轉錄，英文逐字稿品質良好（來源：Groq Whisper）。
- 殘留問題僅為指令空格被吞（如 `kindcreatecluster`）與少數缺標點，已由 `glossary/domains/kubernetes.json` 修正並記於 `known_asr_errors`。
- 附完整中譯 `transcript.zh.md`（時間戳沿用英文原文）。
- 影片來源為 Google Drive 檔案（`videoplayback (2).mp4`），無平台字幕與作者資訊。

## 來源

- 原始資料夾：`watch-output/雲端/2026-10-11_Drive_videoplayback-2-mp4__view`
- 逐字稿來源：whisper (groq)
