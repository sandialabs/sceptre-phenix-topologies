.DEFAULT_GOAL := help

.PHONY: help lint install-dev update-actions container-lint container-shell container-run

help:
	@echo "Available targets:"
	@echo "  lint            - Run all prek hooks across the whole repository"
	@echo "  install-dev     - Install local dev tooling and register git hooks"
	@echo "  update-actions  - Update pinned actions in GitHub workflows"
	@echo "  container-lint  - Run all prek hooks in the Linux dev container (as CI does)"
	@echo "  container-shell - Start a shell in the Linux dev container"
	@echo "  container-run   - Run CMD in the Linux dev container, e.g. make container-run CMD='prek run --files a.yml'"
	@echo "  help            - Show this help message"

lint:
	@command -v prek > /dev/null || { echo "Error: 'prek' not found. Run 'make install-dev' first."; exit 1; }
	@prek run --all-files

install-dev:
	@command -v prek > /dev/null || pip install 'prek>=0.4.3'
	@prek install

update-actions:
	@echo "Updating pinned actions in GitHub workflows..."
	@docker run --rm -v "$(CURDIR):/workflows" mheap/pin-github-action .github/workflows/

# Keep $ in CMD for the shell: make expands an exported variable.
override CMD := $(value CMD)
export CMD

container-lint:
	@.devcontainer/run.sh prek run --all-files

container-shell:
	@.devcontainer/run.sh

container-run:
	@test -n "$$CMD" || { echo "Error: set CMD, e.g. make container-run CMD='prek run --files a.yml'"; exit 1; }
	@.devcontainer/run.sh sh -c "$$CMD"
