#!/bin/bash
set -e
trap 'echo "❌ Docker deployment failed."' ERR

echo ""
echo "🛑 Stopping old Docker container..."
docker stop portfolio-insights-backend || true
echo "✅ Done."

echo ""
echo "🧹 Cleaning up Docker environment..."
# Note that this will remove all unused images, volumes, and containers.
# Great for a lean EC2 environment, but dangerous for local development!
# For a lighter, safer cleanup, use:
#     docker rm resume-scanner || true
#     docker rmi resume-scanner || true
docker system prune -a --volumes -f
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
echo "🐘 Make sure your PostgreSQL database is also set up."
echo ""