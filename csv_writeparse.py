import pandas as pd

def process_phone_csv(input_file, output_file="output.csv"):
    # Read input CSV
    df = pd.read_csv(input_file)

    # Check required column
    if "phone" not in df.columns:
        raise ValueError("CSV must contain a 'phone' column")

    output_rows = []

    for phone in df["phone"]:
        # desc = transcribe(audio)
        desc = ""

        output_rows.append({
            "phone": phone,
            "desc": desc
        })

    # Write output CSV
    out_df = pd.DataFrame(output_rows)
    out_df.to_csv(output_file, index=False)

    return output_file