# 希望金科基础服务：

1. 短信通知服务 
2. ip归属地服务 
3. 手机归属地服务 
4. 其他

## 部署说明

### 坏境变量

- ZK_SERVERS
- HOST

## zookeeper

``` json
{
    "CUR_ENV" : "dev", 
    "CHAOS_DB" : "mysql+pymysql://xxx/xx/xxx/", 
    "SENTRY_DNS" : "", 
    "REDIS_URL" : "redis://////", 
    "LOG_DB" : "mysql+pymysql://xxx/xx/xxx/", 
    "SQLALCHEMY_TRACK_MODIFICATIONS" : "", 
    "SQLALCHEMY_POOL_SIZE" : "", 
    "VERIFY_CODE_EXPIRE" : "", 
}
```
CUR_ENV ( local 本地开发环境，dev 联调环境 test 测试环境  prod 生产环境)

### 开发模式启动

make dev

### 生产模式启动

gunicorn src.main:app -b 0.0.0.0:10160 -k meinheld.gmeinheld.MeinheldWorker
