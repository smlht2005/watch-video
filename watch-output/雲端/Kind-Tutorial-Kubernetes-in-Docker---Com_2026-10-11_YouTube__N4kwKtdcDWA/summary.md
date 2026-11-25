# 摘要：Kind Tutorial: Kubernetes in Docker - Complete Beginner's Guide to Local K8s Clusters

**一句話重點：** KIND（Kubernetes in Docker）以 Docker 容器當節點，在本機快速建立單節點或多節點 Kubernetes 叢集，適合開發、CI 測試、學習與 PoC。

## 重點時間軸

| 時間 | 重點 |
|---|---|
| 00:00 | 開場：KIND 是在開發機執行輕量本地 K8s 叢集的工具 |
| 00:30 | KIND 簡介：原為測試 Kubernetes 本身而生；用容器模擬節點，建立快、省資源、支援多節點 |
| 01:13 | 先決條件：Docker Engine（建議 20.10+）、kubectl、至少 2 GB RAM 與 20 GB 磁碟 |
| 01:55 | 安裝：Linux（curl + chmod + 移至 bin）、macOS（`brew install kind`）、Windows（`choco install kind`）；`kind version` 驗證 |
| 02:36 | 建立第一個叢集：`kind create cluster`，`--name` 自訂名稱；context 為 `kind-<名稱>` |
| 03:22 | 多節點叢集：以 YAML 設定檔定義 1 個 control-plane + 多個 worker，`--config` 建立 |
| 04:17 | 連接埠對應：`extraPortMappings`（如 80→8080、443→8443，TCP）讓主機存取叢集服務 |
| 05:08 | 常用指令：`kind get clusters`、`kind delete cluster --name`、`kind export kubeconfig`、`kind load docker-image` |
| 05:56 | kubectl context：`get-contexts`、`use-context`、`current-context`；避免誤操作錯誤叢集 |
| 06:45 | 使用情境：本地開發、CI 臨時叢集、學習沙箱、展示與 PoC |
| 07:40 | 結語（按讚訂閱、codelucky.com） |

## 名詞與縮寫

- **KIND**：Kubernetes IN Docker。
- **control-plane / worker**：K8s 控制平面節點與工作節點，在 KIND 中皆為 Docker 容器。
- **kubectl**：K8s 命令列工具。**context**：kubectl 連線目標叢集的設定。
- **extraPortMappings**：把節點容器埠對應到主機埠。
- **CI**：持續整合。**PoC**：概念驗證。

## 轉錄校正備註

- 來源為 YouTube 自動英文字幕（滾動重複格式），已去重並合併成句。
- 字幕誤聽已校正：Cubectal/cubectal→kubectl、cubic config→kubeconfig、Chocolaty→Chocolatey、YL/yiml→YAML、「Version 20.10 10」→Docker 20.10、dash-name/d-name→`--name`、dash-config→`--config`、`kubectl config get/use/current context`→帶連字號的子指令。
- **無畫面**：YouTube 對本環境要求登入驗證（bot 偵測，HTTP 403/429），無法下載影片，故報告沒有截圖，也未做投影片分段。
