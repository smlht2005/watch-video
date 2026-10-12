[00:00] 歡迎收看 Kind 教學，Kind 是「Kubernetes in Docker」的縮寫。
[00:05] Kind 是一個強大的工具，讓你在開發機器上直接執行輕量的本機 Kubernetes 叢集。
[00:11] 在這個教學中，你會學到如何設定 Kind，並用它在 Docker 容器內建立 Kubernetes 叢集。
[00:18] 這對測試、學習與本機開發特別有用，不需要昂貴的雲端資源或複雜的虛擬機設定。
[00:30] Kind 是專為使用 Docker 容器節點來執行本機 Kubernetes 叢集而設計的工具。
[00:37] 它原本是為了測試 Kubernetes 本身而建立，後來成為本機開發與持續整合（CI）流程的絕佳選擇。
[00:46] Kind 不使用虛擬機，而是以 Docker 容器模擬 Kubernetes 節點，因此速度極快、資源效率高。
[00:54] Kind 的主要優點包括：叢集建立快速、相較傳統虛擬機方案資源用量極少、支援多節點叢集，並且很適合在接近真實的 Kubernetes 環境中測試應用程式。
[01:13] 安裝 Kind 之前，必須確認系統符合一些前置需求。
[01:18] 首先，機器上必須安裝並執行 Docker Engine，建議 20.10 以上版本以獲得最佳相容性。
[01:27] 第二，需要 kubectl，也就是用來與叢集互動的 Kubernetes 命令列工具。
[01:34] 請安裝與你計畫執行的 Kubernetes 叢集版本相容的版本。
[01:40] 最後，確保系統有足夠資源：至少 2GB RAM 與 20GB 可用磁碟空間。
[01:48] 這些需求能確保 Kind 叢集順暢運作。
[01:55] Kind 的安裝很簡單，依作業系統略有不同。Linux 使用者可用 curl 下載 Kind 執行檔，以 chmod 設為可執行，再移到本機的 bin 目錄。
[02:09] macOS 使用者最簡單的方式是 Homebrew，執行 brew install kind。
[02:15] Windows 使用者可用 Chocolatey，執行 choco install kind。
[02:21] 安裝後，在終端機執行 kind version 確認 Kind 已正確安裝。
[02:29] 這會顯示已安裝的版本，確認 Kind 可以使用。
[02:36] 用 Kind 建立第一個 Kubernetes 叢集非常簡單。
[02:40] 最基本的指令是 kind create cluster，會建立一個預設名稱為 kind 的單節點叢集。
[02:46] 若想自訂叢集名稱，使用 --name 參數加上你想要的叢集名稱，例如 my-cluster。
[02:56] 叢集建立後，Kind 會自動設定 kubectl 連線到它。
[03:02] 你可以用 kubectl cluster-info 搭配適當的 context 驗證叢集是否正常運作。
[03:09] context 名稱的格式是 kind- 加上你的叢集名稱。
[03:13] 這個驗證步驟可確保叢集已可運作、可以使用。
[03:21] 單節點叢集很實用，但 Kind 真正厲害的地方，是為了更貼近真實的測試情境而建立多節點叢集。
[03:30] 要建立多節點叢集，需要以 YAML 格式定義設定檔。
[03:35] 這個設定檔會指定叢集的 kind 與 API 版本，接著是 nodes 區段，
[03:42] 在其中定義每個節點的角色。
[03:45] 你可以指定一個 control plane 節點與多個 worker 節點。
[03:49] 例如，可設定一個控制平面節點加三個工作節點來模擬正式環境。建好設定檔後，只要執行 kind create cluster 並以 --config 參數指向你的 YAML 檔。
[04:06] 接著 Kind 會把所有指定的節點建立成獨立的 Docker 容器，
[04:11] 並組成可運作的多節點 Kubernetes 叢集。
[04:17] 使用 Kind 的一個重要面向，是讓叢集內執行的服務能對外存取。
[04:22] 這是透過連接埠對應（port mapping）設定完成的。
[04:27] 在叢集設定檔中，可在 control plane 節點下加入 extra port mapping 區段，
[04:34] 在這裡指定哪些容器連接埠要對應到哪些主機連接埠。
[04:38] 例如，將容器連接埠 80 對應到主機連接埠 8080 作為 HTTP 流量，容器連接埠 443 對應到主機連接埠 8443 作為 HTTPS 流量。
[04:50] 同時也要指定協定，通常是 TCP。
[04:54] 這個設定讓你能從本機瀏覽器或其他工具直接存取 Kind 叢集內執行的服務，讓開發與測試方便許多。
[05:08] 管理 Kind 叢集只需要幾個基本指令。
[05:12] 要列出所有 Kind 叢集，使用 kind get clusters。
[05:16] 要查看叢集內的節點，使用 kubectl get nodes。
[05:19] 要刪除叢集，執行 kind delete cluster 並以 --name 參數指定要移除的叢集。
[05:27] kind export kubeconfig 指令會把叢集設定匯出到 kubeconfig 檔，kind get kubeconfig 則顯示 kubeconfig 路徑。
[05:37] 特別實用的是 kind load docker-image，可把 Docker 映像檔直接載入叢集節點，不必推送到遠端映像檔倉庫。
[05:47] 這在經常建置與測試容器映像檔的開發過程中特別有幫助。管理多個叢集時，理解 kubectl context 非常重要。
[06:03] Kind 會自動為你的叢集建立並設定 kubectl context，名稱一律以 kind- 開頭，後面接叢集名稱。
[06:11] 要查看所有可用的 context，使用 kubectl config get-contexts。
[06:16] 這會顯示所有已設定的叢集，並標示目前使用的 context。
[06:20] 要在不同叢集間切換，使用 kubectl config use-context 加上 context 名稱，例如 kind-my-cluster。
[06:28] 要快速確認目前連線的叢集，執行 kubectl config current-context。
[06:34] 妥善管理 context 可確保你始終操作在預期的叢集上，避免誤改到錯誤的環境。
[06:45] Kind 用途廣泛，在 Kubernetes 生態系中有多種重要用途。
[06:51] 本機開發：提供完整的 Kubernetes 環境而不必負擔雲端費用，讓你在接近正式環境的條件下測試應用程式。
[07:02] 測試與持續整合流程：Kind 可搭配可快速建立與銷毀的短暫叢集進行自動化測試。
[07:12] 學習 Kubernetes：Kind 提供安全的沙箱環境，讓你放心實驗各種 Kubernetes 概念與設定，不怕弄壞重要資源。
[07:23] 展示與概念驗證：Kind 可快速建立可運作的 Kubernetes 環境，有效展示你的應用或想法。
[07:34] 這些用途讓 Kind 成為任何 Kubernetes 開發者工具箱中不可或缺的工具。
