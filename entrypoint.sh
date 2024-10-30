#! /usr/bin/env bash

if [ "$1" != "init" ]; then
  if [ -z "$GITHUB_TOKEN" ]; then
    echo "Must pass github token to script"
    exit 1
  fi
  if [ -z "$GIT_EMAIL" ]; then
    echo "Must pass email address for git config to script as GIT_EMAIL"
    exit 1
  fi

  # 1) configure git
  git config --global user.name "$GIT_EMAIL"
  git config --global user.email "$GIT_EMAIL"

  # 2) set cloud.gov api endpoint
  cf api api.fr.cloud.gov > /dev/null
fi

# 3) call program
exec "$@"
