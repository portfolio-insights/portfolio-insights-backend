#!/bin/bash
set -e
trap 'echo "❌ Docker teardown failed."' ERR

echo ""
echo "🛑 Stopping Docker container..."
docker stop portfolio-insights-backend || true
echo "✅ Done."

echo ""
echo "🧼 Removing Docker container and images..."
docker rm portfolio-insights-backend || true
docker rmi portfolio-insights-backend || true
echo "✅ Done."

echo ""
echo "🎉 Docker deployment torn down."
echo ""