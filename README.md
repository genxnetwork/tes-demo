# GENXT GA4GH TES server demo repository

## Introduction
Welcome to the GENXT TES server demo repository! This project showcases the use of the Task Execution Service (TES) API, adhering to the GA4GH standard. The TES API facilitates the definition of batch execution tasks, including input files, Docker containers, commands, output files, and additional logging and metadata.

Test TES server URL: [http://tesktest.genx.link/ga4gh/tes/v1/](http://tesktest.genx.cloud/ga4gh/tes/v1/)

For detailed information about the TES API, refer to the [GA4GH Task Execution Service API documentation](https://ga4gh.github.io/task-execution-schemas/docs/).

## Repository Content
This repository includes a demonstration script to run [GRAPE (Genomic RelAtedness detection PipelinE)](https://github.com/genxnetwork/grape) using the GENXT TES enabled computing service. GRAPE is an open-source tool for detecting genomic relatedness and requires a multisample VCF file as input. It also includes workflows for downloading and verifying reference datasets.

## Getting Started
To utilize the script in this repository, follow these steps:

### Step 1: Set AWS S3 Credentials
Configure your AWS S3 credentials and region for downloading input files and saving results:

```python
AWS_ACCESS_KEY_ID = "<Your_Access_Key_ID>"
AWS_SECRET_ACCESS_KEY = "<Your_Secret_Access_Key>"
AWS_REGION = "us-east-1"
```

Configure your GENXT credentials:

```python
username = ''
password = ''
```

### Step 2: Initialize Task Data
Create a JSON object for task data:

```python
task_data = {
   "name": "GRAPE run",
   "resources": {"disk_gb": 200},
   "volumes": ["/vol/a/"],
   "executors": []
}
```

### Step 3: Add Executors
Define the steps of your workflow by adding executors:

#### 3.1 Downloading the Input Files from AWS S3 to Persistent Volume
Use the AWS CLI docker container from Docker Hub to download the input files from AWS S3 to the persistent volume, utilizing the provided S3 credentials:

```python
task_data["executors"].append({
   "image": "amazon/aws-cli",
   "command": ["aws", "s3", "cp", "s3://grapetestbucket/input.vcf.gz", "/vol/a/input.vcf.gz"],
   "env": {
       "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
       "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
       "AWS_REGION": AWS_REGION
   }
})
```
If you have input files on another storage service, you can use the BusyBox docker image and download files with wget:
```python
task_data["executors"].append({
   "image": "busybox",
   "command": ["/bin/wget", "ftp://https://ftp.ebi.ac.uk/robots.txt", "/vol/a/robots.txt"]
})
```

#### 3.2 Running GRAPE Software from Docker Hub Container
Execute the GRAPE software using the genxnetwork/grape Docker Hub container. This step involves downloading the reference panel to the persistent volume and preprocessing the input file.

##### Step 1: Download Reference Panel
Download the reference panel to Persistent volume /vol/a/ in the folder /media/ref:

```python
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
```

##### Step 2: Preprocessing of the Input File
Preprocess the input file with the following command:
```python
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
```

##### Step 3: Relatives Search Using IBIS Flow
Run the relatives search part of the GRAPE software using the IBIS flow:

```python
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
```

#### 3.3 Uploading the Result Files to AWS S3 Bucket from Persistent Volume
Upload the result files from the persistent volume to the AWS S3 bucket:

```python
task_data["executors"].append({
   "image": "amazon/aws-cli",
   "command": ["aws", "s3", "cp", "/vol/a/media/data/results/relatives.tsv", "s3://grapetestbucket/relatives_output.tsv"],
   "env": {
       "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
       "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
       "AWS_REGION": AWS_REGION
   }
})
```

### Step 4: Create Task via POST /tasks Endpoint
Create a task using the POST /tasks endpoint with the following code:

```python
url = "http://tesktest.genx.cloud/ga4gh/tes/v1/tasks"
headers = {
   "accept": "application/json",
   "Content-Type": "application/json"
}
response = requests.post(url, headers=headers, data=json.dumps(task_data), auth=HTTPBasicAuth(username, password))
print("POST request response:", response.json())
task_id = response.json().get("id")
```

### Step 5: Check Task Status via GET /tasks/{task_id} Endpoint
Monitor the status of your task using the GET /tasks/{task_id} endpoint:

```python
url = f"http://tesktest.genx.cloud/ga4gh/tes/v1/tasks/{task_id}"
headers = {
   "accept": "application/json",
   "Content-Type": "application/json"
}
response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password))
print("GET request response:", response.json())
```

### Step 6: Get the List of All Tasks via GET /tasks Endpoint
Retrieve a list of all tasks using the GET /tasks endpoint:

```python
url = f"http://tesktest.genx.cloud/ga4gh/tes/v1/tasks"
headers = {
   "accept": "application/json",
   "Content-Type": "application/json"
}
response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password))
#print("GET request response:", response.json())
all_tasks = response.json().get("tasks")
for task in all_tasks:
   print(task)
```
