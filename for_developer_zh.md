# for development

## 工作流程

每当你开始开发一个需求时：

1. 你【必须】先设计你写的功能的接口，更新 openapiv3.yaml
2. 完成该功能的技术设计，【可以】拉一个会议，让大家一起评审一下。
3. 对于复杂的需求，或需要和其他同学合作的需求，【应该】写一个技术文档。将文档地址贴在jira上对应的条目里
4. 你【应该】先写单元测试，再完成你的功能。你【必须】在提交代码时带上你的单元测试。
5. 最后你【必须】发起 pull request。你【必须】将 pull request 的链接贴到对应需求的jira记录里。并将该jira记录的链接和 pull request 链接一起发到群里请求大家review。 你【必须】跟踪该 pull request，根据大家的意见修改并最终合并。

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
    openapitools/openapi-generator-cli:v7.18.0 generate \
    -i /local/idl/openapiv3.yaml \
    -g python-fastapi \
    -o /local/gen/py
```

### 生成 typescript 代码

```bash
docker run --rm \
 -v "${PWD}:/local" \
 openapitools/openapi-generator-cli:v7.18.0 generate \
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
