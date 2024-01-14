# night-train-data
Night train data

This repository provides a version of static data from the Back-on-Track night trains database which can be used for various purposes including the night train map which is used for the BoT website.

## How to get
Data is currently stored in a google sheet. It can be extracted by using the [google apps script](./scripts/code.gs)

## How to update the data held in this repository
1. run code.gs as a google apps script for the tables you wish to extract data.
OR use get_snapshot.py which uses the currently hosted version of the script
2. create a pull request with the new files.

