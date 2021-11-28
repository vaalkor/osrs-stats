#!/bin/bash
#
# Builds, tests and then publishes the project.
#=====================================================================#
#=====================================================================#

print_var() { echo "$1: ${!1}"; }
err() { echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2; exit 1; }
validate_var() { [ "${!1}" ] || err "No $1 defined. Quitting..."; }
validate_vars() { for var in "$@"; do validate_var "$var"; done }

#=====================================================================#
#=====================================================================#

dotnet restore
dotnet build --no-restore
dotnet test --no-build --verbosity normal
dotnet publish -c Release

cd SimpleStatsServer/bin/Release/netcoreapp2.1/publish || err "Could not switch to publish directory!"

FILENAME=SimpleStatsServer-"$GITHUB_RUN_ID".zip
echo "Zipping files to $FILENAME" 

find . -type f -exec zip "$FILENAME" {} +

aws s3 cp "$FILENAME" s3://vaalkor-app-builds/SimpleStatsServer/"$FILENAME"