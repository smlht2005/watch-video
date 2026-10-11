[00:00] 歡迎收看 KIND 教學；KIND 是 Kubernetes in Docker 的縮寫，是一個可在開發機上執行輕量本地 Kubernetes 叢集的強大工具。
[00:11] 本教學會教你如何安裝 KIND，並用它在 Docker 容器內建立 Kubernetes 叢集。這對測試、學習與本地開發特別有用，不需要昂貴的雲端資源或複雜的虛擬機設定。
[00:30] KIND 專為以 Docker 容器節點執行本地 Kubernetes 叢集而設計。它原本是為了測試 Kubernetes 本身而建立，現已成為本地開發與持續整合（CI）流程的絕佳選擇。KIND 不用虛擬機，而是以 Docker 容器模擬 Kubernetes 節點，因此極快且省資源。主要優點包括：叢集建立快、資源用量遠低於傳統虛擬機方案、支援多節點叢集，並適合在接近真實的 Kubernetes 環境中測試應用程式。
[01:13] 安裝 KIND 前須確認系統符合先決條件。第一，必須安裝並啟動 Docker Engine，建議 20.10 以上版本以獲得最佳相容性。第二，需要 kubectl，即與叢集互動的 Kubernetes 命令列工具，請安裝與你要執行的叢集版本相容的版本。
[01:40] 最後，確認系統資源足夠：至少 2 GB 記憶體與 20 GB 可用磁碟空間，才能讓 KIND 叢集順暢運作。
[01:55] 安裝 KIND 很簡單，依作業系統略有不同。Linux 使用者以 curl 下載 kind 執行檔，用 chmod 設為可執行，再移到本地 bin 目錄。macOS 最簡單的方式是 Homebrew：brew install kind。
[02:16] Windows 使用者可用 Chocolatey：choco install kind。安裝後執行 kind version 驗證，會顯示版本並確認 KIND 已可使用。
[02:36] 以 KIND 建立第一個叢集非常簡單。最基本的指令是 kind create cluster，會建立名為 kind 的單節點叢集；若要自訂名稱，加上 --name 參數，例如 my-cluster。叢集建立後，KIND 會自動設定 kubectl 連線。可用 kubectl cluster-info 搭配 context 驗證叢集運作；context 名稱格式為 kind- 加上叢集名稱。這個驗證步驟可確保叢集已就緒。
[03:22] 單節點叢集很實用，但 KIND 真正的強項是建立更貼近實際測試情境的多節點叢集。要建立多節點叢集，需撰寫 YAML 設定檔，指定叢集 kind 與 API 版本，並在 nodes 區段定義各節點角色：一個 control-plane 節點與多個 worker 節點。
[03:49] 例如可設定一個 control-plane 與三個 worker 來模擬類生產環境。建好設定檔後，執行 kind create cluster --config 指向該 YAML 檔，KIND 就會把每個節點建成獨立的 Docker 容器，並組成可運作的多節點 Kubernetes 叢集。
[04:17] 使用 KIND 的重要一環，是把叢集內的服務暴露給主機，方法是設定連接埠對應（port mapping）。在叢集設定檔 control-plane 節點下加入 extraPortMappings，指定容器埠對應到哪個主機埠；例如容器 80 對應主機 8080（HTTP）、容器 443 對應主機 8443（HTTPS），並指定通訊協定（通常為 TCP）。如此即可從本機瀏覽器或其他工具直接存取 KIND 叢集內的服務，讓開發與測試更方便。
[05:08] 管理 KIND 叢集靠幾個基本指令：kind get clusters 列出所有叢集；kubectl get nodes 檢視叢集節點；kind delete cluster --name 刪除指定叢集；kind export kubeconfig 把叢集設定匯出到 kubeconfig，kind get kubeconfig 則輸出 kubeconfig 內容。特別實用的是 kind load docker-image，可把 Docker 映像直接載入叢集節點，無須推送到遠端映像庫，開發時頻繁建置、測試映像特別方便。
[05:56] 瞭解 kubectl context 對使用 KIND 很重要，尤其是管理多個叢集時。KIND 會自動建立並設定 kubectl context，名稱一律是 kind- 加上叢集名稱。用 kubectl config get-contexts 檢視所有 context 並標示目前使用者；用 kubectl config use-context kind-my-cluster 切換叢集；用 kubectl config current-context 快速確認目前連到哪個叢集。
[06:34] 正確管理 context 能確保你始終在預期的叢集上作業，避免誤改到錯誤的環境。
[06:45] KIND 用途多元。本地開發：無需雲端費用即可取得完整 Kubernetes 環境，在貼近生產的條件下測試應用。測試與 CI：以可快速建立與銷毀的臨時叢集做自動化測試。學習 Kubernetes：提供安全的沙箱，可放心實驗各種概念與設定。展示與概念驗證（PoC）：快速架起可運作的 Kubernetes 環境來呈現應用或構想。這些用途讓 KIND 成為 Kubernetes 開發者工具箱的必備工具。
[07:40] 如果喜歡這支影片，請按讚並訂閱。
[07:46] 歡迎造訪 codelucky.com 獲得更多實用內容。
