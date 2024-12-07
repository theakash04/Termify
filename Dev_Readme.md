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

2. **Sync your branch with master branch**
```bash
# 1. Go to master branch
git checkout master

# 2. Pull from remote master branch to locally
git pull master

# 3. change branch to your branch 
git checkout dev/yourname

# 4. pull from origin master
git pull origin master

# Now you can start writing your code or sync your branch remotelly to sync you can do 
git push
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


`Do clean code`


