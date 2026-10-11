# videoplayback (2).mp4

_Source: whisper (groq)._

```
[00:00] 欢迎来到KIND的这个视频,
[00:02] KIND是Docker的Kubernetes。
[00:04] KIND是一个能够让你使用的很轻松的
[00:07] Local Kubernetes Cluster
[00:09] 在你的发展设计中使用的很强大的工具。
[00:11] 在这个视频中,
[00:12] 你将学习如何设置KIND,
[00:14] 并使用它来创建Kubernetes Cluster
[00:16] 在Docker的包装内。
[00:18] 这非常有用于测试、学习和
[00:21] 在区域发展上的课程,
[00:23] 不需要费用的 cloud 资源
[00:25] 或细胜的 virtual machine 设置。
[00:30] Kind是一个特别设计为使用Docker团体核档用的专用的专用团体
[00:37] 原来是为了测试Kubernetes,它成为了专用的专用团体和继续的运输流程的一个选择
[00:46] 而不是用专用的产品,Kind使用Docker团体来模拟Kubernetes的核档,使它非常快速和有资源
[00:55] KIND的重要优点包括快速的图案创造、
[00:59] 比较传统的机器基础系统上的低重量使用、
[01:03] 支持多核档的图案,
[01:06] 并且它是完美的测试您的应用程序
[01:08] 在一种实际的Kubernetes环境中。
[01:13] 在KIND的安装前,您必须确保您的系统遵守了一定的要求。
[01:18] 首先,您必须将Docker Engine安装和在您的机器上运行。
[01:22] 20.10或高的版本是推薦以最高的配置
[01:27] 第二,您需要Kubectl,
[01:29] 是Kubernetes的指令線工具
[01:32] 使用於您的粒子中的互動
[01:34] 確保您設置在您計劃運作的
[01:37] Kubernetes Cluster版本上的配置
[01:40] 最後,確保您的系統有足夠的資源
[01:43] 至少2GB的RAM和20GB的可用的Disk Space
[01:48] 這些要求確保您的Kind Clusters順暢運作
[01:52] Kind的安装方式是简单的,并且不同于您的运作系统上的方统。Linux用户,您可以下载Kind的组合用Curl,
[02:03] 使用Chmod的按键,
[02:06] 然后将它移到您的本地的bin中心。
[02:09] MacOS用户,
[02:10] 最简单的方法是用Homebrew,
[02:13] simply running brew install kind。
[02:15] Windows用户可以使用Chocolaty
[02:18] 使用Chocolaty的按键,
[02:20] 然后按下Choco,
[02:21] 在安装后,确认Kind正式安装,
[02:25] 按照Kind Version的指令在您的电脑中运行。
[02:28] 这会显示安装版本,
[02:31] 并确认Kind已经准备使用。
[02:35] 在Kind上,您的第一个Kubernetes团队创建是非常简单的。
[02:40] 最基本的指令是Kind Create Cluster,
[02:43] 创建一个单元团队,
[02:45] 以Kind为主要名称。
[02:47] 如果您想要定义您的团队的定义名称,
[02:50] 使用--名字的標籤,然後選擇您想要的cluster名字,例如我的cluster
[02:56] 當cluster創立後,KIND會自動設定QBectal來與它連接
[03:01] 您可以確認cluster正在運作
[03:05] 使用QBectal Cluster Info的指令,以適合的 context
[03:09] context名字跟隨KIND的模式,然後選擇cluster名字
[03:14] 這次的確認方法,確保cluster是在用後,正在運作
[03:20] While single node clusters are useful,
[03:24] Kind really shines when creating multi-node clusters
[03:27] for more realistic testing scenarios.
[03:30] To create a multi-node cluster,
[03:31] you need to define a configuration file in YAML format.
[03:36] This configuration file specifies the cluster kind and API version,
[03:41] followed by a node section where you define the roles of each node.
[03:44] You can specify one control plane node and multiple worker nodes.
[03:48] 例如,您可能要安装一个控制棚的核心和三个工作核心来模仿一个像生产的环境。当您创建了您的设置图片时,直接按用--configure-cluster的--configuree worker nodes to simulate a production-like environment.Once you've created your configuration file,simply run kind create cluster with the dash dash config flag pointing to your YAML file.
[04:06] Kind will then create all the specified nodes as separate Docker containers
[04:10] and configure them into a functioning multi-node Kubernetes cluster.
[04:16] One important aspect of working with Kind
[04:19] 是在你的框架内在你的主项中使用的服务。
[04:23] 这就是通过框架设定的设定。
[04:27] 在你的框架设定文件中,
[04:29] 你可以在控制框架的项目下,
[04:31] 加入一个新的框架设定。
[04:33] 这里,您可以指定哪些框架的框架
[04:36] 应该被选择为主项的框架。
[04:38] 例如,您可能选择框架框80
[04:41] 为http的框架8080,
[04:44] container port 443 to host port 8443 for HTTPS traffic.
[04:50] You also specify the protocol, typically TCP.
[04:54] This configuration allows you to access services running inside your KIND cluster directly from your local machine's browser or other tools,
[05:02] making development and testing much more convenient.
[05:08] Managing your KIND clusters is straightforward with several essential commands.
[05:12] 用kind-get-clusters去列出所有你的kind-clusters
[05:15] 用cubectl-get-nodes去看nodes
[05:19] 如果您需要删除一个cluster
[05:21] 用kind-delete-cluster
[05:22] 用--name-flag 指定哪个cluster要删除
[05:26] kind-export-cubiconfig 指令
[05:29] 输入cluster的设定到cubiconfig的档案
[05:32] 而kind-get-cubiconfig 指令展示cubiconfig的路线
[05:36] 特别有用的指令是kind-load-docker-image
[05:40] 使用Docker的画面直接进入你的图层核档
[05:43] 不需要连接到连接器
[05:46] 这非常有用于发展
[05:49] 经常建立和测试图层画面理解区域的环境是重要的尤其是如果您管理and testing container images.Understanding cubectal contexts is crucial when working with KIND,especially if you manage multiple clusters.
[06:02] KIND automatically creates and configures cubectal contexts for your clusters,
[06:07] always prefixing them with KIND followed by the cluster name.
[06:11] To view all available contexts, use cubectal config get contexts.
[06:15] This shows you all configured clusters and highlights your current context.
[06:20] 用Cubectl Config用的用途, 跟着用途名称, 例如Kind My Cluster。
[06:28] 快速查看您目前关系的图片, 按Cubectl Config的现时途径。
[06:34] 管理途径, 确保您一直在用途的图片, 防止错误的环境中有错误的改变。
[06:42] Kind是非常可靠的,并且服务在Kubernetes的系统中有许多重要的用途。
[06:50] 为了开发区域,它提供一个完全的Kubernetes环境,不需要承受 cloud 费用,让您可以测试您的应用程序,在与生产生产的关系上,近视。
[07:01] 在测试和继续的运输流程中,Kind能够进行自动测试,以使用的细胞图表可以快速创造和破坏。
[07:11] For learning Kubernetes, Kind offers a safe sandbox environment where you can experiment with various Kubernetes concepts and configurations without fear of breaking anything important.
[07:23] Finally, for demonstrations and proof of concepts, Kind allows for quick setup of working Kubernetes environments that can showcase your applications or ideas effectively.
[07:34] These use cases make Kind an essential tool in any Kubernetes developer's toolkit.
[07:38] 请不吝点赞 订阅 转发 打赏支持明镜与点点栏目
```
