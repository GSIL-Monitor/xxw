## 服务名称

反欺诈平台

## 服务简介

反欺诈平台数据大屏，控制中心，策略中心接口


## 使用文档

### 目录结构

- README.md 服务说明文件，包含服务的名称，说明，作者，使用文档
- requirements.txt 依赖库，所有依赖必须指定版本号
- Dockerfile Docker 镜像文件
- docker-compose.yml 服务编排文件
- .gitignore git 忽略文件，排除掉各种多余的文件，比如临时文件，编辑器状态文件等，只保留本文档给的目录结构
- tests/ 测试用例目录
- src/main.py 服务主文件，入口文件，启动文件，zk配置
- src/modules/ 服务的各个子模块
- src/commons/ 公共文件，通用函数

### 开发

1. 环境准备: Python==3.6.5, pip==10.0.1, libev
2. 安装依赖: pip install -r requirements.txt
3. 开发模式启动 make dev

### 文档地址

https://documenter.getpostman.com/view/828172/RWMJqmti

### 模型定义

http://gitlab.xwfintech.com/backend/fraud-api/blob/master/src/models.py