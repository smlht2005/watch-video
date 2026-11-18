# 知識點

## 已確認

## 候選
### KIND 用 Docker 容器模擬 Kubernetes 節點，而不是虛擬機
- 出處：00:30
- 引文：「Instead of using virtual machines, KIND uses Docker containers to simulate Kubernetes nodes」
- 說明：講者說 KIND（Kubernetes in Docker）是專為用 Docker 容器節點跑本地 Kubernetes 叢集設計的工具，原本為測試 Kubernetes 本身而建，如今適合本地開發與 CI；它不用虛擬機，而是用 Docker 容器模擬節點，因此建立叢集快、資源用量少，並支援多節點叢集。
- 標示：講者主張，未查證

### 安裝前提：Docker、kubectl 與最低資源
- 出處：01:40
- 引文：「at least 2 GB of RAM and 20 GB of available disk space」
- 說明：講者說安裝 KIND 前要先有執行中的 Docker Engine（建議 20.10 以上）與相容版本的 kubectl，並至少有 2 GB RAM 與 20 GB 可用磁碟空間，才能讓叢集順暢運作。Linux 以 curl 下載二進位檔、chmod 後移到 local bin，macOS 用 brew install kind，Windows 用 choco install kind，安裝後以 kind version 驗證。
- 標示：講者主張，未查證

### 建立叢集的最基本指令：kind create cluster
- 出處：02:36
- 引文：「The most basic command is kind create cluster」
- 說明：講者說最基本的指令是 kind create cluster，建立單節點叢集、預設名稱 kind；要自訂名稱用 --name 旗標（例：my cluster）。叢集建好後 KIND 會自動設定 kubectl 連線，可用 kubectl cluster-info 搭配 context 驗證，context 名稱格式是 kind-<叢集名>。
- 標示：講者主張，未查證

### 多節點叢集用 YAML 設定檔定義
- 出處：03:22
- 引文：「you need to define a configuration file in YAML format」
- 說明：講者說 KIND 在多節點測試時特別好用：需用 YAML 格式的設定檔，指定叢集 kind 與 API 版本，再在 nodes 區段定義每個節點的角色（一個 control plane 加多個 worker，例：1 個 control plane 與 3 個 worker 模擬類生產環境），之後用 kind create cluster --config 指向該檔案，KIND 就把每個節點建成獨立的 Docker 容器並組成可用的叢集。
- 標示：講者主張，未查證

### 用 port mapping 讓本機存取叢集內服務
- 出處：04:17
- 引文：「map container port 80 to host port 8080」
- 說明：講者說要把叢集內的服務露給宿主機，要在設定檔 control plane 節點下加 extra port mapping，指定容器埠對應到主機埠，例如容器 80 對應主機 8080（HTTP）、443 對應 8443（HTTPS），協定通常是 TCP，這樣就能從本機瀏覽器或工具直接存取叢集內服務。
- 標示：講者主張，未查證

### kind load docker-image：不經遠端 registry 直接載入映像檔
- 出處：05:08
- 引文：「loads a docker image directly into your cluster nodes」
- 說明：講者說 kind load docker-image 能把 Docker 映像檔直接載入叢集節點，不必先推到遠端 registry，在開發時常需反覆建置與測試容器映像時特別有用。其他常用指令：kind get clusters 列出叢集、kubectl get nodes 看節點、kind delete cluster --name 刪除叢集、kind export kubeconfig 匯出設定。
- 標示：講者主張，未查證

### kubectl context 要管好，避免誤改到別的叢集
- 出處：05:56
- 引文：「always prefixing them with kind followed by the cluster name」
- 說明：講者說 KIND 會自動為每個叢集建立並設定 kubectl context，名稱一律以 kind 開頭加叢集名（例：kind-my-cluster）；用 kubectl config get-contexts 檢視、use-context 切換、current-context 確認目前連到哪個叢集。講者強調妥善管理 context 才能確保一直在操作預期的叢集，避免誤改到錯誤環境。
- 標示：講者主張，未查證
