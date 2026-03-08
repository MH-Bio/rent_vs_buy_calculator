"""
This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/

DISCLAIMER:
This software is provided "as is", without warranty of any kind, expressed or implied.
The author makes no representations or guarantees regarding the accuracy,
completeness, or reliability of the calculations or information contained in
this code.

This code is intended for educational and informational purposes only and
should not be considered financial, legal, or tax advice. Use of this software
is entirely at your own risk. Users should consult a qualified tax or financial
professional before making any decisions based on the results produced by this
program.

IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY,
INCLUDING BUT NOT LIMITED TO DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES ARISING FROM THE USE OF, OR INABILITY TO USE, THIS SOFTWARE.

Run all combinations for various variables and create a list of all combinations from best to worst

Date: March 7, 2026
Author: Michael C. Hernandez
email: michaelhern@hotmail.com
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import rent_vs_buy_calculator as calculator
from matplotlib.ticker import ScalarFormatter
import itertools

def combinations(home_value: int = 350000, interest_rate: float = 6.25, your_rent: int = 1800, filing_status: str = "single", income: int = 100000):

    down_payments: list = []
    for i in range(0, 50001, 10000):
        down_payments.append(i)

    sell_year: list = []
    for i in range(1, 31, 1):
        sell_year.append(i)

    years_in_house: list = []
    for i in range(1, 5, 1):
        years_in_house.append(i)
    
    annual_extra_payment: list = []
    for i in range(0, 30001, 10000):
        annual_extra_payment.append(i)

    extra_payment_years: list = []
    for i in range(5):
        extra_payment_years.append(i)

    stock_instead_of_house: list = [True, False]

    params = {
        "down_payment": down_payments,
        "sell_year": sell_year,
        "years_in_house": years_in_house,
        "annual_extra_payment": annual_extra_payment,
        "extra_payment_years": extra_payment_years,
        "stock_instead_of_house": stock_instead_of_house
    }

    keys = params.keys()
    values = params.values()

    all_combinations = [
        dict(zip(keys, combo))
        for combo in itertools.product(*values)
    ]

    # Remove invalid combinations
    all_combinations = [
        combo for combo in all_combinations
        if combo["sell_year"] >= combo["years_in_house"]
    ]

    all_combinations = [
        combo for combo in all_combinations
        if combo["years_in_house"] >= combo["extra_payment_years"]
    ]

    df_list: list = []
    
    scenario_results = []

    print(f"Running {len(all_combinations)} scenarios... This could take a while...")
    for combination in all_combinations:

        df = calculator.calculator(
            house_price=home_value,
            down_payment=combination["down_payment"],
            mortgage_interest_rate=interest_rate,
            years_in_house=combination["years_in_house"],
            your_rent=your_rent,
            stock_instead_of_house=combination["stock_instead_of_house"],
            sell_house_year=combination["sell_year"],
            annual_extra_payment=combination["annual_extra_payment"],
            extra_payment_years=combination["extra_payment_years"],
            married=filing_status,
            income=income,
        )

        net_worth_buy = df[calculator.NET_WORTH_BUY].iloc[-1]
        stock_balance_rent = df[calculator.STOCK_BALANCE_RENT].iloc[-1]

        max_nw = max(net_worth_buy, stock_balance_rent)

        scenario_results.append({
            "max_nw": max_nw,
            "net_worth_buy": net_worth_buy,
            "stock_balance_rent": stock_balance_rent,
            **combination
        })

    scenario_results.sort(key=lambda x: x["max_nw"], reverse=True)

    top_10 = scenario_results[:10]

    results_df = pd.DataFrame(scenario_results)

    excel_path = os.path.join(os.getcwd(), "combinations.xlsx")

    best_down_payment = results_df.groupby("down_payment")["max_nw"].mean().reset_index()

    best_sell_year = results_df.groupby("sell_year")["max_nw"].mean().reset_index()

    best_extra_payment = results_df.groupby("annual_extra_payment")["max_nw"].mean().reset_index()


    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:

        # Save summary results
        results_df.to_excel(writer, sheet_name="All combinations", index=False)

        # Summary pages
        best_down_payment.to_excel(writer, sheet_name="Best Down Payment", index=False)
        best_sell_year.to_excel(writer, sheet_name="Best Sell Year", index=False)
        best_extra_payment.to_excel(writer, sheet_name="Best Extra Payment", index=False)

        # Rerun top 10 scenarios and save full dataframes
        for i, scenario in enumerate(top_10, start=1):

            df = calculator.calculator(
                house_price=home_value,
                down_payment=scenario["down_payment"],
                mortgage_interest_rate=interest_rate,
                years_in_house=scenario["years_in_house"],
                your_rent=your_rent,
                stock_instead_of_house=scenario["stock_instead_of_house"],
                sell_house_year=scenario["sell_year"],
                annual_extra_payment=scenario["annual_extra_payment"],
                extra_payment_years=scenario["extra_payment_years"],
                married=filing_status,
                income=income,
            )

            params_df = pd.DataFrame([scenario])
            params_df.to_excel(writer, sheet_name=f"Top {i}", index=False, startrow=0)

            df.to_excel(writer, sheet_name=f"Top {i}", index=False, startrow=5, float_format="%.2f")


def main():

    return combinations(home_value=350000,
                        interest_rate=6.25,
                        your_rent=1800,
                        filing_status="single",
                        income=125000)

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit