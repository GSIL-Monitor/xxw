# B 端用户中心

## 接口说明

### 执行
项目根目录下执行 `make db` 初始化数据库，写入基本数据
将 stdout 里面的 权限系统 appid 记录发送给前端
将 超级用户 密码记录 给权限拥有者

## 环境变量说明

### 数据库

####  mysql

- DATABASE_NAME: mysql 名
- DATABASE_USER: mysql 用户名
- DATABASE_HOST: mysql host
- DATABASE_PORT: mysql 端口
- DATABASE_PASSWORD: mysql 密码

#### redis

- REDIS_HOST: redis host
- REDIS_PORT: redis 端口
- REDIS_PASSWORD: redis 密码

### celery

- CELERY_BROKER_URL: celery 地址， 使用 redis 地址即可，'redis://localhost:6379'
- CELERY_RESULT_BACKEND: celery, 使用 redis 地址即可， 'redis://localhost:6379'

### sentry

- SENTRY_DSN： sentry 地址

### host 访问限制

- HOSTS: 格式 "host," 或 "host,host" 或 "*"
