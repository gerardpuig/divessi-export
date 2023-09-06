# DiveSSI export

![license](https://img.shields.io/github/license/gerardpuig/divessi-export.svg)
[![Tests](https://github.com/gerardpuig/divessi-export/workflows/Tests/badge.svg)](https://github.com/gerardpuig/divessi-export/actions/workflows/tests.yml)

This is a simple python script to export all your dive logs from the DiveSSI app. The fields in the export are the ones I have selected to be the most useful but feel free to add any other field you may find relevant.

## Install

Copy the example params and set your own credentials:

```sh
cp params.example.py params.py
```

## Usage

Run the export.py provided, it will use the divessi api to generate a divelog.csv file:

```sh
python export.py
```

## Tests

```sh
make tests
```

## Motivations

- Current [DiveSSI website](https://divessi.com) has less data that what you can add from the app, although you can see the same dive logs you are not able to retrieve all the fields. Website looks like a limited version from the app.
- It's not possible to get a backup from the website, there is an export that generates a csv but it's very limited, you are missing a lot of information.
- You should be able to get your own data and do as you see fit, maybe just to have your local backup or to export to another divelog app.
