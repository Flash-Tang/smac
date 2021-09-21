# 基于星际争霸II的多智能体强化学习

## 配置

1. **星际争霸环境**

   + [ ] 下载星际争霸2，链接：[Battle.net](https://battle.net/).

   + [ ] 创建虚拟环境

     ```shell
     virtualenv venv --python=python3.5
     source venv/bin/activate
     pip install gym==0.10.5
     pip install tensorflow==1.8.0
     pip install numpy==1.14.5
     ```

   + [ ] 下载本git仓库

     https://github.com/Flash-Tang/smac.git

   + [ ] 下载自定义地图

     [地图链接](https://github.com/oxwhirl/smac/releases/download/v0.1-beta1/SMAC_Maps.zip)

   + [ ] 下载星际争霸地图编辑器

2. **算法**

   + [ ] 下载MADDPG源代码

     ```shell
     git clone https://github.com/openai/maddpg.git
     cd maddpg
     pip install -e .
     ```

3. **mininet工具**

## 使用

### 训练

+ smac/smac/experiments/train_agents.py

+ smac/smac/experiments/train_goup_leader.py

  以上两个命令分别在experiments/policy文件夹下生成模型文件

**Mininet网络仿真**

+ smac/smac/experiments/com_with_mn.py

**对抗**

+ smac/smac/experiments/battle.py

## 环境

+ SMAC（一个定制化的星际争霸环境，着重于mini-game而非星际争霸完整游戏）
+ [原版SMAC地址](https://github.com/oxwhirl/smac)

## 算法

1. MADDPG

   + Multi-Agent Deep Deterministic Policy Gradient (MADDPG)

   + [算法实现](https://github.com/openai/maddpg)

   + 配置：

     ```shell
     git clone https://github.com/openai/maddpg.git
     cd maddpg
     pip install -e .
     ```

2. 