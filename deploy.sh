#!/bin/bash

# Define the project name, which will be the subdirectory on GitHub Pages
PROJECT_NAME="hotel-reservation-system"
GITHUB_USERNAME="antoniopt0210"
PAGES_REPO="https://github.com/${GITHUB_USERNAME}/${GITHUB_USERNAME}.github.io.git"

echo "Building React app for production..."
npm run build

echo "Navigating to the build directory..."
cd build

echo "Initializing Git and connecting to your GitHub Pages repository..."
git init
git remote add origin ${PAGES_REPO}
git add .
git commit -m "Deploying ${PROJECT_NAME} to GitHub Pages"
git branch -M main

echo "Pushing build folder to GitHub Pages..."
git push -f origin main:${PROJECT_NAME}

echo "Deployment complete! Your app should be live in a few minutes at https://${GITHUB_USERNAME}.github.io/${PROJECT_NAME}"
