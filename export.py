#!/usr/bin/python
from divessi.api import SSIApi
from params import username, password
import csv


def main():
    response = SSIApi(username, password).get_divelog()
    with open('divelog.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=response[0].keys())
        writer.writeheader()

        for dive in response:
            writer.writerow(dive)


if __name__ == "__main__":
    main()
