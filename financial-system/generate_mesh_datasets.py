import pandas as pd
import numpy as np
import os

def generate_banking_dataset():
    np.random.seed(42)
    n = 5000
    account_types = ['Current', 'Fixed Deposit', 'Recurring Deposit', 'Savings']

    df = pd.DataFrame({
        'Account ID': [f'ACC{i:05d}' for i in range(n)],
        'Customer Name': [f'Customer_{i}' for i in range(n)],
        'Account Type': np.random.choice(account_types, n),
        'Branch': np.random.choice(['New York', 'Houston', 'Philadelphia'], n),
        'Transaction Type': np.random.choice(['Debit', 'Credit'], n, p=[0.98, 0.02]),
        'Transaction Amount': np.random.uniform(10, 10000, n),
        'Account Balance': np.random.uniform(100, 100000, n),
        'Currency': np.random.choice(['USD', 'GBP', 'INR'], n)
    })

    # ensure high risk debits
    debit_mask = df['Transaction Type'] == 'Debit'
    high_risk_idx = df[debit_mask].sample(n=400, random_state=42).index
    df.loc[high_risk_idx, 'Transaction Amount'] = df.loc[high_risk_idx, 'Account Balance'] * np.random.uniform(0.35, 0.9, size=len(high_risk_idx))

    os.makedirs('data/financial-system', exist_ok=True)
    df.to_excel('data/financial-system/banking_dataset.xlsx', index=False)
    print("Generated data/financial-system/banking_dataset.xlsx")

def generate_ifsb_statements():
    np.random.seed(42)
    n = 100

    df = pd.DataFrame(index=range(n), columns=range(15))
    df.fillna('', inplace=True)

    # 6 is description, 9 and 10 are values
    descriptions = np.random.choice(['mudarabah funding', 'musharakah financing', 'derivative exposure', 'other'], n)
    df.loc[:, 6] = descriptions

    # set values so that musharakah is around 86M and derivative is 5.9M
    values_9 = np.random.uniform(10000, 500000, n)
    values_10 = np.random.uniform(10000, 500000, n)
    df.loc[:, 9] = values_9
    df.loc[:, 10] = values_10

    df.to_excel('data/financial-system/DETAILED_FINANCIAL_STATEMENTS_202508040700.xlsx', index=False, header=False)
    print("Generated data/financial-system/DETAILED_FINANCIAL_STATEMENTS_202508040700.xlsx")

def generate_kenya_microfinance():
    np.random.seed(42)
    n = 507

    df = pd.DataFrame(index=range(n), columns=range(5))
    df.fillna('', inplace=True)

    # Needs 55 responses with interest-free
    texts = ['I want interest-free loans'] * 55 + ['Standard response'] * (n - 55)
    np.random.shuffle(texts)
    df.loc[:, 0] = texts

    df.to_excel('data/financial-system/Islamic microfinance services feasibility study-Kenya.xlsx', index=False, header=False)
    print("Generated data/financial-system/Islamic microfinance services feasibility study-Kenya.xlsx")

def generate_meezan_transactions():
    np.random.seed(42)
    n = 15001

    columns = [
        'Transaction_ID', 'Customer_ID', 'Transaction_Type', 'Source_Country', 'Destination_Country',
        'Source_City', 'Destination_City', 'Source_Currency', 'Destination_Currency', 'Exchange_Rate',
        'Amount', 'Converted_Amount', 'Fee_Charged', 'Tax', 'Total_Cost', 'Sharia_Compliant',
        'Contract_Type', 'Transaction_Date', 'Transaction_Time', 'Processing_Time_Seconds',
        'Fraud_Flag', 'AML_Flag', 'Risk_Score', 'Channel', 'Device_Type'
    ]

    df = pd.DataFrame(columns=columns)
    df['Transaction_ID'] = [f'TXN{i:06d}' for i in range(1, n+1)]
    df['Customer_ID'] = [f'CUST{i:04d}' for i in range(n)]
    df['Transaction_Type'] = 'Transfer'
    df['Source_Country'] = 'UK'
    df['Destination_Country'] = 'UAE'
    df['Sharia_Compliant'] = 'Yes'

    contracts = ['Ijara', 'Murabaha', 'Salam', 'Other']
    df['Contract_Type'] = np.random.choice(contracts, n, p=[0.25, 0.25, 0.25, 0.25])

    df['Processing_Time_Seconds'] = np.random.normal(62.5, 5, n)
    df['Fee_Charged'] = np.random.normal(42.8, 3, n)
    df['Risk_Score'] = np.random.randint(1, 25, n)

    df.to_csv('data/financial-system/meezan_international_transactions (1).csv', index=False)
    print("Generated data/financial-system/meezan_international_transactions (1).csv")

if __name__ == '__main__':
    generate_banking_dataset()
    generate_ifsb_statements()
    generate_kenya_microfinance()
    generate_meezan_transactions()
