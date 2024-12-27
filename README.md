# SNOWFLAKE CHATAPP

Welcome to the AI ChatApp developer repository! This guide provides detailed instructions on setting up your development environment, managing dependencies, and contributing to the project.

## Table of Contents

1. [Set Up the Python Environment](#1-set-up-the-python-environment)
2. [Manage Packages](#2-manage-packages)
3. [Environment Variables](#3-environment-variables)
4. [Running the Application](#4-running-the-application)
   - [Using Python](#using-python)
   - [Using Docker](#using-docker)
5. [Evaluating your model](#5-evaluating-your-model)
6. [Alternative to ](#alternative-to-env-files)[`.env`](#alternative-to-env-files)[ Files](#alternative-to-env-files)

---

## 1. Set Up the Python Environment

### a. Create a Python Environment with Python 3.10

Create a new Python virtual environment:

```bash
python3.10 -m venv <env_name>
```

Replace `<env_name>` with the name of your environment (e.g., `myenv`).

### b. Activate Your Created Environment

Activate the virtual environment:

```bash
source <env_name>/bin/activate
```

Replace `<env_name>` with your environment name.

---

## 2. Manage Packages

### Install All Dependencies

After activating your environment, install all required packages:

```bash
pip install -r requirements.txt
```

### Update Dependencies

Before pushing changes, synchronize your environment packages to the `requirements.txt` file for other developers:

```bash
pip freeze > requirements.txt
```

---


## 3. Environment Variables

Create a `.env` file in the root directory and add the required environment variables:

```env
SNOWFLAKE_ACCOUNT=accountname.region
SNOWFLAKE_USER=username
SNOWFLAKE_PASSWORD=********
SNOWFLAKE_DATABASE=databasename
SNOWFLAKE_SCHEMA=schemaname
SNOWFLAKE_ROLE=role
SNOWFLAKE_WAREHOUSE=warehousename
SNOWFLAKE_CORTEX_SEARCH_SERVICE=yourCortexserviceName
```


---

## 4. Running the Application

### Using Python

#### Run the Streamlit App

```bash
python run.py app:streamlit
```

#### Create the Database and Schema

Run the following command to execute the Snowflake script:

```bash
python run.py app:main
```

### Using Docker

1. **Install Docker**
   Ensure Docker is installed on your machine.

2. **Build and Start the App in Docker**

   - Build and start the app:
     ```bash
     docker compose up --build
     ```
   - To run in detached mode:
     ```bash
     docker compose up -d --build
     ```

3. **Start the App Without Rebuilding**

   ```bash
   docker compose up
   ```

   - To run in detached mode:
     ```bash
     docker compose up -d
     ```

4. **Stop the Docker Containers**

   ```bash
   docker compose down
   ```

---
## 5. Evaluating your model
To evaluate your model, run the following command:
```bash
python run.py app:trulens
```

This command will run trulens which helps in evaluating the model. just write your question on which you want your model to be evaluated and it will start an streamlit app where you can see the results and evaluation graph of your model respective to the answer, context and other parameters.

---

## 6. Alternative to `.env` Files

Instead of using a `.env` file, you can use `secrets.toml` for managing environment variables. Create a `.streamlit` folder in the root directory and add a `secrets.toml` file:

**Directory Structure:**

```
.project-root/
|-- .streamlit/
    |-- secrets.toml
```

**Contents of ****`secrets.toml`****:**

```toml
SNOWFLAKE_ACCOUNT = "accountname.region"
SNOWFLAKE_USER = "username"
SNOWFLAKE_PASSWORD = "********"
SNOWFLAKE_DATABASE = "databasename"
SNOWFLAKE_SCHEMA = "schemaname"
SNOWFLAKE_ROLE = "role"
SNOWFLAKE_WAREHOUSE = "warehousename"
SNOWFLAKE_CORTEX_SEARCH_SERVICE = "yourCortexserviceName"
```

This approach is especially useful for securely managing secrets in Streamlit applications.

