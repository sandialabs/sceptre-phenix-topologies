.DEFAULT_GOAL := help

.PHONY: help lint install-dev update-actions

help:
	@echo "Available targets:"
	@echo "  lint           - Run all prek hooks across the whole repository"
	@echo "  install-dev    - Install local dev tooling and register git hooks"
	@echo "  update-actions - Update pinned actions in GitHub workflows"
	@echo "  help           - Show this help message"

lint:
	@command -v prek > /dev/null || { echo "Error: 'prek' not found. Run 'make install-dev' first."; exit 1; }
	@prek run --all-files

install-dev:
	@command -v prek > /dev/null || pip install 'prek>=0.4.3'
	@prek install

update-actions:
	@echo "Updating pinned actions in GitHub workflows..."
	@docker run --rm -v "$(CURDIR):/workflows" mheap/pin-github-action .github/workflows/
