# videoplayback (2).mp4

_Source: whisper (groq)._

```
[00:00] 歡迎來到KIND的這個影片，
[00:02] KIND是Docker的Kubernetes。
[00:04] KIND是一個能夠讓你使用的很輕鬆的
[00:07] Local Kubernetes Cluster
[00:09] 在你的發展設計中使用的很強大的工具。
[00:11] 在這個影片中，
[00:12] 你將學習如何設定KIND,
[00:14] 並使用它來建立Kubernetes Cluster
[00:16] 在Docker的包裝內。
[00:18] 這非常有用於測試、學習和
[00:21] 在區域發展上的課程，
[00:23] 不需要費用的 cloud 資源
[00:25] 或細勝的 virtual machine 設定。
[00:30] Kind是一個特別設計為使用Docker團體核檔用的專用的專用團體
[00:37] 原來是為了測試Kubernetes,它成為了專用的專用團體和繼續的運輸流程的一個選擇
[00:46] 而不是用專用的產品，Kind使用Docker團體來模擬Kubernetes的核檔，使它非常快速和有資源
[00:55] KIND的重要優點包括快速的圖案創造、
[00:59] 比較傳統的機器基礎系統上的低重量使用、
[01:03] 支援多核檔的圖案，
[01:06] 並且它是完美的測試您的應用程式
[01:08] 在一種實際的Kubernetes環境中。
[01:13] 在KIND的安裝前，您必須確保您的系統遵守了一定的要求。
[01:18] 首先，您必須將Docker Engine安裝和在您的機器上執行。
[01:22] 20.10或高的版本是推薦以最高的配置
[01:27] 第二，您需要Kubectl,
[01:29] 是Kubernetes的指令線工具
[01:32] 使用於您的粒子中的互動
[01:34] 確保您設定在您計劃運作的
[01:37] Kubernetes Cluster版本上的配置
[01:40] 最後，確保您的系統有足夠的資源
[01:43] 至少2GB的RAM和20GB的可用的Disk Space
[01:48] 這些要求確保您的Kind Clusters順暢運作
[01:52] Kind的安裝方式是簡單的，並且不同於您的運作系統上的方統。Linux使用者，您可以下載Kind的組合用Curl,
[02:03] 使用Chmod的按鍵，
[02:06] 然後將它移到您的本地的bin中心。
[02:09] MacOS使用者，
[02:10] 最簡單的方法是用Homebrew,
[02:13] simply running brew install kind。
[02:15] Windows使用者可以使用Chocolaty
[02:18] 使用Chocolaty的按鍵，
[02:20] 然後按下Choco,
[02:21] 在安裝後，確認Kind正式安裝，
[02:25] 按照Kind Version的指令在您的電腦中執行。
[02:28] 這會顯示安裝版本，
[02:31] 並確認Kind已經準備使用。
[02:35] 在Kind上，您的第一個Kubernetes團隊建立是非常簡單的。
[02:40] 最基本的指令是Kind Create Cluster,
[02:43] 建立一個單元團隊，
[02:45] 以Kind為主要名稱。
[02:47] 如果您想要定義您的團隊的定義名稱，
[02:50] 使用--名字的標籤，然後選擇您想要的cluster名字，例如我的cluster
[02:56] 當cluster創立後，KIND會自動設定kubectl來與它連線
[03:01] 您可以確認cluster正在運作
[03:05] 使用kubectl Cluster Info的指令，以適合的 context
[03:09] context名字跟隨KIND的模式，然後選擇cluster名字
[03:14] 這次的確認方法，確保cluster是在用後，正在運作
[03:20] While single node clusters are useful,
[03:24] Kind really shines when creating multi-node clusters
[03:27] for more realistic testing scenarios.
[03:30] To create a multi-node cluster,
[03:31] you need to define a configuration file in YAML format.
[03:36] This configuration file specifies the cluster kind and API version,
[03:41] followed by a node section where you define the roles of each node.
[03:44] You can specify one control plane node and multiple worker nodes.
[03:48] 例如，您可能要安裝一個控制平面的核心和三個工作節點來模仿一個像生產的環境。當您建立了您的設定圖片時，直接按用--configure-cluster的--configuree worker nodes to simulate a production-like environment.Once you've created your configuration file,simply run kind create cluster with the dash dash config flag pointing to your YAML file.
[04:06] Kind will then create all the specified nodes as separate Docker containers
[04:10] and configure them into a functioning multi-node Kubernetes cluster.
[04:16] One important aspect of working with Kind
[04:19] 是在你的框架內在你的主項中使用的服務。
[04:23] 這就是透過框架設定的設定。
[04:27] 在你的框架設定檔案中，
[04:29] 你可以在控制框架的專案下，
[04:31] 加入一個新的框架設定。
[04:33] 這裡，您可以指定哪些框架的框架
[04:36] 應該被選擇為主項的框架。
[04:38] 例如，您可能選擇框架框80
[04:41] 為http的框架8080,
[04:44] container port 443 to host port 8443 for HTTPS traffic.
[04:50] You also specify the protocol, typically TCP.
[04:54] This configuration allows you to access services running inside your KIND cluster directly from your local machine's browser or other tools,
[05:02] making development and testing much more convenient.
[05:08] Managing your KIND clusters is straightforward with several essential commands.
[05:12] 用kind-get-clusters去列出所有你的kind-clusters
[05:15] 用kubectl-get-nodes去看nodes
[05:19] 如果您需要刪除一個cluster
[05:21] 用kind-delete-cluster
[05:22] 用--name-flag 指定哪個cluster要刪除
[05:26] kind-export-kubeconfig 指令
[05:29] 輸入cluster的設定到kubeconfig的檔案
[05:32] 而kind-get-kubeconfig 指令展示kubeconfig的路線
[05:36] 特別有用的指令是kind-load-docker-image
[05:40] 使用Docker的畫面直接進入你的圖層核檔
[05:43] 不需要連線到聯結器
[05:46] 這非常有用於發展
[05:49] 經常建立和測試圖層畫面理解區域的環境是重要的尤其是如果您管理and testing container images.Understanding kubectl contexts is crucial when working with KIND,especially if you manage multiple clusters.
[06:02] KIND automatically creates and configures kubectl contexts for your clusters,
[06:07] always prefixing them with KIND followed by the cluster name.
[06:11] To view all available contexts, use kubectl config get contexts.
[06:15] This shows you all configured clusters and highlights your current context.
[06:20] 用kubectl Config用的用途， 跟著用途名稱， 例如Kind My Cluster。
[06:28] 快速檢視您目前關係的圖片， 按kubectl Config的現時途徑。
[06:34] 管理途徑， 確保您一直在用途的圖片， 防止錯誤的環境中有錯誤的改變。
[06:42] Kind是非常可靠的，並且服務在Kubernetes的系統中有許多重要的用途。
[06:50] 為了開發區域，它提供一個完全的Kubernetes環境，不需要承受 cloud 費用，讓您可以測試您的應用程式，在與生產生產的關係上，近視。
[07:01] 在測試和繼續的運輸流程中，Kind能夠進行自動測試，以使用的細胞圖表可以快速創造和破壞。
[07:11] For learning Kubernetes, Kind offers a safe sandbox environment where you can experiment with various Kubernetes concepts and configurations without fear of breaking anything important.
[07:23] Finally, for demonstrations and proof of concepts, Kind allows for quick setup of working Kubernetes environments that can showcase your applications or ideas effectively.
[07:34] These use cases make Kind an essential tool in any Kubernetes developer's toolkit.
[07:38] 請不吝點贊 訂閱 轉發 打賞支援明鏡與點點欄目
```
