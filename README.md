# 🚀 Enterprise Data Transformation Pipeline Using Gen AI

## 🧠 Overview

This tool is a comprehensive solution for data analysis, cleaning, transformation, and extracting valuable business insights. Powered by **TIAA’s advanced Generative AI**, the pipeline automates the entire data processing lifecycle—helping you uncover trends, outliers, and relationships effortlessly.

## 📊 What to Expect

- Fully automated analysis of any dataset  
- Detection of relationships, anomalies, and patterns  
- Generation of actionable business insights  
- Rich visualizations and metadata exploration  
- Seamless integration with AWS for storage and management

---

## 🛠️ How to Get Started

This application runs on **Python** and integrates with **AWS S3** and **PostgreSQL RDS**.

### ✅ Minimum Requirements

- **Operating System**: Windows / Linux  
- **Software**: PostgreSQL

---

## 📦 Setup Instructions

### 1. Go to the project directory
```bash
cd SAAS_REPO
```

### 2. Create a virtual environment
```bash
python -m venv SAAS
```

### 3. Activate the virtual environment
```bash
source SAAS/bin/activate
```

### 4. Install required dependencies
```bash
pip install -r requirements.txt
```

### 5. Set AWS Access Keys

Export your AWS credentials or set them via the AWS CLI.

---

### 6. Run the application
```bash
streamlit run App/app.py
```

### 7. Upload Data

- Upload your data files for analysis.  
- If needed, use the sample files provided in the `Data` package.

### 8. Wait for the pipeline to complete processing.

### 9. Explore Visual Outputs

- Navigate through the Streamlit interface to view processed metadata and interactive plots.  
- Gain actionable insights from auto-generated visualizations.

---

_Built with 🧠 Gen AI and Python, deployed with Streamlit and AWS_
