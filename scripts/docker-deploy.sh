#!/bin/bash

echo ""
echo "🛑 Stopping old Docker container..."
docker stop portfolio-insights-backend || true
echo "✅ Done."

echo ""
echo "🧼 Removing old Docker container and images..."
docker rm portfolio-insights-backend || true
docker rmi portfolio-insights-backend || true
echo "✅ Done."

echo ""
echo "🐳 Building new Docker image..."
docker build --pull -t portfolio-insights-backend .
echo "✅ Done."

echo ""
echo "🚀 Spinning up new Docker container..."
docker run -d --restart unless-stopped --name portfolio-insights-backend -p 8001:8001 --env-file .env.docker portfolio-insights-backend
echo "✅ Done."

echo ""
echo "🎉 Backend running on Docker."
echo ""