# Makefile for the RAG Backend API

.PHONY: help build run stop logs shell install run-local clean

# ====================================================================================
# VARIABLES
# ====================================================================================

IMAGE_NAME := rag-backend
CONTAINER_NAME := rag-backend-container
PORT := 8000

# ====================================================================================
# HELP
# ====================================================================================

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build         Build the Docker image for the application."
	@echo "  run           Run the application in a Docker container."
	@echo "  stop          Stop the running Docker container."
	@echo "  logs          Follow the logs of the running container."
	@echo "  shell         Get a shell inside the running container."
	@echo "  install       Install Python dependencies locally using requirements.txt."
	@echo "  run-local     Run the application locally with auto-reload for development."
	@echo "  clean         Remove the Docker image."

# ====================================================================================
# DOCKER COMMANDS
# ====================================================================================

build:
	@docker build -t $(IMAGE_NAME) .

run:
	@docker run -d --rm -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop:
	@docker stop $(CONTAINER_NAME)

logs:
	@docker logs -f $(CONTAINER_NAME)

shell:
	@docker exec -it $(CONTAINER_NAME) /bin/sh

clean:
	@docker rmi $(IMAGE_NAME)

# ====================================================================================
# LOCAL DEVELOPMENT COMMANDS
# ====================================================================================

install:
	@pip install -r requirements.txt

run-local:
	@uvicorn main:app --host 0.0.0.0 --port $(PORT) --reload