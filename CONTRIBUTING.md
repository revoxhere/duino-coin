# Contribution Guide

Welcome to the Duino-Coin Master Server contribution guide!

Before you begin, please read and follow all the instructions in this document so your contribution can be integrated smoothly.

---

## Preparing the Environment

1. **Fork** this repository using the `Fork` button at the top.

2. **Clone your fork locally**:
```bash
git clone https://github.com/YOUR_USERNAME/duco-main
cd duco-main
```

3. **Install Rust**

Make sure you have the latest stable Rust toolchain installed:
```bash
rustup install stable
rustup default stable
```

Verify the installation:
```bash
rustc --version
cargo --version
```

4. **Install project dependencies**

Rust dependencies are managed automatically by Cargo:
```bash
cargo fetch
```

5. **Configure [Lefthook](https://github.com/evilmartians/lefthook)**  
This is mandatory to ensure code consistency:
```bash
lefthook install
```

---

## Code Style & Formatting

Before committing, ensure your code is properly formatted and linted:

```bash
cargo fmt
cargo clippy --all-targets --all-features -- -D warnings
```

These checks are also enforced automatically by Lefthook.

---

## Commit Conventions

* We use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard.
* **Do not use emojis** in commit messages.
* Lefthook will validate commit messages automatically.
* The standard format is:

```
<type>(optional scope): description
```

Example:
```
feat(network): add connection rate limiting
```

---

## Pull Requests

1. Always work on a new branch created from `main`:
```bash
git checkout -b feat/your-feature-name
```

2. Make sure your code passes formatting, linting, and tests:
```bash
cargo fmt
cargo clippy
cargo test
```

3. Write a clear and concise description in the pull request:
   - What was changed
   - Why it was changed

4. Name the pull request consistently with the main commit message  
   (following **Conventional Commits**).

5. Wait for review. You may be asked to update your code if it does not meet the project's standards or guidelines.

---

## Additional Notes

- Keep changes focused and minimal.
- Avoid unrelated refactors in the same PR.
- Prefer clear, explicit code over clever tricks.
