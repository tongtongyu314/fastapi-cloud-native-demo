# FastAPI 云原生演示项目

用于学习本地 k3s + Helm + Argo CD + Prometheus 的最小 FastAPI 示例。不含数据库和业务逻辑。

## 项目结构

```
.
├── app/
│   ├── __init__.py
│   ├── config.py          # 环境变量配置（PORT / APP_ENV / APP_VERSION）
│   └── main.py            # FastAPI 应用 + Prometheus 指标中间件
├── tests/
│   └── test_main.py       # 基础接口测试
├── k8s/                   # 裸 YAML
│   ├── namespace.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── charts/fastapi-demo/   # Helm Chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── .github/workflows/ci.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 接口

| 方法 | 路径        | 说明                                          |
| ---- | ----------- | --------------------------------------------- |
| GET  | `/`         | 返回 `{service, version, env}`                |
| GET  | `/health`   | 返回 `{"status": "ok"}`，用于存活/就绪探针    |
| GET  | `/info`     | 返回版本、环境、hostname                      |
| GET  | `/metrics`  | Prometheus 指标（http_requests_total 等）     |

## 本地运行

### 1. 直接用 uvicorn 启动

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

环境变量：

```bash
PORT=8000 APP_ENV=dev APP_VERSION=0.1.0 python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 运行测试

```bash
pip install pytest httpx
pytest -v
```

## Docker

### 构建镜像

```bash
docker build -t fastapi-cloud-native-demo:0.1.0 .
```

### 运行容器

```bash
docker run -d --name fastapi-demo -p 8000:8000 \
  -e APP_ENV=dev -e APP_VERSION=0.1.0 \
  fastapi-cloud-native-demo:0.1.0
```

## Kubernetes（裸 YAML）

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

本地验证（端口转发）：

```bash
kubectl -n fastapi-demo port-forward svc/fastapi-demo 8000:8000
```

## Helm

```bash
helm install fastapi-demo ./charts/fastapi-demo -n fastapi-demo --create-namespace
```

常用覆盖：

```bash
helm upgrade --install fastapi-demo ./charts/fastapi-demo -n fastapi-demo \
  --set image.repository=my-registry/fastapi-cloud-native-demo \
  --set image.tag=0.1.0 \
  --set service.port=8000 \
  --set ingress.enabled=true \
  --set ingress.host=fastapi-demo.local
```

渲染模板（不实际部署）：

```bash
helm template fastapi-demo ./charts/fastapi-demo
```

## Argo CD 接入（后续）

1. 将本仓库推送到 Git。
2. 在 Argo CD 中创建 Application，指向仓库的 `charts/fastapi-demo` 或 `k8s/` 目录。
3. 配置自动同步（Auto-Sync + Self-Heal），观察 Argo CD 拉起 Deployment。
4. 后续可通过修改 `values.yaml` 或 `k8s/*.yaml` 触发 GitOps 同步。

示例 Application：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: fastapi-demo
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/<your-user>/fastapi-cloud-native-demo.git
    targetRevision: main
    path: charts/fastapi-demo
  destination:
    server: https://kubernetes.default.svc
    namespace: fastapi-demo
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## Prometheus 接入

`/metrics` 端点暴露 `http_requests_total` 和 `http_request_duration_seconds`，Prometheus 可直接抓取。在 k3s 中若已安装 kube-prometheus-stack，可配置 ServiceMonitor 指向 `fastapi-demo` 服务的 8000 端口 `/metrics` 路径。

## 验证命令

服务启动后（本地或端口转发），执行：

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/info
curl http://localhost:8000/metrics
```

预期返回：

```bash
$ curl http://localhost:8000/
{"service":"fastapi-cloud-native-demo","version":"0.1.0","env":"dev"}

$ curl http://localhost:8000/health
{"status":"ok"}

$ curl http://localhost:8000/info
{"version":"0.1.0","env":"dev","hostname":"<hostname>"}

$ curl http://localhost:8000/metrics | grep http_requests_total
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/health",method="GET",status="200"} 1.0
```
