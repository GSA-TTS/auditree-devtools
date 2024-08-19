# Auditree Devtools

This image contains the necessary configuration and code for running Auditree validations
for DevTools-flavored applications.

## Use in your project

1. Create a new github repository to store your auditree evidence and reports. *Important* Add a default README with the gitub UI, so that there is a single commit in the repo before running Auditree.
1. Initialize the config file: `docker run --rm ghcr.io/gsa-tts/auditree init > path/to/auditree.template.json`
1. Edit the generated config to insert the proper repository addresses for both your evidence locker repo and code repo.
1. TKTK instructions for actual use coming soon.

### Updating the Docker image:

1. Make required changes
1. Push to GitHub and create a PR
1. On merging to main, a new docker image will be built, tagged, and pushed to the github container registry.

Each published image will be tagged with:

1. `latest`
1. The publication date: `YYYYMMDD`
1. The branch it was created on: `main`
1. The short git sha: `sha-c9f60e2`
