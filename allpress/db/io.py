
import csv


def import_news_sources_from_file(filepath: str) -> list:
    csvfile = open(filepath, 'r', newline='')
    csv_reader = csv.reader(csvfile)
    csv_values = []
    for line in csv_reader:
        csv_values.append(line)
    return csv_values