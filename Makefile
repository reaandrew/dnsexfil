.PHONY: help clean build-lambdas deploy plan destroy test-lambdas

# Default target
help:
	@echo "Available targets:"
	@echo "  build-lambdas    - Build all Lambda deployment packages"
	@echo "  clean           - Remove all build artifacts"
	@echo "  plan            - Run terraform plan"
	@echo "  deploy          - Deploy infrastructure with terraform apply"
	@echo "  destroy         - Destroy infrastructure with terraform destroy"
	@echo "  test-lambdas    - Test Lambda functions locally"
	@echo ""

# Automatically discover all Lambda directories
LAMBDA_DIRS := $(shell find lambdas -maxdepth 1 -type d ! -name lambdas | sed 's|lambdas/||')
LAMBDA_PACKAGES := $(foreach dir,$(LAMBDA_DIRS),infrastructure/$(subst -,_,$(dir)).zip)

# Build all Lambda functions
build-lambdas: clean $(LAMBDA_PACKAGES)
	@echo "All Lambda packages built successfully!"

# Generic rule to build any Lambda function
infrastructure/%.zip:
	$(eval ZIP_NAME := $(notdir $@))
	$(eval ZIP_BASENAME := $(basename $(ZIP_NAME)))
	$(eval LAMBDA_NAME := $(subst _,-,$(ZIP_BASENAME)))
	@echo "Building $(LAMBDA_NAME) Lambda ($(ZIP_NAME))..."
	@cd lambdas/$(LAMBDA_NAME) && \
		if [ -f requirements.txt ] && [ -s requirements.txt ] && ! grep -q "^# No additional requirements" requirements.txt; then \
			echo "Installing dependencies for $(LAMBDA_NAME)..."; \
			python3 -m venv .venv && \
			.venv/bin/pip install -r requirements.txt -t . && \
			rm -rf .venv; \
		fi
	@cd lambdas/$(LAMBDA_NAME) && \
		zip -r ../../infrastructure/$(ZIP_NAME) . -x "*.pyc" "__pycache__/*" ".venv/*" "*.md"
	@echo "$(LAMBDA_NAME) package created: infrastructure/$(ZIP_NAME)"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -f infrastructure/*.zip
	@find lambdas/ -name "*.pyc" -delete
	@find lambdas/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find lambdas/ -name ".venv" -type d -exec rm -rf {} + 2>/dev/null || true
	@find lambdas/ -name "boto3*" -type d -exec rm -rf {} + 2>/dev/null || true
	@find lambdas/ -name "botocore*" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete!"

# Terraform operations
plan: build-lambdas
	@echo "Running terraform plan..."
	@cd infrastructure && terraform plan

deploy: build-lambdas
	@echo "Deploying infrastructure..."
	@cd infrastructure && terraform apply -auto-approve
	@echo "Uploading Public Suffix List data..."
	@$(MAKE) update-psl

destroy:
	@echo "Destroying infrastructure..."
	@cd infrastructure && terraform destroy -auto-approve

# Test Lambda functions locally (optional)
test-lambdas:
	@echo "Testing Lambda functions..."
	@echo "Note: Install python-lambda-local for local testing"
	@echo "pip install python-lambda-local"
	@echo "lambda-local -l lambdas/partition-repair/ -h lambda_function.lambda_handler -e test_event.json"

# Update PSL data
update-psl:
	@echo "Updating Public Suffix List data..."
	@scripts/update_psl.sh

# Show DNS detection timeline
timeline:
	@echo "Analyzing DNS detection timeline..."
	@scripts/dns_timeline.sh $(HOURS)

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	@python3 -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

init:
	@echo "Initializing Terraform..."
	@cd infrastructure && terraform init