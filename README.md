# Codeforces Archive

Automatically synchronizes accepted **Codeforces** submissions to GitHub using **GitHub Actions**.

## ⚙️ Architecture

```mermaid
flowchart TD
    A([GitHub Actions])
    B[Fetch Recent Submissions]
    C{Accepted?}
    D[Skip]
    E{Already Synced?}
    F[Skip]
    G[Save Solution]
    H[Update History]
    I[Commit & Push]

    A --> B
    B --> C
    C -- No --> D
    C -- Yes --> E
    E -- Yes --> F
    E -- No --> G
    G --> H
    H --> I
```

## 📂 Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── codeforces_commit.yml
├── submissions/
├── fetch_submission.py
├── submission_history.json
└── README.md
```

## ✨ Features

* Automatically syncs newly accepted Codeforces submissions
* Runs every 15 minutes via GitHub Actions
* Prevents duplicate uploads using submission history
* Preserves the correct file extension for each programming language
* Supports manual workflow execution from GitHub Actions

## 💻 Supported Languages

Works with all major languages supported by Codeforces, including:

* C++
* Python
* Java
* Kotlin
* Go
* Rust
* JavaScript
* TypeScript
* C#
* PHP
