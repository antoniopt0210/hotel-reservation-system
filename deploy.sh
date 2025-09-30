#!/bin/bash

# Navigate into the frontend directory
cd frontend

# Build the React app for production
npm run build

# Navigate into the build directory
cd build

# Initialize Git and connect to your repository
git init
git add .
git commit -m "Deploying to GitHub Pages"
git branch -M gh-pages

# Push the build folder to the gh-pages branch
git push -f https://github.com/antoniopt0210/hotel-reservation-system.git gh-pages:gh-pages

echo "Deployment complete! Your app should be live in a few minutes."
