# videoplayback (2).mp4

- 來源：https://drive.google.com/file/d/1bVcAjmgzoAhVKgMyXApHrQSOl-7_ZoGa/view?usp=drivesdk
- 平台 / 上傳者：Drive / 
- 長度：07:55 (475.2s)
- 逐字稿來源：whisper (groq)
- 更新日期：2026-10-11
- **關鍵字：** #Kind #Kubernetes in Docker #kubectl #kubeconfig #多節點叢集 #control plane #worker node #extraPortMappings #kubectl context #CI/CD

## 摘要與名詞說明

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

## 圖文對照（畫面 + 逐字稿＋中譯）

### 投影片 1：Kind：Kubernetes in Docker（00:00–00:30）

![00:00](frames/frame_0001.jpg)

**重點：** 在本機用 Docker 建立輕量 Kubernetes 叢集，適合測試、學習與開發。

**標籤：** #Kind #Docker

歡迎來到KIND的這個影片，KIND是Docker的Kubernetes。KIND是一個能夠讓你使用的很輕鬆的，Local Kubernetes Cluster，在你的發展設計中使用的很強大的工具。在這個影片中，你將學習如何設定KIND,，並使用它來建立Kubernetes Cluster，在Docker的包裝內。這非常有用於測試、學習和，在區域發展上的課程，不需要費用的 cloud 資源，或細勝的 virtual machine 設定。

**中譯：** 歡迎收看 Kind 的介紹影片。Kind 就是「Kubernetes in Docker」，能讓你輕鬆在本機建立 Kubernetes 叢集，是開發時很強大的工具。這支影片會教你如何設定 Kind，並在 Docker 容器內建立 Kubernetes 叢集，非常適合測試、學習與本機開發，不需要雲端資源或複雜的虛擬機設定。

### 投影片 2：什麼是 Kind（00:30–01:13）

![00:30](frames/frame_0006.jpg)

**重點：** 以 Docker 容器節點執行本機叢集；優點：建立快、資源少、支援多節點、適合測試。

**標籤：** #Kind #多節點

Kind是一個特別設計為使用Docker團體核檔用的專用的專用團體，原來是為了測試Kubernetes,它成為了專用的專用團體和繼續的運輸流程的一個選擇，而不是用專用的產品，Kind使用Docker團體來模擬Kubernetes的核檔，使它非常快速和有資源，KIND的重要優點包括快速的圖案創造、比較傳統的機器基礎系統上的低重量使用、支援多核檔的圖案，並且它是完美的測試您的應用程式，在一種實際的Kubernetes環境中。

**中譯：** Kind 是用 Docker 容器節點來執行本機 Kubernetes 叢集的工具，原本是為了測試 Kubernetes 本身而設計，後來也成為本機開發與 CI 流程的選擇。Kind 以 Docker 容器模擬 Kubernetes 節點，因此速度快、資源佔用低。主要優點：叢集建立快速、比傳統虛擬機輕量、支援多節點叢集，並且很適合在接近真實的 Kubernetes 環境中測試應用程式。

### 投影片 3：安裝前置需求（01:13–01:52）

![01:13](frames/frame_0014.jpg)

**重點：** Docker Engine 20.10+、kubectl、至少 2GB RAM 與 20GB 磁碟。

**標籤：** #Docker #kubectl

在KIND的安裝前，您必須確保您的系統遵守了一定的要求。首先，您必須將Docker Engine安裝和在您的機器上執行。20.10或高的版本是推薦以最高的配置，第二，您需要Kubectl,，是Kubernetes的指令線工具，使用於您的粒子中的互動，確保您設定在您計劃運作的，Kubernetes Cluster版本上的配置，最後，確保您的系統有足夠的資源，至少2GB的RAM和20GB的可用的Disk Space，這些要求確保您的Kind Clusters順暢運作。

**中譯：** 安裝 Kind 之前，系統需先滿足幾項需求。第一，機器上必須安裝並執行 Docker Engine，建議 20.10 以上版本。第二，需要 kubectl（Kubernetes 的命令列工具）與叢集互動，並確認版本與你要執行的 Kubernetes 叢集相容。最後，系統至少要有 2GB RAM 與 20GB 可用磁碟空間，才能讓 Kind 叢集順暢運作。

### 投影片 4：安裝 Kind（01:52–02:35）

![01:52](frames/frame_0021.jpg)

**重點：** Linux 用 curl+chmod+mv；macOS 用 brew install kind；Windows 用 choco install kind；kind version 驗證。

**標籤：** #brew #choco

Kind的安裝方式是簡單的，並且不同於您的運作系統上的方統。Linux使用者，您可以下載Kind的組合用Curl,，使用Chmod的按鍵，然後將它移到您的本地的bin中心。MacOS使用者，最簡單的方法是用Homebrew,，simply running brew install kind。Windows使用者可以使用Chocolaty，使用Chocolaty的按鍵，然後按下Choco,，在安裝後，確認Kind正式安裝，按照Kind Version的指令在您的電腦中執行。這會顯示安裝版本，並確認Kind已經準備使用。

**中譯：** Kind 的安裝方式依作業系統而異。Linux 使用者可用 curl 下載執行檔，以 chmod 設為可執行，再移到本機的 bin 目錄。macOS 最簡單的方式是 Homebrew，執行 brew install kind。Windows 使用者可用 Chocolatey，執行 choco install kind。安裝完成後，執行 kind version 確認安裝版本，Kind 即可使用。

### 投影片 5：建立第一個叢集（02:35–03:20）

![02:35](frames/frame_0028.jpg)

**重點：** kind create cluster；--name 自訂名稱；kubectl cluster-info --context 驗證。

**標籤：** #kind create cluster

在Kind上，您的第一個Kubernetes團隊建立是非常簡單的。最基本的指令是Kind Create Cluster,，建立一個單元團隊，以Kind為主要名稱。如果您想要定義您的團隊的定義名稱，使用--名字的標籤，然後選擇您想要的cluster名字，例如我的cluster，當cluster創立後，KIND會自動設定kubectl來與它連線，您可以確認cluster正在運作，使用kubectl Cluster Info的指令，以適合的 context，context名字跟隨KIND的模式，然後選擇cluster名字，這次的確認方法，確保cluster是在用後，正在運作。

**中譯：** 用 Kind 建立第一個 Kubernetes 叢集非常簡單。最基本的指令是 kind create cluster，會建立名為 kind 的單節點叢集。若想自訂叢集名稱，加上 --name 參數與名稱，例如 my-cluster。叢集建立後，Kind 會自動設定 kubectl 與它連線，可用 kubectl cluster-info 搭配對應的 context 確認叢集正在運作。

### 投影片 6：多節點叢集設定（03:20–04:16）

![03:20](frames/frame_0035.jpg)

**重點：** YAML 定義 1 個 control-plane 與 3 個 worker；kind create cluster --config。

**標籤：** #YAML #control plane #worker

While single node clusters are useful, Kind really shines when creating multi-node clusters for more realistic testing scenarios. To create a multi-node cluster, you need to define a configuration file in YAML format. This configuration file specifies the cluster kind and API version, followed by a node section where you define the roles of each node. You can specify one control plane node and multiple worker nodes. 例如，您可能要安裝一個控制平面的核心和三個工作節點來模仿一個像生產的環境。當您建立了您的設定圖片時，直接按用--configure-cluster的--configuree worker nodes to simulate a production-like environment.Once you've created your configuration file,simply run kind create cluster with the dash dash config flag pointing to your YAML file. Kind will then create all the specified nodes as separate Docker containers and configure them into a functioning multi-node Kubernetes cluster.

**中譯：** 單節點叢集很實用，但 Kind 真正的優勢在於建立多節點叢集，以進行更貼近真實的測試。要建立多節點叢集，需要寫一個 YAML 設定檔，指定叢集的 kind 與 API 版本，接著在 nodes 區段定義各節點的角色。可設定一個 control-plane 節點與多個 worker 節點，例如一個控制平面加三個工作節點，來模擬類似正式環境的架構。建好設定檔後，執行 kind create cluster --config 並指向該 YAML 檔。Kind 會把每個指定的節點建立成獨立的 Docker 容器，並組成可運作的多節點 Kubernetes 叢集。

### 投影片 7：連接埠對應設定（04:16–05:08）

![04:16](frames/frame_0045.jpg)

**重點：** extraPortMappings：容器 80→主機 8080、443→8443，協定 TCP。

**標籤：** #extraPortMappings

One important aspect of working with Kind 是在你的框架內在你的主項中使用的服務。 這就是透過框架設定的設定。 在你的框架設定檔案中， 你可以在控制框架的專案下， 加入一個新的框架設定。 這裡，您可以指定哪些框架的框架 應該被選擇為主項的框架。 例如，您可能選擇框架框80 為http的框架8080, container port 443 to host port 8443 for HTTPS traffic. You also specify the protocol, typically TCP. This configuration allows you to access services running inside your KIND cluster directly from your local machine's browser or other tools, making development and testing much more convenient.

**中譯：** 使用 Kind 的一個重點，是如何從主機存取叢集內的服務，這要透過叢集設定檔中的 port mapping（連接埠對應）。在設定檔的 control-plane 節點下加入 extraPortMappings，指定哪些容器連接埠要對應到主機連接埠。例如把容器連接埠 80 對應到主機 8080 作為 HTTP，容器連接埠 443 對應到主機 8443 作為 HTTPS，並指定協定（通常是 TCP）。這樣就能從本機瀏覽器或其他工具直接存取 Kind 叢集內執行的服務，讓開發與測試更方便。

### 投影片 8：叢集管理指令（05:08–05:49）

![05:08](frames/frame_0053.jpg)

**重點：** get clusters、get nodes、delete cluster、export/get kubeconfig、load docker-image。

**標籤：** #kind load docker-image

Managing your KIND clusters is straightforward with several essential commands. 用kind-get-clusters去列出所有你的kind-clusters 用kubectl-get-nodes去看nodes 如果您需要刪除一個cluster 用kind-delete-cluster 用--name-flag 指定哪個cluster要刪除 kind-export-kubeconfig 指令 輸入cluster的設定到kubeconfig的檔案 而kind-get-kubeconfig 指令展示kubeconfig的路線 特別有用的指令是kind-load-docker-image 使用Docker的畫面直接進入你的圖層核檔 不需要連線到聯結器 這非常有用於發展.

**中譯：** 管理 Kind 叢集有幾個基本指令：kind get clusters 列出所有叢集，kubectl get nodes 查看節點。要刪除叢集用 kind delete cluster，並以 --name 指定要刪除的叢集。kind export kubeconfig 會把叢集設定匯出到 kubeconfig 檔，kind get kubeconfig 則顯示 kubeconfig 的內容。特別實用的是 kind load docker-image，可把本機 Docker 映像檔直接載入叢集節點，不需要推送到映像檔倉庫，對經常建置與測試容器映像檔的開發很有幫助。

### 投影片 9：kubectl context 管理（05:49–06:42）

![05:49](frames/frame_0061.jpg)

**重點：** context 以 kind- 為前綴；get-contexts、use-context、current-context。

**標籤：** #context

經常建立和測試圖層畫面理解區域的環境是重要的尤其是如果您管理and testing container images.Understanding kubectl contexts is crucial when working with KIND,especially if you manage multiple clusters. KIND automatically creates and configures kubectl contexts for your clusters, always prefixing them with KIND followed by the cluster name. To view all available contexts, use kubectl config get contexts. This shows you all configured clusters and highlights your current context. 用kubectl Config用的用途， 跟著用途名稱， 例如Kind My Cluster。 快速檢視您目前關係的圖片， 按kubectl Config的現時途徑。 管理途徑， 確保您一直在用途的圖片， 防止錯誤的環境中有錯誤的改變。.

**中譯：** 同時管理多個叢集時，理解 kubectl context 很重要。Kind 會自動為叢集建立並設定 kubectl context，名稱一律以 kind- 開頭，後面接叢集名稱。用 kubectl config get-contexts 查看所有 context 與目前使用的 context。用 kubectl config use-context 加上 context 名稱（例如 kind-my-cluster）切換；用 kubectl config current-context 查看目前所在的 context。管理好 context 可確保你始終在正確的叢集上操作，避免在錯誤環境中做出錯誤變更。

### 投影片 10：常見使用情境（06:42–07:38）

![06:42](frames/frame_0070.jpg)

**重點：** 本機開發、測試與 CI/CD、學習 Kubernetes、展示與概念驗證。

**標籤：** #CI/CD

Kind是非常可靠的，並且服務在Kubernetes的系統中有許多重要的用途。 為了開發區域，它提供一個完全的Kubernetes環境，不需要承受 cloud 費用，讓您可以測試您的應用程式，在與生產生產的關係上，近視。 在測試和繼續的運輸流程中，Kind能夠進行自動測試，以使用的細胞圖表可以快速創造和破壞。 For learning Kubernetes, Kind offers a safe sandbox environment where you can experiment with various Kubernetes concepts and configurations without fear of breaking anything important. Finally, for demonstrations and proof of concepts, Kind allows for quick setup of working Kubernetes environments that can showcase your applications or ideas effectively. These use cases make Kind an essential tool in any Kubernetes developer's toolkit.

**中譯：** Kind 非常可靠，用途廣泛。本機開發：提供完整的 Kubernetes 環境而不必負擔雲端費用，可在接近正式環境的條件下測試應用程式。測試與 CI/CD：可自動化測試，叢集能快速建立與銷毀。學習 Kubernetes：提供安全的沙箱，可放心實驗各種概念與設定，不怕弄壞重要資源。展示與概念驗證：可快速建立可運作的 Kubernetes 環境，有效展示你的應用或想法。這些用途讓 Kind 成為 Kubernetes 開發者工具箱中不可或缺的工具。

### 投影片 11：片尾（07:38–07:55）

![07:38](frames/frame_0079.jpg)

**重點：** 請觀眾按讚、訂閱、轉發（非教學內容）。

請不吝點贊 訂閱 轉發 打賞支援明鏡與點點欄目。

**中譯：** 請不吝點讚、訂閱、轉發、打賞（片尾版權宣傳語）。

## 已知轉錄錯誤

| 時間 | 聽成 | 應為 |
|---|---|---|
| 00:02 | KIND是Docker的Kubernetes | Kind 即 Kubernetes in Docker |
| 00:30 | 專用的專用團體／核檔 | （原文：容器節點／叢集，Whisper 誤聽嚴重，以中譯與投影片為準） |
| 02:40 | 團隊／單元團隊 | cluster（叢集）；推測 |
| 04:16 | 框架／主項 | port mapping／host（連接埠對應／主機）；推測 |
| 07:38 | 明鏡與點點欄目 | 片尾宣傳語，非教學內容 |
