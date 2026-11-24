.DEFAULT_GOAL := help

.PHONY: help lint install-dev update-actions container-shell container-run

help:
	@echo "Available targets:"
	@echo "  lint            - Run all prek hooks across the whole repository, as CI does"
	@echo "  install-dev     - Register the git pre-commit hook"
	@echo "  update-actions  - Update pinned actions in GitHub workflows"
	@echo "  container-shell - Start a shell in the Linux dev container"
	@echo "  container-run   - Run CMD in the Linux dev container, e.g. make container-run CMD='prek run --files a.yml'"
	@echo "  help            - Show this help message"
	@echo "lint, install-dev, and the container targets use the dev container. Docker must be installed."

lint:
	@.devcontainer/run.sh prek run --all-files --show-diff-on-failure

install-dev:
	@hook="$$(git rev-parse --git-path hooks)/pre-commit"; \
	if [ -e "$$hook" ] && ! grep -q prek "$$hook"; then \
		echo "Error: $$hook is not a prek hook. Remove it, then run this target again."; exit 1; \
	fi; \
	install -m 0755 .devcontainer/pre-commit "$$hook" && echo "Installed $$hook"

update-actions:
	@echo "Updating pinned actions in GitHub workflows..."
	@docker run --rm -v "$(CURDIR):/workflows" mheap/pin-github-action .github/workflows/

# Keep $ in CMD for the shell: make expands an exported variable.
override CMD := $(value CMD)
export CMD

container-shell:
	@.devcontainer/run.sh

container-run:
	@test -n "$$CMD" || { echo "Error: set CMD, e.g. make container-run CMD='prek run --files a.yml'"; exit 1; }
	@.devcontainer/run.sh sh -c "$$CMD"
