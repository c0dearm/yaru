# Contributing

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## How to Contribute

### Fork and branch

We follow the usual GitHub flow:

1. **Fork the Repository**: Fork the project repository to your GitHub account.
2. **Clone the Repository**: Clone your forked repository to your local machine.
   ```bash
   git clone https://github.com/YOUR_USERNAME/yaru.git
   ```
3. **Create a Branch**: Create a new branch for your feature or bug fix.
   ```bash
   git checkout -b your-branch-name
      ```

### Testing and code quality

The only requirement to start working is to have [uv](https://docs.astral.sh/) installed. Once
you do, you can create a virtual environment with all the required development dependencies
installed with:

```bash
uv sync --all-groups
```

Once you have made your changes, you can run all the tests by using `yaru` itself(!). We don't allow
merging Pull Requests that don't pass the tests.

```bash
yaru run-tests --docs --coverage
```

We leverage the use of [pre-commit](https://pre-commit.com/) to guarantee code style and quality
consistency across all our contributions. It is part of our development dependencies, so if you are
already within the virtual environment you just need to run:

```bash
pre-commit install
```

This will install itself as git hook, so that it will automatically lint your changes everytime you create
a new commit. Note also, that if needed you can lint your changes anytime without having to create a new commit with:

```bash
pre-commit run --all-files
```

The `pre-commit` lints are also run by our CI pipelines, so if they fail your Pull Request won't be allowed to
be merged either.

### Create a Pull Request

We follow the usual GitHub flow:

1. **Commit Your Changes**: Commit your changes with a [conventional](https://www.conventionalcommits.org/en/v1.0.0/) commit message.
   ```bash
    git add .
    git commit -m "added(docs)[YARU-1]: create the CONTRIBUTING.md file"
   ```
2. **Push Your Changes**: Push your changes to your forked repository.
   ```bash
    git push origin your-branch-name
   ```
3. **Create a Pull Request**: Open a pull request from your branch to the main repository.

## Reporting Issues

If you find a bug or have a feature request, please [open an issue](https://github.com/c0dearm/yaru/issues/new) on GitHub.

## License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE).

---

Feel free to suggest improvements to these guidelines!
