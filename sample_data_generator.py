import pandas as pd
import numpy as np
from pathlib import Path

def generate_sample_data():
    np.random.seed(42)
    
    markets = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East']
    ledgers = [
        'Revenue - Product Sales',
        'Revenue - Services',
        'COGS - Materials',
        'COGS - Labor',
        'COGS - Overhead',
        'SG&A - Marketing',
        'SG&A - Sales',
        'SG&A - Admin',
        'R&D - Development',
        'R&D - Research',
        'Depreciation',
        'Interest Expense',
        'Other Income',
        'Tax Expense'
    ]
    
    months = ['2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12']
    
    Path("sample_data").mkdir(exist_ok=True)
    
    base_values = {
        'Revenue - Product Sales': 1000000,
        'Revenue - Services': 300000,
        'COGS - Materials': -400000,
        'COGS - Labor': -200000,
        'COGS - Overhead': -100000,
        'SG&A - Marketing': -80000,
        'SG&A - Sales': -120000,
        'SG&A - Admin': -60000,
        'R&D - Development': -50000,
        'R&D - Research': -30000,
        'Depreciation': -25000,
        'Interest Expense': -15000,
        'Other Income': 10000,
        'Tax Expense': -50000
    }
    
    market_multipliers = {
        'North America': 1.5,
        'Europe': 1.2,
        'Asia Pacific': 1.0,
        'Latin America': 0.6,
        'Middle East': 0.4
    }
    
    for i, month in enumerate(months):
        data = []
        growth_factor = 1 + (i * 0.02)
        
        for market in markets:
            for ledger in ledgers:
                base = base_values[ledger] * market_multipliers[market] * growth_factor
                actual = base * (1 + np.random.uniform(-0.1, 0.15))
                plan = base * (1 + np.random.uniform(-0.05, 0.05))
                forecast = base * (1 + np.random.uniform(-0.08, 0.08))
                
                data.append({
                    'Market': market,
                    'Ledger Account': ledger,
                    'Actual': round(actual, 2),
                    'Plan': round(plan, 2),
                    'Forecast': round(forecast, 2)
                })
        
        df = pd.DataFrame(data)
        filename = f"sample_data/financial_report_{month}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Generated: {filename}")
    
    ledger_mapping = pd.DataFrame([
        {'ledger': 'Revenue - Product Sales', 'bucket': 'Revenue', 'driver': 'Volume', 'controllable': True},
        {'ledger': 'Revenue - Services', 'bucket': 'Revenue', 'driver': 'Volume', 'controllable': True},
        {'ledger': 'COGS - Materials', 'bucket': 'COGS', 'driver': 'Volume', 'controllable': True},
        {'ledger': 'COGS - Labor', 'bucket': 'COGS', 'driver': 'Headcount', 'controllable': True},
        {'ledger': 'COGS - Overhead', 'bucket': 'COGS', 'driver': 'Fixed', 'controllable': False},
        {'ledger': 'SG&A - Marketing', 'bucket': 'SG&A', 'driver': 'Discretionary', 'controllable': True},
        {'ledger': 'SG&A - Sales', 'bucket': 'SG&A', 'driver': 'Headcount', 'controllable': True},
        {'ledger': 'SG&A - Admin', 'bucket': 'SG&A', 'driver': 'Fixed', 'controllable': False},
        {'ledger': 'R&D - Development', 'bucket': 'R&D', 'driver': 'Project', 'controllable': True},
        {'ledger': 'R&D - Research', 'bucket': 'R&D', 'driver': 'Project', 'controllable': True},
        {'ledger': 'Depreciation', 'bucket': 'Non-Cash', 'driver': 'Fixed', 'controllable': False},
        {'ledger': 'Interest Expense', 'bucket': 'Financing', 'driver': 'Fixed', 'controllable': False},
        {'ledger': 'Other Income', 'bucket': 'Other', 'driver': 'Variable', 'controllable': False},
        {'ledger': 'Tax Expense', 'bucket': 'Tax', 'driver': 'Calculated', 'controllable': False}
    ])
    ledger_mapping.to_excel("sample_data/ledger_mapping.xlsx", index=False)
    print("Generated: sample_data/ledger_mapping.xlsx")

if __name__ == "__main__":
    generate_sample_data()

