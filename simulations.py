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

Creates graphs for different scenarios

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

STARTING_DIR = os.getcwd()


def down_payment_simulations(start: int = 0, stop: int = 60000, step: int = 10000):
    """
    Step through different down payment values and plot multiple net worth lines
    """
    new_dir = "Down Payment"
    new_path = os.path.join(STARTING_DIR, new_dir)
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    os.chdir(new_path)
    
    df_list: list[pd.DataFrame] = []
    down_payments: int = []
    
    # Collect data
    for down_payment in range(start, stop + 1, step):
        df = calculator.calculator(down_payment=down_payment)
        df_list.append(df)
        down_payments.append(down_payment)
    
    plt.figure(figsize=(10,6))
    
    # Plot all lines
    for df, dp in zip(df_list, down_payments):
        # Convert months to years
        years = df["Month"] / 12
        plt.plot(years, df[calculator.NET_WORTH_BUY], label=f"Down Payment ${dp:,}")
    
    # Labels and title
    plt.xlabel("Years")
    plt.ylabel("Net Worth ($)")
    plt.title("Net Worth Over Time for Different Down Payments")
    plt.grid(True)
    
    # Legend
    plt.legend()
    
    # X-axis step size of 5 years
    max_year = int(df_list[0]["Month"].iloc[-1] / 12)
    plt.xticks(np.arange(0, max_year + 1, 5))

    # Y-axis step size of 250,000
    max_y = max(df[calculator.NET_WORTH_BUY].max() for df in df_list)
    plt.yticks(np.arange(0, max_y + 250000, 250000))

    # Force plain numbers on y-axis (no scientific notation)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.ticklabel_format(style='plain', axis='y')
    
    # Save the figure
    plt.savefig(os.path.join(os.getcwd(), "net_worth_down_payment_comparison.png"), dpi=300)

    # Save all DataFrames to a single Excel file
    excel_path = os.path.join(new_path, "down_payment_scenarios.xlsx")
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        for df, dp in zip(df_list, down_payments):
            sheet_name = f"Down Payment {dp}"
            # Excel sheet names have a max length of 31 characters
            sheet_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    os.chdir(STARTING_DIR)


def sell_year_simulations(start: int = 5, stop: int = 30, step: int = 5):
    new_dir = "Sell Year"
    new_path = os.path.join(STARTING_DIR, new_dir)
    if not os.path.exists(new_path):
        os.makedirs(new_path)

    os.chdir(new_path)
    
    df_list: list[pd.DataFrame] = []
    years: int = []
    
    # Collect data
    for year in range(start, stop + 1, step):
        df = calculator.calculator(years_in_house=year,
                                   sell_house_year=year)
        df_list.append(df)
        years.append(year)
    
    plt.figure(figsize=(10,6))
    
    # Plot all lines
    for df, yr in zip(df_list, years):
        # Convert months to years
        years = df["Month"] / 12
        plt.plot(years, df[calculator.NET_WORTH_BUY], label=f"Sell Year {yr:,}")
    
    # Labels and title
    plt.xlabel("Years")
    plt.ylabel("Net Worth ($)")
    plt.title("Net Worth Over Time for Different Sell Years")
    plt.grid(True)
    
    # Legend
    plt.legend()
    
    # X-axis step size of 5 years
    max_year = int(df_list[0]["Month"].iloc[-1] / 12)
    plt.xticks(np.arange(0, max_year + 1, 5))

    # Y-axis step size of 250,000
    max_y = max(df[calculator.NET_WORTH_BUY].max() for df in df_list)
    plt.yticks(np.arange(0, max_y + 250000, 250000))

    # Force plain numbers on y-axis (no scientific notation)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.ticklabel_format(style='plain', axis='y')
    
    # Save the figure
    plt.savefig(os.path.join(os.getcwd(), "net_worth_sell_year_comparison.png"), dpi=300)

    # Save all DataFrames to a single Excel file
    year_label = step
    excel_path = os.path.join(new_path, "sell_year_scenarios.xlsx")
    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        for df, dp in zip(df_list, years):
            sheet_name = f"Sell Year {year_label}"
            # Excel sheet names have a max length of 31 characters
            sheet_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            year_label += step
    
    os.chdir(STARTING_DIR)


def main():
    down_payment_simulations()
    sell_year_simulations()

    return None

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit