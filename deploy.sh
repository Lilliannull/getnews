#!/bin/bash

set -e  # Stop script if any command fails

echo "🚀 Deploying to GitHub Pages..."

# Path where the temporary worktree will live
DEPLOY_DIR="../gh-pages-deploy"

# Ensure we're in the main project directory
MAIN_DIR=$(pwd)

# Clean up any old deploy worktree if exists
rm -rf "$DEPLOY_DIR"

# Create a temporary worktree from the gh-pages branch
git worktree add "$DEPLOY_DIR" gh-pages

# Copy the generated HTML file to index.html
cp "$MAIN_DIR/fetch_titles.html" "$DEPLOY_DIR/index.html"

# Enter the deploy directory
cd "$DEPLOY_DIR"

# Commit and push changes
git add index.html
git commit -m "🔄 Update index.html on $(date '+%Y-%m-%d %H:%M')" || echo "⚠️ Nothing to commit"
git push origin gh-pages

# Return and clean up
cd "$MAIN_DIR"
git worktree remove "$DEPLOY_DIR" --force

echo "✅ Deployment complete: https://lilliannull.github.io/getnews/"
