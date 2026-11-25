# Kind Tutorial: Kubernetes in Docker - Complete Beginner's Guide to Local K8s Clusters

- 來源：https://youtu.be/N4kwKtdcDWA?si=E8oJT3J51MsNc3pB
- 平台 / 上傳者：YouTube / CodeLucky
- 長度：07:55 (475.0s)
- 逐字稿來源：captions (en, automatic, original)
- 更新日期：2026-10-11
- **關鍵字：** #KIND #Kubernetes in Docker #Kubernetes #Docker #kubectl #多節點叢集 #連接埠對應 #kube context #CI #本地開發

## 摘要與名詞說明

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

## 圖文對照（畫面 + 逐字稿＋中譯）

Welcome to this tutorial on KIND, which stands for Kubernetes in Docker. KIND is a powerful tool that allows you to run lightweight local Kubernetes clusters right on your development machine. Throughout this tutorial, you'll learn how to set up KIND and use it to create Kubernetes clusters inside Docker containers. This is particularly useful for testing, learning, and local development without the need for expensive cloud resources or complex virtual machine setups. Kind is a tool specifically designed for running local Kubernetes clusters using Docker container nodes. Originally created for testing Kubernetes itself, it has become an excellent choice for local development and continuous integration pipelines. Instead of using virtual machines, KIND uses Docker containers to simulate Kubernetes nodes, making it incredibly fast and resource efficient. The key advantages of KIND include fast cluster creation, minimal resource usage compared to traditional virtual machine-based solutions, support for multi-node clusters, and it's perfect for testing your applications in a realistic Kubernetes environment. Before installing Kind, you need to ensure your system meets certain prerequisites. First, you must have Docker Engine installed and running on your machine. Docker 20.10 or higher is recommended for optimal compatibility. Second, you need kubectl, which is the Kubernetes command line tool used for interacting with your clusters. Make sure to install a version compatible with the Kubernetes cluster version you plan to run. Finally, ensure your system has adequate resources, at least 2 GB of RAM and 20 GB of available disk space. These requirements ensure smooth operation of your kind clusters. Installing KIND is straightforward and varies slightly depending on your operating system. For Linux users, you can download the Kind binary using curl, make it executable with the chmod command, and then move it to your local bin directory. For Mac OS users, the easiest method is using Homebrew by simply running brew install kind. Windows users can install Kind using Chocolatey with the command choco install kind. After installation, verify that KIND is properly installed by running the Kind version command in your terminal. This will display the installed version and confirm that KIND is ready to use. Creating your first Kubernetes cluster with KIND is remarkably simple. The most basic command is kind create cluster, which creates a single node cluster with the default name kind. If you want to specify a custom name for your cluster, use the --name flag followed by your desired cluster name. For example, my cluster. Once the cluster is created, kind automatically configures kubectl to connect to it. You can verify that your cluster is running properly by using the kubectl cluster info command with the appropriate context. The context name follows the pattern kind followed by your cluster name. This verification step ensures your cluster is operational and ready for use. While single node clusters are useful, kind really shines when creating multi-node clusters for more realistic testing scenarios. To create a multi-node cluster, you need to define a configuration file in YAML format. This configuration file specifies the cluster kind and API version followed by a node section where you define the roles of each node. You can specify one control plane node and multiple worker nodes. For example, you might configure one control plane node and three worker nodes to simulate a production-like environment. Once you've created your configuration file, simply run kind create cluster with the --config flag pointing to your YAML file. Kind will then create all the specified nodes as separate docker containers and configure them into a functioning multi-node kubernetes cluster. One important aspect of working with kind is exposing services running inside your cluster to your host machine. This is accomplished through port mapping configuration. In your cluster configuration file, you can add an extra port mapping section under the control plane node. Here you specify which container ports should be mapped to which host ports. For example, you might map container port 80 to host port 8080 for HTTP traffic and container port 443 to host port 8443 for HTTPS traffic. You also specify the protocol, typically TCP. This configuration allows you to access services running inside your Kind cluster directly from your local machine's browser or other tools, making development and testing much more convenient. Managing your Kind clusters is straightforward with several essential commands. To list all your kind clusters, use kind get clusters. To view the nodes within a cluster, use kubectl get nodes. When you need to delete a cluster, run kind delete cluster with the --name flag specifying which cluster to remove. The kind export kubeconfig command exports the cluster's configuration to your kubeconfig file while kind get kubeconfig displays the kubeconfig path. An especially useful command is kind load docker-image which loads a docker image directly into your cluster nodes without needing to push it to a remote registry. This is particularly helpful during development when you're frequently building and testing container images. Understanding kubectl contexts is crucial when working with Kind, especially if you manage multiple clusters. Kind automatically creates and configures kubectl contexts for your clusters, always prefixing them with kind followed by the cluster name. To view all available contexts, use kubectl config get-contexts. This shows you all configured clusters and highlights your current context. To switch between different clusters, use kubectl config use-context followed by the context name such as kind-my-cluster. To quickly check which cluster you're currently connected to, run kubectl config current-context. Managing contexts properly ensures you're always working with the intended cluster, preventing accidental changes to the wrong environment. Kind is incredibly versatile and serves multiple important use cases in the Kubernetes ecosystem. For local development, it provides a complete Kubernetes environment without incurring cloud costs, allowing you to test your applications in conditions that closely mirror production in testing and continuous integration pipelines. Kind enables automated testing with ephemeral clusters that can be quickly created and destroyed. For learning Kubernetes, KIND offers a safe sandbox environment where you can experiment with various Kubernetes concepts and configurations without fear of breaking anything important. Finally, for demonstrations and proof of concepts, KIND allows for quick setup of working Kubernetes environments that can showcase your applications or ideas effectively. These use cases make kind an essential tool in any Kubernetes developer toolkit. If you like this video, hit that like button and don't forget to subscribe. Visit codelucky.com for more such useful content.

**中譯：** 歡迎收看 KIND 教學；KIND 是 Kubernetes in Docker 的縮寫，是一個可在開發機上執行輕量本地 Kubernetes 叢集的強大工具。本教學會教你如何安裝 KIND，並用它在 Docker 容器內建立 Kubernetes 叢集。這對測試、學習與本地開發特別有用，不需要昂貴的雲端資源或複雜的虛擬機設定。KIND 專為以 Docker 容器節點執行本地 Kubernetes 叢集而設計。它原本是為了測試 Kubernetes 本身而建立，現已成為本地開發與持續整合（CI）流程的絕佳選擇。KIND 不用虛擬機，而是以 Docker 容器模擬 Kubernetes 節點，因此極快且省資源。主要優點包括：叢集建立快、資源用量遠低於傳統虛擬機方案、支援多節點叢集，並適合在接近真實的 Kubernetes 環境中測試應用程式。安裝 KIND 前須確認系統符合先決條件。第一，必須安裝並啟動 Docker Engine，建議 20.10 以上版本以獲得最佳相容性。第二，需要 kubectl，即與叢集互動的 Kubernetes 命令列工具，請安裝與你要執行的叢集版本相容的版本。最後，確認系統資源足夠：至少 2 GB 記憶體與 20 GB 可用磁碟空間，才能讓 KIND 叢集順暢運作。安裝 KIND 很簡單，依作業系統略有不同。Linux 使用者以 curl 下載 kind 執行檔，用 chmod 設為可執行，再移到本地 bin 目錄。macOS 最簡單的方式是 Homebrew：brew install kind。Windows 使用者可用 Chocolatey：choco install kind。安裝後執行 kind version 驗證，會顯示版本並確認 KIND 已可使用。以 KIND 建立第一個叢集非常簡單。最基本的指令是 kind create cluster，會建立名為 kind 的單節點叢集；若要自訂名稱，加上 --name 參數，例如 my-cluster。叢集建立後，KIND 會自動設定 kubectl 連線。可用 kubectl cluster-info 搭配 context 驗證叢集運作；context 名稱格式為 kind- 加上叢集名稱。這個驗證步驟可確保叢集已就緒。單節點叢集很實用，但 KIND 真正的強項是建立更貼近實際測試情境的多節點叢集。要建立多節點叢集，需撰寫 YAML 設定檔，指定叢集 kind 與 API 版本，並在 nodes 區段定義各節點角色：一個 control-plane 節點與多個 worker 節點。例如可設定一個 control-plane 與三個 worker 來模擬類生產環境。建好設定檔後，執行 kind create cluster --config 指向該 YAML 檔，KIND 就會把每個節點建成獨立的 Docker 容器，並組成可運作的多節點 Kubernetes 叢集。使用 KIND 的重要一環，是把叢集內的服務暴露給主機，方法是設定連接埠對應（port mapping）。在叢集設定檔 control-plane 節點下加入 extraPortMappings，指定容器埠對應到哪個主機埠；例如容器 80 對應主機 8080（HTTP）、容器 443 對應主機 8443（HTTPS），並指定通訊協定（通常為 TCP）。如此即可從本機瀏覽器或其他工具直接存取 KIND 叢集內的服務，讓開發與測試更方便。管理 KIND 叢集靠幾個基本指令：kind get clusters 列出所有叢集；kubectl get nodes 檢視叢集節點；kind delete cluster --name 刪除指定叢集；kind export kubeconfig 把叢集設定匯出到 kubeconfig，kind get kubeconfig 則輸出 kubeconfig 內容。特別實用的是 kind load docker-image，可把 Docker 映像直接載入叢集節點，無須推送到遠端映像庫，開發時頻繁建置、測試映像特別方便。瞭解 kubectl context 對使用 KIND 很重要，尤其是管理多個叢集時。KIND 會自動建立並設定 kubectl context，名稱一律是 kind- 加上叢集名稱。用 kubectl config get-contexts 檢視所有 context 並標示目前使用者；用 kubectl config use-context kind-my-cluster 切換叢集；用 kubectl config current-context 快速確認目前連到哪個叢集。正確管理 context 能確保你始終在預期的叢集上作業，避免誤改到錯誤的環境。KIND 用途多元。本地開發：無需雲端費用即可取得完整 Kubernetes 環境，在貼近生產的條件下測試應用。測試與 CI：以可快速建立與銷毀的臨時叢集做自動化測試。學習 Kubernetes：提供安全的沙箱，可放心實驗各種概念與設定。展示與概念驗證（PoC）：快速架起可運作的 Kubernetes 環境來呈現應用或構想。這些用途讓 KIND 成為 Kubernetes 開發者工具箱的必備工具。如果喜歡這支影片，請按讚並訂閱。歡迎造訪 codelucky.com 獲得更多實用內容。

## 已知轉錄錯誤

| 時間 | 聽成 | 應為 |
|---|---|---|
| 01:13 | Cubectal | kubectl |
| 02:16 | Chocolaty | Chocolatey |
| 03:22 | YL format | YAML format |
| 01:13 | Version 20.10 10 | Docker 20.10（推測） |
| 05:08 | cubic config | kubeconfig |
