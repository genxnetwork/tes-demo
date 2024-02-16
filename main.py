import requests
import json
from requests.auth import HTTPBasicAuth

# Define AWS S3 credentials and region
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_REGION = "us-east-1"

# Your GENXT credentials
username = ''
password = ''

# Initialize JSON Data
task_data = {
    # Task name
    "name": "GRAPE run",

    # Persistent volume limit
    "resources": {"disk_gb": 200},
    
    # Persistent volume
    "volumes": ["/vol/a/"],

    "executors": []
}

# Add Executors - steps of the workflow

# Downloading the input files from AWS S3 to persistent volume using S3 credentials
task_data["executors"].append({
    "image": "amazon/aws-cli",
    "command": ["aws", "s3", "cp", "s3://grapetestbucket/input.vcf.gz", "/vol/a/input.vcf.gz"],
    "env": {
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "AWS_REGION": AWS_REGION
    }
})

# Running GRAPE software. Step 1: reference panel download 
task_data["executors"].append({
    "image": "genxnetwork/grape",
    "command": [
        "python",
        "launcher.py",
        "reference",
        "--use-bundle",
        "--ref-directory",
        "/vol/a/media/ref",
        "--real-run"
    ]
})

# Running GRAPE software. Step 2: preprocessing of the input file 
task_data["executors"].append({
    "image": "genxnetwork/grape",
    "command": [
        "python",
        "launcher.py",
        "preprocess",
        "--ref-directory",
        "/vol/a/media/ref",
        "--vcf-file",
        "/vol/a/input.vcf.gz",
        "--directory",
        "/vol/a/media/data",
        "--assembly",
        "hg37",
        "--real-run"
    ]
})

# Running GRAPE software. Step 3: relatives search using IBIS flow 
task_data["executors"].append({
    "image": "genxnetwork/grape",
    "command": [
        "python",
        "launcher.py",
        "find",
        "--flow",
        "ibis",
        "--ref-directory",
        "/vol/a/media/ref",
        "--directory",
        "/vol/a/media/data",
        "--real-run"
    ]
})

# Uploading the result files to AWS S3 bucket from persistent volume
task_data["executors"].append({
    "image": "amazon/aws-cli",
    "command": ["aws", "s3", "cp", "/vol/a/media/data/results/relatives.tsv", "s3://grapetestbucket/relatives_output.tsv"],
    "env": {
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "AWS_REGION": AWS_REGION
    }
})

# Print the whole JSON structure
# print(json.dumps(task_data, indent=4))

# Requesting TES API - task creation
url = "http://tesktest.genxt.cloud/ga4gh/tes/v1/tasks"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
response = requests.post(url, headers=headers, data=json.dumps(task_data), auth=HTTPBasicAuth(username, password))
print("POST request response:", response.json())
task_id = response.json().get("id")

# Requesting TES API - task status
url = f"http://tesktest.genxt.cloud/ga4gh/tes/v1/tasks/{task_id}"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password))
print("GET request response:", response.json())

# Requesting TES API - task list
url = f"http://tesktest.genxt.cloud/ga4gh/tes/v1/tasks"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password))
all_tasks = response.json().get("tasks")
for task in all_tasks:
    print(task)
