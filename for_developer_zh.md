# for development

## vue

```bash
cd vue-app
npm install
npm run format
npm run dev
```

## 用idl生成代码

### 生成python代码

```bash
docker run --rm \
    -v "${PWD}:/local" \
    openapitools/openapi-generator-cli generate \
    -i /local/idl/openapiv3.yaml \
    -g python-fastapi \
    -o /local/gen/py
```

### 生成 typescript 代码

```bash
docker run --rm \
 -v "${PWD}:/local" \
 openapitools/openapi-generator-cli generate \
 -i /local/idl/openapiv3.yaml \
 -g typescript-fetch \
 -o /local/gen/ts
```

### 单元测试

```bash
npm run test:unit
```

### 新增后端api接口

1. 编写 openapiv3.yaml，生成 python 代码
2. 在 `backend/console/handler` 新建文件，编写 handler
3. 在 `gen/py/src/openapi_server/impl/starroll_impl.py`注册新的handler
