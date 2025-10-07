
# Phishing URL Classifier: End-to-End MLOps Pipeline 🛡️

This project demonstrates a complete MLOps pipeline for classifying malicious (phishing) URLs, covering data handling, model deployment, monitoring, and containerization.

## 🌟 Project Highlights

  * **Machine Learning:** Trained Random Forest Classifier for URL classification.
  * **Data Storage:** Stores model weights in **AWS S3** for version control and decoupling.
  * **Logging/Monitoring:** Logs all prediction job details and outcomes to **MongoDB Atlas**.
  * **Frontend:** User interface built with **Streamlit** for file upload and result visualization.
  * **Backend:** RESTful API built with **Flask** for serving predictions.
  * **Deployment:** Containerized using **Docker** for reproducibility and production readiness.

## 🏗️ Architecture Diagram

The application follows a robust microservices architecture:

1.  **User** uploads a CSV via the Streamlit UI.
2.  **Streamlit** sends data to the **Flask API**.
3.  **Flask API** downloads the ML model from **AWS S3** on startup.
4.  **Flask API** processes features, makes predictions, and sends results back to Streamlit.
5.  **Flask API** simultaneously logs the prediction job summary to **MongoDB Atlas**.
6.  The API service itself is containerized using **Docker** for easy deployment.

-----

## ⚙️ Setup and Installation

### Prerequisites

1.  **Python 3.11+**
2.  **Git**
3.  **Docker Desktop** (Required for the containerized solution)
4.  **AWS Account** (for S3)
5.  **MongoDB Atlas Cluster**

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone [YOUR-GITHUB-REPO-LINK]
    cd phishing-classifier
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv phishing_env
    .\phishing_env\Scripts\Activate.ps1  # Windows PowerShell
    # source phishing_env/bin/activate    # Linux/macOS
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration (`.env` file)

Create a file named **`.env`** in the project root to securely store your credentials. This file is excluded from Git via `.gitignore`.

```env
# AWS Credentials for S3 model access
AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
S3_BUCKET_NAME=myphishing-classifier

# MongoDB Atlas URI (connection string)
# Note: The 'tlsAllowInvalidCertificates=true' is used for local development compatibility.
MONGO_URI="mongodb+srv://<USER>:<PASSWORD>@cluster0.ytrhnxg.mongodb.net/phishing_db?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
```

-----

## 🚀 Running the Pipeline (Containerized Method)

The most professional way to run this project is through Docker.

### 1\. Build the Docker Image

This command builds the image based on the `Dockerfile` and tags it with your Docker Hub username (`gopi875444`).

```bash
docker build -t gopi875444/phishing-classifier:latest .
```

### 2\. Run the Container

This launches the Flask API in the background (`-d`) and maps the internal port 5000 to your host machine's port 5000.

```bash
docker run -d -p 5000:5000 --name phishing-detector gopi875444/phishing-classifier:latest
```

### 3\. Run the Streamlit Frontend

With the container running, launch the UI in a separate terminal window:

```bash
streamlit run streamlit_app.py
```

-----

## 📊 Evaluation and Metrics

The pipeline calculates and displays key metrics when the ground truth column (`Result`) is present in the uploaded CSV:

  * **Total Records**
  * **Phishing URLs** Count
  * **Legitimate URLs** Count
  * **Model Accuracy** (e.g., 98.59%)

All this summary data, along with the job metadata, is automatically logged to the `prediction_jobs` collection in **MongoDB Atlas** for monitoring.

-----

## 📦 Deployment Asset

The final deployable image has been pushed to Docker Hub:

```bash
docker push gopi875444/phishing-classifier:latest
```

You can pull and run this image on any cloud platform (AWS ECS, Azure ACI, etc.) to host the prediction API publicly.