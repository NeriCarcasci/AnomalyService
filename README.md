# Anomaly Detection Service

## **Overview**
This repository contains an anomaly detection API built with FastAPI, MongoDB, and OpenShift.

<br>

<br>

## **1. Setup**
The steps I used from 0 to working deployment

### **1.1 Prerequisites**
- Python 3.10+ (Homebrew python is the worse thing I have witnessed)
- OpenShift CLI (`oc`)
- MongoDB Atlas account (or local MongoDB instance) -- Google Firestore can be used too
- FastAPI & dependencies

### **1.2 Installation**
#### **1️⃣ Clone the repository**
```sh
git clone https://github.com/NeriCarcasci/AnomalyService.git
cd AnomalyService
```
if changing the python then rebuild container image with
` podman build --platform linux/amd64 -t quay.io/ncarcasc/anomaly-detection:latest .`
where the --platform is needed if you are building for Openshift coming from a MacOS. And then publish to quay.io with
` podman push quay.io/ncarcasc/anomaly-detection:latest`

#### **2️⃣ Create a virtual environment & install dependencies**
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt # or one by one as mentioned in docker file
```

#### **3️⃣ Setup to OpenShift**
```sh
oc new-project anomaly-detection
```

#### **4️⃣ Setup MongoDB Connection**
1. If using MongoDB Atlas, **whitelist your OpenShift cluster's IP**.
2. Save your MongoDB URI as a env viariable (or modify `MONGO_URI` in `main.py`):
```sh
oc set env deployment/anomaly-detection MONGO_URI="mongodb+srv://USERNAME:PASSWORD@maincluster.g70a1.mongodb.net/DATABASE?retryWrites=true&w=majority&appName=maincluster" -n anomaly-detection
```

#### **5️⃣ Apply YAML to openshift**
using `oc apply -f [file]`:
1. Apply `deployment.yaml`
2. Apply `service.yaml`
3. Apply `route.yaml`

   
#### **6️⃣ Verify Deplyment & Test API Locally**
```sh
oc get pods -n anomaly-detection
```
Check logs if things explode:
```sh
oc logs -f deployment/anomaly-detection -n anomaly-detection
```

<br>

---

<br>

## **2. Debug - Problems Encountered**
If tests fail, comment out testing functions. They are clearly the problem. 😎

### **Common Errors & Fixes**
| Error ID | Error Title |
|----------|------------|
| [1] | MongoDB Authentication Failure |
| [2] | OpenShift Route Not Working |
| [3] | SSL Handshake Failure |
| [4] | Internal Server Error on `/detect-anomalies` |

See appendix for details on each issue and how to fix them.
<br>
---
<br>

## **3. Documentation**

### **3.1 Code Structure**
- `main.py`: API endpoints & logic
- `models.py`: Data models for API requests
- `db.py`: MongoDB connection functions
- `tests/`: Unit tests for API functions

### **3.2 Why These Choices?**
✔ **NumPy over SciPy** → Avoid `norm.pdf()` and maths issues that kept me up at night 
✔ **MongoDB instead of MinIO** → Persistence without waiting 2 hours for minIO operator to install, google firebase is okay too
<br>

---

<br>

# 📌 OpenShift Deployment YAML Explained

## **1️⃣ Deployment (`deployment.yaml`)**
This file defines the **OpenShift Deployment** for the `anomaly-detection` service.
This deployment **runs a single instance** of `anomaly-detection`, using the latest container image from Quay.io, **exposing port 8080**.
I broke it down into different parts to understand it.

```yaml
metadata:
  name: anomaly-detection
  namespace: anomaly-detection
```
- `name`: Specifies the **name of the deployment** (`anomaly-detection`).
- `namespace`: Defines the **namespace** where this deployment is created (`anomaly-detection`).

```yaml
spec:
  replicas: 1
```
- `replicas`: Specifies **how many instances (pods) of the application** should run at the same time. Here, it's set to **1**.

```yaml
  selector:
    matchLabels:
      app: anomaly-detection
```
- This ensures that the deployment manages pods that **match the given labels** (`app: anomaly-detection`).

```yaml
  template:
    metadata:
      labels:
        app: anomaly-detection
```
- The `template` defines **how each pod is structured**.
- `labels` help OpenShift **identify and group pods** under the `anomaly-detection` app.

```yaml
    spec:
      containers:
      - name: anomaly-detection
        image: quay.io/ncarcasc/anomaly-detection:latest 
        ports:
        - containerPort: 8080
```
- `containers`: Defines the **main container running in the pod**.
- `name`: Name of the container (`anomaly-detection`).
- `image`: Specifies the **Docker image** used to run the container. Here, it's hosted on Quay.io (`quay.io/ncarcasc/anomaly-detection:latest`).
- `containerPort`: Defines the **port inside the container** that the application will listen on (`8080`).

```yaml
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "250m"
            memory: "256Mi"
```
- **Requests**: The **minimum resources** the container needs to start.
  - `cpu: "250m"` → **250 millicores** (0.25 CPU core).
  - `memory: "256Mi"` → **256 Megabytes** of RAM.
- **Limits**: The **maximum resources** the container is allowed to use.
  - `cpu: "500m"` → **500 millicores** (0.5 CPU core).
  - `memory: "512Mi"` → **512 Megabytes** of RAM.


## **2️⃣ Service (`service.yaml`)**

The **Service (`service.yaml`)** exposes `anomaly-detection` **inside OpenShift** on port **80 → 8080**.

### **What is this?**
A **Service** in OpenShift exposes a set of pods as a network service. It allows internal communication between components inside the cluster.

### **Key Sections**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: anomaly-detection
  namespace: anomaly-detection
```
- `apiVersion`: Defines this as a **core Kubernetes Service resource**.
- `kind`: Specifies that this is a **Service**.
- `name`: The **name of the service** (`anomaly-detection`).
- `namespace`: The **namespace** where this service is deployed.

```yaml
spec:
  selector:
    app: anomaly-detection
```
- `selector`: This ensures the service routes traffic to pods **labeled as `app: anomaly-detection`**.

```yaml
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```
- `port`: **External port** for the service (used internally in OpenShift).
- `targetPort`: **Port inside the container** where the application is running (**8080** in our case).

```yaml
  type: ClusterIP
```
- **`ClusterIP` (default)** → This makes the service accessible **only inside the OpenShift cluster**.

---

## **3️⃣ Route (`route.yaml`)**
The **Route (`route.yaml`)** exposes `anomaly-detection` **externally** over **HTTPS (Edge Termination)**.
### **What is this?**
An **OpenShift Route** exposes the application to the external world via a public URL.

### **Key Sections**
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: anomaly-detection
  namespace: anomaly-detection
```
- `apiVersion`: Defines this as an **OpenShift Route resource**.
- `kind`: Specifies that this is a **Route** (not a Service or Deployment).
- `name`: The **name of the route** (`anomaly-detection`).
- `namespace`: The **namespace** where this route is created.

```yaml
spec:
  to:
    kind: Service
    name: anomaly-detection
```
- This **connects the route to the Service named `anomaly-detection`**.
- Requests to this route are forwarded **to the internal service**.

```yaml
  port:
    targetPort: 8080
```
- Ensures the route forwards traffic **to port 8080 inside the service**.

```yaml
  tls:
    termination: edge
```
- Enables **TLS (HTTPS) encryption** with **Edge Termination**:
  - **Edge termination** → The connection is encrypted **until OpenShift**, but then it becomes **plain HTTP inside the cluster**.
<br>

---

<br>

## **Appendix A: Debugging Errors**

<br>

<br>

### **[1] MongoDB Authentication Failure**
- **What it was:** Connection refused, authentication errors or timeout issues if not properly error handled.
- **Fix:** Whitelist OpenShift IP in MongoDB, get IP of pod through terminal, or set free access.
  
<br>

### **[2] OpenShift Route Not Working**
- **What it was:** Requests timeout externally but work inside the pod.
- **Fix:** Ensure `oc expose svc/anomaly-detection` exposes **port 8080**, not **80**.
  
<br>

### **[3] SSL Handshake Failure**
- **What it was:** PyMongo throwing `SSL: TLSV1_ALERT_INTERNAL_ERROR`
- **Fix:** Install latest OpenSSL, export `SSL_CERT_FILE` path.
  
<br>

### **[4] Internal Server Error on `/detect-anomalies`**
- **What it was:** NumPy throwing weird scalar conversion errors.
- **Fix:** Replaced `norm.pdf()` with explicit NumPy calculations.
  
<br>

## ** Some other useful commands I used**
| Command | Description |
|---------|------------|
| `oc logs -f deployment/anomaly-detection -n anomaly-detection` | View logs live |
| `oc exec -it <pod-name> -- python3` | Debug inside the pod |
| `oc rollout restart deployment/anomaly-detection -n anomaly-detection` | Redeploy after changes |

