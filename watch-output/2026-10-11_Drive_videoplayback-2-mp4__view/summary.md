# 摘要：Kind（Kubernetes in Docker）入門教學

**一句話重點：** 這是一支約 8 分鐘的投影片式教學，介紹如何用 Kind 在本機以 Docker 容器建立單節點與多節點 Kubernetes 叢集，並涵蓋安裝、連接埠對應、管理指令與 kubectl context。

| 時間 | 重點 |
|---|---|
| 00:00 | 開場：Kind = Kubernetes in Docker，輕量本機叢集 |
| 00:30 | 什麼是 Kind；優點：建立快、資源少、支援多節點、適合測試 |
| 01:13 | 前置需求：Docker 20.10+、kubectl、2GB RAM、20GB 磁碟 |
| 01:52 | 安裝：Linux（curl/chmod/mv）、macOS（brew）、Windows（choco）；`kind version` |
| 02:35 | `kind create cluster`、`--name`、`kubectl cluster-info --context` |
| 03:20 | 多節點 YAML 設定（1 control-plane + 3 worker）與 `--config` |
| 04:16 | `extraPortMappings`：80→8080、443→8443（TCP） |
| 05:08 | 管理指令：get clusters／get nodes／delete cluster／export 與 get kubeconfig／load docker-image |
| 05:49 | kubectl context：`kind-` 前綴、get/use/current-context |
| 06:42 | 使用情境：本機開發、CI/CD、學習、展示 |
| 07:38 | 片尾宣傳語（非教學內容） |

## 名詞與縮寫
- **Kind**：Kubernetes in Docker，以 Docker 容器當節點的本機叢集工具。
- **control plane／worker node**：控制平面節點／工作節點。
- **kubeconfig／context**：kubectl 連線設定檔／其中的叢集連線組合。
- **extraPortMappings**：把節點容器連接埠對應到主機連接埠，便於從本機存取叢集服務。

## 轉錄校正備註
- 影片為中英混雜，Whisper（Groq）把部分英文旁白誤聽成不通順的中文（如「團隊」＝cluster、「框架」＝port）。已用詞典修正 kubectl／kubeconfig／控制平面／工作節點，並附完整中譯 `transcript.zh.md`，指令內容以投影片畫面為準。
- 影片來源為 Google Drive 檔案（`videoplayback (2).mp4`），無平台字幕與作者資訊。
