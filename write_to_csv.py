import csv
import os

def process_phone_csv(number, content, output_file="output.csv"):
    file_exists = os.path.isfile(output_file)

    with open(output_file, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["numbers", "reason"])

        # Write header only if file is new
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "numbers": number,
            "reason": content
        })
    