# base-user-image template

This is a template repository for creating dedicated single-user server images
for Cal-ICOR Jupyterhubs.

## Creating a new user image repository

This repo can be used as a template to create a new image for Jupyterhub
deployments.

**Important!** Do not create a *fork* of this repository, as a fork is designed
to track the commit history of both itself and the parent (upstream)
repositories.  Instead, we want the new image repo (created as a template) to
have it's own history starting upon creation.

### Basic workflow for creating a new hub user image

#### 1. Create a new repository using this one as a template

Be sure to set the owner as `cal-icor` and `Public` visibility.

![click on the upper right corner and use the template to create a new repo](images/template.png)

![settings for the new repo](images/new-repo.png)

#### 2. Set the new image secrets and variables

In the new repo, under `Settings`, select `Secrets and Variables` on the left
menu bar, and then click on `Variables`. Add repository variables for `HUB`
(name of the hub -- optional) and `IMAGE` (relative path to the image in GAR).

`IMAGE` needs to be prepended by `cal-icor-hubs/user-images/`, which is the
path where we store user images in GAR.

The final value for `IMAGE` should be:

``` bash
cal-icor-hubs/user-images/<name-of-user-image>
```

![variables](images/actions-variables.png)

#### 3. Create a fork the new repository

To perform work on the new image, you first need to create a fork of the new
one. When your fork is created, turn off the Github Actions so they only run
on the new image repo.  This is found under `Settings --> Actions --> General`,
then click on `Disable actions` and save.

![disable actions in your fork](images/disable-actions.png)

#### 4. Clone the new repo and set git remotes

Clone the new image repo to your device, and then set the git remotes to have
`upstream` point to the repo in the `cal-icor` org, and `origin` pointing to
your fork.

``` bash
git clone git@github.com:cal-icor/fancy-new-user-image.git
git remote rename origin upstream
git remote add origin git@github.com:<username>/fancy-new-user-image.git
```

When completed, `git remote -v` should show this:

``` bash
$ git remote -v
origin  git@github.com:<username>/fancy-new-user-image.git (fetch)
origin  git@github.com:<username>/fancy-new-user-image.git (push)
upstream        git@github.com:cal-icor/fancy-new-user-image.git (fetch)
upstream        git@github.com:cal-icor/fancy-new-user-image.git (push)
```

#### 5. Configure hubs to use this new image

You can have a hub use the new image by modifying that deployment's
`common.yaml`.  Here's [an example](https://github.com/cal-icor/cal-icor-hubs/blob/staging/deployments/csumb/config/common.yaml#L19)
for a live hub.

#### 6. Customize the image

If you need to change any of the default packages, do so by editing the
[`repo2docker` configuration files](https://repo2docker.readthedocs.io/en/latest/configuration/)
on a feature branch in your fork of the image repository, and then open a pull
request to merge these changes to the `main` branch of the parent repo in the
`cal-icor` organization.  More detailed instructions are found in
[CONTRIBUTING.md](https://github.com/cal-icor/base-user-image/blob/main/CONTRIBUTING.md).

#### 7. Update the new image's README

In addition, we also provide a template for a simplified `README.md`
[here](https://github.com/cal-icor/cal-icor-hubs/blob/main/README-template.md).
We strongly recommend replacing the original `README.md` with an updated
version from this template.

These steps are just a summary, and much more detailed instructions are
[located here](https://docs.cal-icor.org/new-image/).

### Modifying the new image

The process to modify and push an image to the Google Artifact Registry via the
CI/CD pipeline is located in the [contribution guide](CONTRIBUTING.md)

### Moving an existing image into the `cal-icor` organization

If you have an existing image repository, and would like to bring it in to the
`cal-icor` organization and retain the `git` history, please refer
to our documentation :arrow_right:
https://docs.datahub.berkeley.edu/admins/howto/transition-image.html

Our documentation is based on helpful guide put together by 2i2c :arrow_right:
https://infrastructure.2i2c.org/howto/update-env/#split-up-an-image-for-use-with-the-repo2docker-action

## About this template repository

This template repository uses the
[jupyterhub/repo2docker-action](https://github.com/jupyterhub/repo2docker-action)
to build a Docker image using the contents of this repo, and pushes it to our
[Google Artifact Registry](https://cloud.google.com/artifact-registry) when
a pull request is merged to `main`.

### The environment

The repo provides a default `environment.yml` conda configuration file for
`repo2docker` to use to define and build a single-user server image. This file
is used to define the python packages that will be installed during the image
build process, either via `conda` or `pip`.

If you want to do a more customized image build, you can always convert this
image to be built from a `Dockerfile`.  One example is the
[CSUMB user image](https://github.com/cal-icor/csumb-user-image)

**Note:**
A complete list of configuration files that can be added to the
repository and used by `repo2docker` to build the Docker image can be found in
the [repo2docker documentation](https://repo2docker.readthedocs.io/en/latest/config_files.html#configuration-files).

### Making changes to a single user server image

Once you've created the new image repo from this template, please refer to
[the contribution instructions](CONTRIBUTING.md) located in the repo for
detailed instructions.

### The GitHub Action workflows

This template repository provides GitHub Action workflows that can build
and push the image to Google Artifact Repository when configured, and push a
commit to the [Cal-ICOR Jupyterhub repo](https://github.com/cal-icor/cal-icor-hubs)
repository that modifies `hubploy.yaml` for any hubs using this image with the
new SHA tag.

#### 1. Lint workflow files on pull requests :arrow_right: [action-lint-prs.yaml](https://github.com/cal-icor/shared-workflows/blob/main/.github/workflows/action-lint-prs.yaml)

This workflow run a yaml linter as well as [Reviewdog's Action Linter](https://github.com/reviewdog/action-actionlint) on all PRs.

#### 2. Build and test container image :arrow_right: [build-test-image.yaml](https://github.com/cal-icor/shared-workflows/blob/main/.github/workflows/build-test-image.yaml)

This workflow is triggered when a pull request is opened against the default
branch (`main`). During PR builds, the image is **only** built and **not**
pushed to the Google Artifact Registry.

Please note that the image will not be built for documentation changes
(markdown files or any graphic images in the `images/` subdirectory).

#### 3. Build, test and push container image :arrow_right: [build-push-open-pr.yaml](https://github.com/cal-icor/shared-workflows/blob/main/.github/workflows/build-push-create-pr.yaml)

After a PR is merged to `main`, this workflow builds the image again, pushes it
to the Google Artifact Registry and then creates a commit that updates the image tag
for any hubs that use this image. That commit is then pushed to the 
[Cal-ICOR Jupyterhub repo](https://github.com/cal-icor/cal-icor-hubs), and you will
then need to manually create a pull requests to merge and deploy the new image.
