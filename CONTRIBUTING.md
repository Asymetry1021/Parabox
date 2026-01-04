# Contributing to Parabox

Thank you for your interest in contributing to Parabox! This guide will help you add your existing code files to the repository.

## How to Import Your Existing Files

If you already have code files on your computer and want to add them to this repository, follow these steps:

### Step 1: Place Your Files in the Repository Directory

First, copy or move your existing files into the repository directory:

```bash
# Navigate to the repository directory
cd /path/to/Parabox

# Copy your files here
# You can organize them into subdirectories as needed
```

### Step 2: Check Which Files Are New

Use `git status` to see which files are untracked (not yet added to Git):

```bash
git status
```

This will show you all the new files that Git doesn't know about yet.

### Step 3: Add Files to Git

You have several options for adding files:

#### Add a Single File
```bash
git add path/to/your/file.ext
```

#### Add Multiple Specific Files
```bash
git add file1.py file2.py file3.py
```

#### Add All Files in a Directory
```bash
git add src/
```

#### Add All New Files (Use with Caution)
```bash
git add .
```

**Note:** Be careful with `git add .` as it will add all untracked files. Make sure you don't accidentally add files you don't want in the repository (like build artifacts, temporary files, or sensitive information).

### Step 4: Create .gitignore (Optional but Recommended)

Before adding files, you may want to create a `.gitignore` file to exclude certain files or directories:

```bash
# Create .gitignore file
touch .gitignore
```

Common patterns to add to `.gitignore`:

```
# Build outputs
*.o
*.exe
dist/
build/

# Dependencies
node_modules/
venv/

# IDE files
.vscode/
.idea/
*.swp

# OS files
.DS_Store
Thumbs.db

# Sensitive files
*.env
.env.local
secrets.json
```

### Step 5: Commit Your Files

After adding files, commit them with a descriptive message:

```bash
git commit -m "Add initial game implementation files"
```

### Step 6: Push to GitHub

Finally, push your changes to GitHub:

```bash
git push origin main
```

If you're working on a different branch:

```bash
git push origin your-branch-name
```

## Example Workflow

Here's a complete example of importing a Python game implementation:

```bash
# 1. Navigate to the repository
cd ~/Parabox

# 2. Create a source directory
mkdir src

# 3. Copy your files
cp ~/my-game-files/*.py src/

# 4. Create .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# 5. Check what will be added
git status

# 6. Add the files
git add src/
git add .gitignore

# 7. Commit
git commit -m "Add initial Python game implementation"

# 8. Push to GitHub
git push origin main
```

## Common Issues and Solutions

### Issue: "fatal: not a git repository"
**Solution:** Make sure you're in the correct directory. Run `pwd` to check your current location, and `cd` to the repository directory.

### Issue: Large files causing errors
**Solution:** GitHub has a file size limit (100MB). For large files, consider using [Git LFS (Large File Storage)](https://git-lfs.github.com/).

### Issue: Accidentally added sensitive files
**Solution:** If you haven't pushed yet, you can unstage files with:
```bash
git reset HEAD path/to/sensitive/file
```

If you've already pushed, you'll need to remove the file from history. See [GitHub's guide on removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

### Issue: Merge conflicts when pushing
**Solution:** Pull the latest changes first, resolve any conflicts, then push:
```bash
git pull origin main
# Resolve any conflicts in your editor
git add .
git commit -m "Merge remote changes"
git push origin main
```

## Project Structure

When adding files, consider organizing them logically:

```
Parabox/
├── README.md           # Project overview
├── CONTRIBUTING.md     # This file
├── .gitignore         # Files to ignore
├── src/               # Source code
│   ├── main.py        # Entry point
│   ├── game.py        # Game logic
│   └── levels/        # Level definitions
├── assets/            # Game assets
│   ├── sprites/       # Image files
│   └── sounds/        # Audio files
├── tests/             # Unit tests
└── docs/              # Documentation
```

## Need Help?

If you're stuck or have questions:
1. Check the [GitHub documentation](https://docs.github.com)
2. Open an issue in this repository
3. Ask for help in the discussions section

Happy coding!
