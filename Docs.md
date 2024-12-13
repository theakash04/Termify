# AI ChatApp Developer Guide

This guide helps you manage your Python environment and dependencies in the project.

## 1. Set Up the Python Environment

### a. Create a Conda Environment with Python 3.10
To create a new environment with Python 3.10:
```bash
python3.10 -m venv <envName>
```
This creates an environment named `myenv`.

### b. Activate your created Environment
To start using the environment:
```bash
source .venv/bin/activate
```
---

## 2. Manage Packages

### Install all dependencies after activating your enviroment
```bash
pip install -r requirement.txt
```

### Before pushing to git make sure to run the below command to sync your env packages to requirents for other devs
```bash
pip freeze > requirement.txt
```
---

## Developer Notes

1. **Environment Variables**

Create a `.env` file in the root directory and add your variables.
```env
SNOWFLAKE_ACCOUNT=acountname.region
SNOWFLAKE_USER=username
SNOWFLAKE_PASSWORD=********
SNOWFLAKE_DATABASE=databasename
SNOWFLAKE_SCHEMA=schemaname
SNOWFLAKE_ROLE=role
SNOWFLAKE_WAREHOUSE=warehousename
SNOWFLAKE_CORTEX_SEARCH_SERVICE=yourCortexserviceName
```

2. **Sync your branch with master branch**
```bash
# 1. In your own branch which is dev/yourname
git fetch origin

# 2. resolve merge conflicts if any

# 3. merge it in your code locally
git rebase origin/master

# 4. Now push your code remotelly
git push origin dev/yourname
```


3. How to push your code to main branch **Make sure you are in your own branch not someone else or Master branch**
```bash
# first stage your changes
git add .

# commit your changes
git commit -m "update: something update"

# push your changes to your branch
git push -u origin dev/yourname
```

4. Now go to `github.com` and make a pull request or contribute when making pull request make sure write comment on what you changed point vise

### Steps on how You can create a session with snowfake **Make sure you have created `.env` file in root directory**
```python
# Import the class
from your_module import SnowflakeConnector

# Step 1: Instantiate the class
connector = SnowflakeConnector()

# Step 2: Connect to Snowflake
connector.connect()

# Step 3: Retrieve the session
session = connector.get_session()

# Step 5: Close the connection
connector.close_connection()
```

