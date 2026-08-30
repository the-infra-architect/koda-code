# SonarQube Cloud

The workflow contains an optional `sonar` job using the official scanner action. It runs only when
the repository variable `SONAR_ENABLED` is `true` and requires:

- secret `SONAR_TOKEN`
- variable `SONAR_PROJECT_KEY`
- variable `SONAR_ORGANIZATION`

Set the variables in the private repository and update `sonar-project.properties` only with the
owner-approved project identity. Pull-request analysis also requires the repository and SonarQube
Cloud project to be connected.

Sonar is an additional signal. It does not replace tests, review, security analysis, or the local
quality gate.

