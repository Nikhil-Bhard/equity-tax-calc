import streamlit as st
import pandas as pd
from datetime import datetime

st.title("📊 Equity Capital Gains Tax Calculator (Budget 2024)")

st.write("""
Upload your Excel file with the following columns:
- **Purchase Date**
- **Sell Date**
- **Purchase Price**
- **Sell Price**
- **Brokerage & Other Charges**
""")

# File uploader
uploaded_file = st.file_uploader("Upload Excel", type=["xlsx", "xls", "csv"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Ensure proper column names
    df.columns = [c.strip().lower() for c in df.columns]

    required_cols = ["purchase date", "sell date", "purchase price", "sell price", "brokerage & other charges"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"Your file must contain these columns: {required_cols}")
    else:
        # Process data
        results = []
        for _, row in df.iterrows():
            try:
                purchase_date = pd.to_datetime(row["purchase date"])
                sell_date = pd.to_datetime(row["sell date"])
                holding_period = (sell_date - purchase_date).days
                purchase_price = row["purchase price"]
                sell_price = row["sell price"]
                charges = row["brokerage & other charges"]

                # Net gain
                net_gain = sell_price - purchase_price - charges

                # STCG or LTCG
                gain_type = "STCG" if holding_period <= 365 else "LTCG"

                # Tax rate logic
                cutover_date = datetime(2024, 7, 23)
                if gain_type == "STCG":
                    rate = 15 if sell_date < cutover_date else 20
                    taxable_gain = net_gain
                else:  # LTCG
                    exemption = 100000 if sell_date < cutover_date else 125000
                    rate = 10 if sell_date < cutover_date else 12.5
                    taxable_gain = max(0, net_gain - exemption)

                # Tax amount
                tax_amount = taxable_gain * rate / 100

                results.append({
                    "Purchase Date": purchase_date.date(),
                    "Sell Date": sell_date.date(),
                    "Type": gain_type,
                    "Net Gain (₹)": net_gain,
                    "Taxable Gain (₹)": taxable_gain,
                    "Rate (%)": rate,
                    "Tax Amount (₹)": tax_amount
                })
            except Exception as e:
                st.error(f"Error processing row: {e}")

        result_df = pd.DataFrame(results)

        st.success("✅ Calculation complete!")
        st.dataframe(result_df)

        # Download option
        out_filename = "Equity_Tax_Results.xlsx"
        result_df.to_excel(out_filename, index=False)
        with open(out_filename, "rb") as f:
            st.download_button("⬇️ Download Results (Excel)", f, file_name=out_filename)
