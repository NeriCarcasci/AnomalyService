# Anomaly Detection Service

## **Overview**
This repository contains an **anomaly detection API** built with **FastAPI**, **MongoDB**, and **OpenShift**. The goal is to provide a scalable and efficient anomaly detection service that can be deployed on OpenShift while maintaining flexibility in storage options (MongoDB Atlas, Google Firestore, or local MongoDB).

---

## **1. Setup**
A step-by-step breakdown of getting from zero to a working deployment.

### **1.1 Prerequisites**
- Python **3.10+** (avoid Homebrew Python—it’s a disaster waiting to happen)
- OpenShift CLI (`oc`)
- A **MongoDB Atlas account** (or a local MongoDB instance). Google Firestore can be swapped in if needed.
- FastAPI & dependencies

### **1.2 Installation**
#### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/NeriCarcasci/AnomalyService.git
cd AnomalyService
```
If making Python changes, rebuild and publish the container:
```sh
podman build --platform linux/amd64 -t quay.io/ncarcasc/anomaly-detection:latest .
podman push quay.io/ncarcasc/anomaly-detection:latest
```
The `--platform` flag is crucial when building on macOS for OpenShift.

#### **2️⃣ Create a Virtual Environment & Install Dependencies**
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Or install manually as per the Dockerfile
```

#### **3️⃣ Deploy to OpenShift**
```sh
oc new-project anomaly-detection
```

#### **4️⃣ Configure MongoDB Connection**
1. **If using MongoDB Atlas**, whitelist your OpenShift cluster’s IP.
2. **Set MongoDB URI as an environment variable** (or update `MONGO_URI` in `main.py`):
```sh
oc set env deployment/anomaly-detection MONGO_URI="mongodb+srv://USERNAME:PASSWORD@maincluster.mongodb.net/DATABASE?retryWrites=true&w=majority&appName=maincluster" -n anomaly-detection
```

#### **5️⃣ Apply OpenShift YAML Files**
Deploy the application using:
```sh
oc apply -f deployment.yaml
oc apply -f service.yaml
oc apply -f route.yaml
```

#### **6️⃣ Verify Deployment & Test API**
Check if the pods are running:
```sh
oc get pods -n anomaly-detection
```
If things go sideways, check the logs:
```sh
oc logs -f deployment/anomaly-detection -n anomaly-detection
```

---

## **2. Debugging & Common Issues**
If tests fail, the testing functions are likely the culprit. Comment them out and move on. 

| Error ID | Issue |
|----------|--------------------------------------|
| [1] | MongoDB Authentication Failure |
| [2] | OpenShift Route Not Working |
| [3] | SSL Handshake Failure |
| [4] | Internal Server Error on `/detect-anomalies` |

### **Solutions**
#### **[1] MongoDB Authentication Failure**
- **Cause:** Connection refused, authentication issues, or timeouts.
- **Fix:** Whitelist OpenShift’s IP in MongoDB Atlas or allow open access for debugging.

#### **[2] OpenShift Route Not Working**
- **Cause:** Requests timeout externally but work inside the pod.
- **Fix:** Ensure `oc expose svc/anomaly-detection` exposes port **8080**, not **80**.

#### **[3] SSL Handshake Failure**
- **Cause:** PyMongo throwing `SSL: TLSV1_ALERT_INTERNAL_ERROR`.
- **Fix:** Install the latest OpenSSL and explicitly set `SSL_CERT_FILE`.

#### **[4] Internal Server Error on `/detect-anomalies`**
- **Cause:** NumPy-related scalar conversion errors.
- **Fix:** Replace `norm.pdf()` with direct NumPy calculations.

---

## **3. Code Structure & Design Choices**

### **3.1 Code Layout**
- `app.py` → Main application entry point
- `routes.py` → API endpoints & logic
- `models.py` → API request data models
- `db.py` → Database connection functions
- `services/` → Core business logic
- `metrics/` → Fairness and evaluation metric implementations
- `tests/` → Unit tests

### **3.2 Design Decisions**
✔ **NumPy over SciPy** → Avoided `norm.pdf()` and other precision issues that haunted me at night.
✔ **MongoDB over MinIO** → Persistent storage without spending **two hours installing the MinIO operator**. Google Firestore is also a valid alternative.

---

## **4. OpenShift Deployment Breakdown**
### **4.1 Deployment (`deployment.yaml`)**
Defines how OpenShift deploys `anomaly-detection`, running a single instance and exposing port **8080**.

```yaml
metadata:
  name: anomaly-detection
  namespace: anomaly-detection
```

```yaml
spec:
  replicas: 1
```

```yaml
    spec:
      containers:
      - name: anomaly-detection
        image: quay.io/ncarcasc/anomaly-detection:latest
        ports:
        - containerPort: 8080
```

### **4.2 Service (`service.yaml`)**
Exposes the application **internally** on **port 80 → 8080**.

```yaml
spec:
  selector:
    app: anomaly-detection
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
```

### **4.3 Route (`route.yaml`)**
Exposes the service **externally** over HTTPS (Edge Termination).

```yaml
spec:
  to:
    kind: Service
    name: anomaly-detection
  port:
    targetPort: 8080
  tls:
    termination: edge
```

---

## **5. Useful OpenShift Commands**

| Command | Purpose |
|---------|---------|
| `oc logs -f deployment/anomaly-detection -n anomaly-detection` | View live logs |
| `oc exec -it <pod-name> -- python3` | Debug inside the pod |
| `oc rollout restart deployment/anomaly-detection -n anomaly-detection` | Redeploy after changes |

---

This documentation balances **depth and clarity** while keeping the energy high. If something breaks, well, that’s what logs are for. 🚀
