# Continuous Integration

The GitHub Actions workflow runs on pull requests and protected-branch pushes. It tests Python 3.11,
3.12, and 3.13, with the full quality gate on 3.11 and tests on every supported version.

The security job performs static security analysis, the deterministic tracked-file secret scan, and
dependency vulnerability auditing. The package job builds both distribution formats.

Sonar analysis is optional and isolated from ordinary CI so a missing external credential does not
block local development or pretend to be a successful hosted analysis.

