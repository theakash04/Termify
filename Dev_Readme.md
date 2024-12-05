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

2. **Merge Your Branch with the Main Branch**:
   - After finishing your task, merge your branch with `main`:
     ```bash
     git fetch origin
     git merge origin/main
     ```

3. **Push and Pull After PR Acceptance**:
   - Once your PR is accepted, pull the latest changes from `main`:
     ```bash
     git pull origin main
     ```


