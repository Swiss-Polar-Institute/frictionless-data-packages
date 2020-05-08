import csv
import argparse
import datetime


def convert_isodatetime_in_file(input_file, output_file, date_time_column_header):
    """
    Import rows from a file, get the ISO datetime and convert it to a timestamp (secs since start of 1970) for one row,
     then append the time column to an output file.
    """
    missing_values = ['', 'NaN', 'NA', 'NAN']

    with open(input_file) as input_csv_file:
        csv_reader = csv.reader(input_csv_file, delimiter=',')
        with open(output_file, 'w') as output_csv_file:
            csv_writer = csv.writer(output_csv_file)

            row_count = 0
            for row in csv_reader:
                if row_count % 10 == 0 and row_count != 0:
                    print(f'Converted {row_count} rows')

                if row_count == 0:
                    header = row
                    date_time_column = header.index(date_time_column_header)
                    header.append('time')
                    csv_writer.writerow(header)
                    row_count += 1
                    continue

                row_count += 1

                isodatetime = row[date_time_column]
                if isodatetime in missing_values:
                    row.append(isodatetime)
                    csv_writer.writerow(row)
                    continue

                try:
                    isodatetime_dt = datetime.datetime.strptime(isodatetime, '%Y-%m-%dT%H:%M:%S%z')
                except ValueError:
                    isodatetime_dt = None

                if isodatetime_dt is not None:
                    secssince1970 = isodatetime_dt.timestamp()
                    row.append(secssince1970)
                    csv_writer.writerow(row)
                else:
                    print("Date time not processed: ", isodatetime)

            output_csv_file.close()
        input_csv_file.close()

        print('Total rows converted:', row_count)


def main():
    parser = argparse.ArgumentParser(description='Convert ISO datetime to seconds since 1907-01-01T00:00:00Z in '
                                                 'INPUT_FILE and write out the new rows to OUTPUT_FILE')
    parser.add_argument('input_file', help='Input filepath and name')
    parser.add_argument('output_file', help='Output filepath and name')
    parser.add_argument('date_time_column_header', help='Header of date_time column in input file')

    args = parser.parse_args()

    convert_isodatetime_in_file(args.input_file, args.output_file, args.date_time_column_header)


if __name__ == "__main__":
    main()
