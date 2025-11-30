# GitHub Setup & Sync Guide

## 1. Create Repository on GitHub
1. Go to [GitHub.com](https://github.com) and log in.
2. Click the **+** icon in the top-right and select **New repository**.
3. Name it `sportsee-rag` (or your preferred name).
4. **Important**: Do NOT check "Initialize with README", "Add .gitignore", or "Add license". We already have these locally.
5. Click **Create repository**.

## 2. Push Local Code to GitHub
Run these commands in your terminal (replace `YOUR_USERNAME` with your actual GitHub username):

```bash
# Link local repo to remote
git remote add origin https://github.com/YOUR_USERNAME/sportsee-rag.git

# Rename branch to main if not already (we did this, but good to be safe)
git branch -M main

# Push the code
git push -u origin main
```

## 3. Work from Another Computer
On your second machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sportsee-rag.git
   cd sportsee-rag
   ```

2. **Set up the environment**:
   ```bash
   # Install Poetry (if not installed)
   pip install poetry

   # Install dependencies
   poetry install
   ```

3. **Configure Environment Variables**:
   - Create a `.env` file (copy `.env.example`).
   - Add your API keys (these are NOT synced to GitHub for security).

4. **Run the App**:
   ```bash
   poetry run uvicorn src.api.main:app --reload
   ```

## 4. Daily Workflow
- **Before starting work**: `git pull origin main`
- **After finishing work**:
  ```bash
  git add .
  git commit -m "Description of changes"
  git push origin main
  ```
