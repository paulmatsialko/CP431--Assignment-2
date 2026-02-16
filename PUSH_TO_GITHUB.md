# Push Assignment 2 to GitHub

Run these commands from the `CP431` folder (or your project root) in a terminal.

## One-time setup

```bash
cd c:\Users\macqu\Desktop\CP431

# Initialize Git (if not already)
git init

# Add the GitHub repo as remote "origin"
git remote add origin https://github.com/paulmatsialko/CP431--Assignment-2.git
```

If the folder is already a git repo and you already have an `origin` remote you want to replace:

```bash
git remote remove origin
git remote add origin https://github.com/paulmatsialko/CP431--Assignment-2.git
```

## Add, commit, and push

```bash
# Stage all assignment files
git add parallel_merge.py run_tests.sh submit_orca.sbatch README.md requirements.txt

# Or stage everything in the folder
git add .

# Commit
git commit -m "Assignment 2: Parallel merging of two sorted arrays (MPI4PY)"

# Push to GitHub (main branch; use 'master' if your default is master)
git branch -M main
git push -u origin main
```

If the repo already has a default branch (e.g. `main`) and you get an error, try:

```bash
git push -u origin main
```

## Authentication

- **HTTPS:** When you run `git push`, Git will ask for your GitHub username and password. For password, use a **Personal Access Token** (not your account password). Create one at: GitHub → Settings → Developer settings → Personal access tokens.
- **SSH:** If you use SSH keys, change the remote to:
  ```bash
  git remote set-url origin git@github.com:paulmatsialko/CP431--Assignment-2.git
  git push -u origin main
  ```

## Optional: ignore local / env files

Create a `.gitignore` so you don’t commit large or local files:

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
env/

# SLURM / logs
*.out
*.err

# OS
.DS_Store
Thumbs.db
```

Then:

```bash
git add .
git commit -m "Assignment 2: Parallel merging of two sorted arrays (MPI4PY)"
git push -u origin main
```
