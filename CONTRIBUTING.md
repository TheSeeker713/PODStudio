# Contributing to PODStudio

Thank you for your interest in contributing to PODStudio! This document provides guidelines and instructions for contributing.

## Branching Model

We use a trunk-based development model with feature branches:

- **`main`**: Default branch; always stable, deployable code
- **`feat/<short-name>`**: Feature branches (e.g., `feat/bg-removal`, `feat/pack-builder`)
- **`fix/<short-name>`**: Bugfix branches (e.g., `fix/gpu-detection`)
- **`release/v0.x`**: Release preparation branches
- **`docs/<short-name>`**: Documentation-only changes

### Workflow

1. Create a feature branch from `main`:
   ```powershell
   git checkout main
   git pull origin main
   git checkout -b feat/your-feature-name
   ```

2. Make changes, commit frequently with conventional commits (see below)

3. Push and create a Pull Request:
   ```powershell
   git push origin feat/your-feature-name
   ```

4. Request review, address feedback, merge when approved

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style/formatting (no logic change)
- **refactor**: Code restructuring (no feature/fix)
- **perf**: Performance improvements
- **test**: Adding/updating tests
- **chore**: Tooling, dependencies, config

### Examples

```
feat(ui): add collapsible dock panels

Implement QDockWidget-based layout with user-configurable
dock positions and visibility toggles.

Closes #42
```

```
fix(worker): handle ffmpeg timeout on large videos

Add 5-minute timeout with graceful cancellation for video
transcoding jobs to prevent worker hangs.

Fixes #89
```

## Code Quality

### Pre-commit Hooks

All commits are checked by pre-commit hooks:

```powershell
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Linting & Formatting

```powershell
# Lint
ruff check .

# Format
black .
isort .
```

### Type Checking (Optional)

```powershell
mypy app/
```

## Testing

### Running Tests

```powershell
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/unit/test_thumbnails.py -v
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names: `test_thumbnail_generation_for_png_image()`
- Mock external dependencies (FFmpeg, GPU libraries)
- Use golden files for media processing tests

## Pull Request Process

1. **Pre-flight checks**:
   - [ ] All tests pass (`pytest`)
   - [ ] Pre-commit hooks pass
   - [ ] Code coverage maintained (>80%)
   - [ ] Documentation updated (if applicable)

2. **PR Description**:
   - Link to related issue(s)
   - Summary of changes
   - Screenshots/GIFs for UI changes
   - Breaking changes noted

3. **Review**:
   - At least one approval required
   - Address all comments before merging
   - Squash-merge into `main` (keep history clean)

## Documentation

- All features must have corresponding documentation in `/docs`
- Update relevant `.md` files when changing behavior
- Use diagrams for complex flows (ASCII art or Mermaid)

## Issue Reporting

Use GitHub issue templates:

- **Bug Report**: [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- **Feature Request**: [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)

Include:
- OS version (Windows 10/11)
- Python version
- Hardware specs (GPU, RAM)
- Steps to reproduce (for bugs)

## Development Setup

See [docs/ops/install_windows.md](docs/ops/install_windows.md) for full setup instructions.

## Questions?

- Open a [Discussion](https://github.com/<youruser>/PODStudio/discussions)
- Check [docs/ops/troubleshooting.md](docs/ops/troubleshooting.md)

---

Thank you for contributing! 🎉
