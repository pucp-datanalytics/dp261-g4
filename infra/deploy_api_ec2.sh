#!/usr/bin/env bash
set -euo pipefail

# Script de referencia para Rol 3 (Cloud/DevOps).
# No contiene credenciales. Requiere variables de entorno configuradas en la terminal o CI/CD.

: "${AWS_REGION:?Falta AWS_REGION}"
: "${ECR_REGISTRY:?Falta ECR_REGISTRY, ej. 009030765814.dkr.ecr.us-east-1.amazonaws.com}"
: "${ECR_REPOSITORY_API:?Falta ECR_REPOSITORY_API}"

IMAGE_URI="${ECR_REGISTRY}/${ECR_REPOSITORY_API}:latest"

aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"

docker build -t sprint6-api -f api/Dockerfile .
docker tag sprint6-api:latest "$IMAGE_URI"
docker push "$IMAGE_URI"

echo "Imagen publicada: $IMAGE_URI"
echo "En EC2, ejecutar:"
echo "docker pull $IMAGE_URI"
echo "docker run -d --name sprint6-api -p 8000:8000 -e API_KEY=\"<opcional>\" $IMAGE_URI"
