[00:00] 歡迎收看 Kind 的介紹影片。Kind 就是「Kubernetes in Docker」，能讓你輕鬆在本機建立 Kubernetes 叢集，是開發時很強大的工具。
[00:11] 這支影片會教你如何設定 Kind，並在 Docker 容器內建立 Kubernetes 叢集，非常適合測試、學習與本機開發，不需要雲端資源或複雜的虛擬機設定。
[00:30] Kind 是用 Docker 容器節點來執行本機 Kubernetes 叢集的工具，原本是為了測試 Kubernetes 本身而設計，後來也成為本機開發與 CI 流程的選擇。
[00:46] Kind 以 Docker 容器模擬 Kubernetes 節點，因此速度快、資源佔用低。
[00:55] 主要優點：叢集建立快速、比傳統虛擬機輕量、支援多節點叢集，並且很適合在接近真實的 Kubernetes 環境中測試應用程式。
[01:13] 安裝 Kind 之前，系統需先滿足幾項需求。第一，機器上必須安裝並執行 Docker Engine，建議 20.10 以上版本。
[01:27] 第二，需要 kubectl（Kubernetes 的命令列工具）與叢集互動，並確認版本與你要執行的 Kubernetes 叢集相容。
[01:40] 最後，系統至少要有 2GB RAM 與 20GB 可用磁碟空間，才能讓 Kind 叢集順暢運作。
[01:52] Kind 的安裝方式依作業系統而異。Linux 使用者可用 curl 下載執行檔，以 chmod 設為可執行，再移到本機的 bin 目錄。
[02:09] macOS 最簡單的方式是 Homebrew，執行 brew install kind。Windows 使用者可用 Chocolatey，執行 choco install kind。
[02:21] 安裝完成後，執行 kind version 確認安裝版本，Kind 即可使用。
[02:35] 用 Kind 建立第一個 Kubernetes 叢集非常簡單。最基本的指令是 kind create cluster，會建立名為 kind 的單節點叢集。
[02:47] 若想自訂叢集名稱，加上 --name 參數與名稱，例如 my-cluster。
[02:56] 叢集建立後，Kind 會自動設定 kubectl 與它連線，可用 kubectl cluster-info 搭配對應的 context 確認叢集正在運作。
[03:20] 單節點叢集很實用，但 Kind 真正的優勢在於建立多節點叢集，以進行更貼近真實的測試。
[03:31] 要建立多節點叢集，需要寫一個 YAML 設定檔，指定叢集的 kind 與 API 版本，接著在 nodes 區段定義各節點的角色。
[03:44] 可設定一個 control-plane 節點與多個 worker 節點，例如一個控制平面加三個工作節點，來模擬類似正式環境的架構。
[03:56] 建好設定檔後，執行 kind create cluster --config 並指向該 YAML 檔。
[04:06] Kind 會把每個指定的節點建立成獨立的 Docker 容器，並組成可運作的多節點 Kubernetes 叢集。
[04:16] 使用 Kind 的一個重點，是如何從主機存取叢集內的服務，這要透過叢集設定檔中的 port mapping（連接埠對應）。
[04:27] 在設定檔的 control-plane 節點下加入 extraPortMappings，指定哪些容器連接埠要對應到主機連接埠。
[04:38] 例如把容器連接埠 80 對應到主機 8080 作為 HTTP，容器連接埠 443 對應到主機 8443 作為 HTTPS，並指定協定（通常是 TCP）。
[04:54] 這樣就能從本機瀏覽器或其他工具直接存取 Kind 叢集內執行的服務，讓開發與測試更方便。
[05:08] 管理 Kind 叢集有幾個基本指令：kind get clusters 列出所有叢集，kubectl get nodes 查看節點。
[05:19] 要刪除叢集用 kind delete cluster，並以 --name 指定要刪除的叢集。
[05:26] kind export kubeconfig 會把叢集設定匯出到 kubeconfig 檔，kind get kubeconfig 則顯示 kubeconfig 的內容。
[05:36] 特別實用的是 kind load docker-image，可把本機 Docker 映像檔直接載入叢集節點，不需要推送到映像檔倉庫，對經常建置與測試容器映像檔的開發很有幫助。
[05:49] 同時管理多個叢集時，理解 kubectl context 很重要。Kind 會自動為叢集建立並設定 kubectl context，名稱一律以 kind- 開頭，後面接叢集名稱。
[06:11] 用 kubectl config get-contexts 查看所有 context 與目前使用的 context。
[06:20] 用 kubectl config use-context 加上 context 名稱（例如 kind-my-cluster）切換；用 kubectl config current-context 查看目前所在的 context。
[06:34] 管理好 context 可確保你始終在正確的叢集上操作，避免在錯誤環境中做出錯誤變更。
[06:42] Kind 非常可靠，用途廣泛。本機開發：提供完整的 Kubernetes 環境而不必負擔雲端費用，可在接近正式環境的條件下測試應用程式。
[07:01] 測試與 CI/CD：可自動化測試，叢集能快速建立與銷毀。
[07:11] 學習 Kubernetes：提供安全的沙箱，可放心實驗各種概念與設定，不怕弄壞重要資源。
[07:23] 展示與概念驗證：可快速建立可運作的 Kubernetes 環境，有效展示你的應用或想法。
[07:34] 這些用途讓 Kind 成為 Kubernetes 開發者工具箱中不可或缺的工具。
[07:38] 請不吝點讚、訂閱、轉發、打賞（片尾版權宣傳語）。
