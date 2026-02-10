#!/bin/bash

# Script para construir e fazer deploy da aplicação no SaladCloud versão linux

set -e

DOCKER_USERNAME="renan2002"
IMAGE_NAME="instagram-link-collector"
VERSION="1.1.12"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

echo "Construindo imagem Docker: $FULL_IMAGE_NAME"

docker build -t "$FULL_IMAGE_NAME" .

echo "Imagem construída com sucesso!"

echo "Fazendo upload para Docker Hub..."

# Login no Docker Hub
echo "Faça login no Docker Hub:"
docker login

# Fazer upload
docker push "$FULL_IMAGE_NAME"
echo "Upload concluído!"

echo "Informações para o SaladCloud:"
echo "   Image: $FULL_IMAGE_NAME"
echo ""