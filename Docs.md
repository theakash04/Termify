# AI ChatApp Developer Guide

This guide helps you manage your Python environment and dependencies in the project.

## 1. Set Up the Conda Environment

### a. Create a Conda Environment with Python 3.10
To create a new environment with Python 3.10:
```bash
conda create -n myenv python=3.10
```
This creates an environment named `myenv`.

### b. Activate the Conda Environment
To start using the environment:
```bash
conda activate myenv
```
---

## 2. Manage Packages

### Prerequisites
Make sure the `manage_package.sh` script is executable. If it's not, run:
```bash
chmod +x manage_package.sh
```

### a. Install All Dependencies from `requirements.txt`
To install all packages listed in `requirements.txt`, just run:
```bash
./manage_package.sh
```

### b. Install a Specific Package
To install a new package:
```bash
./manage_package.sh -i <package-name>
```

### c. Delete a Package
To remove a package:
```bash
./manage_package.sh -d <package-name>
```

---

## Developer Notes (Temporary)

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
```

2. **Sync your branch with master branch**
```bash
# 1. In your own branch which is dev/yourname
git fetch

# 2. resolve merge conflicts if any

# 3. merge it in your code locally
git merge origin/master

# 4. Now push your code remotelly
git push origin dev/akash
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

if session:  # Check if the session is active
    try:
        # Step 4: Execute a query
        result = session.sql("SELECT CURRENT_VERSION()").collect()
        print(f"Snowflake Version: {result[0][0]}")
    except Exception as e:
        print(f"Error occurred while executing query: {e}")

# Step 5: Close the connection
connector.close_connection()
```

