# Disclaimer

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

------------------------------------------------------------------------

# License

This software is licensed under the MIT License.

Copyright (c) 2026 Michael Hernandez

https://opensource.org/license/MIT

------------------------------------------------------------------------

# Rent vs Buy Calculator

A Python tool for analyzing the long‑term financial impact of buying a
home vs renting and investing.

The program models mortgage amortization, rent increases, property
appreciation, taxes, and investment returns to estimate net worth over
time under different scenarios.

It can:

-   Simulate a single scenario
-   Run thousands of parameter combinations
-   Generate graphs and Excel reports
-   Compare rent vs buy investment outcomes

------------------------------------------------------------------------

# Features

-   30‑year mortgage amortization modeling
-   Tracks:
    -   Loan balance
    -   Interest vs principal
    -   Home equity
    -   Net worth
    -   Rental income
    -   Stock market investments
-   Accounts for:
    -   Property taxes
    -   HOA
    -   PMI
    -   Insurance
    -   Inflation
    -   Rent increases
    -   House appreciation
    -   Vacancy rates
    -   Maintenance costs
-   Simulates selling the home and applies:
    -   Capital gains taxes
    -   Depreciation recapture
    -   Net investment income tax
-   Compares outcomes against renting and investing the difference

Outputs include:

-   Monthly simulation results
-   Excel reports
-   Scenario comparison graphs
-   Ranked scenario tables

------------------------------------------------------------------------

# Project Structure

rent_vs_buy_calculator/

    rent_vs_buy_calculator.py   # Core financial simulation engine
    combinations.py             # Runs thousands of parameter combinations
    simulations.py              # Generates scenario graphs
    tax_calculator.py           # Federal + Oregon tax logic
    README.md

------------------------------------------------------------------------

# Requirements

Python 3.9+

Install dependencies:

pip install pandas numpy matplotlib xlsxwriter

------------------------------------------------------------------------

# Quick Start

Run a basic rent vs buy calculation:

python rent_vs_buy_calculator.py

Example with parameters:

python rent_vs_buy_calculator.py\
--house_price 350000\
--down_payment 50000\
--mortgage_interest_rate 6.25\
--years_in_house 10\
--sell_house_year 15\
--your_rent 1800

------------------------------------------------------------------------

# Core Simulation Script

## rent_vs_buy_calculator.py

This script performs the main financial simulation.

It generates a monthly amortization schedule and calculates:

-   mortgage payments
-   rental income
-   investment balances
-   equity
-   net worth

### Output Columns

  Column                 Description
  ---------------------- ----------------------------------
  Month                  Month of simulation
  Monthly Payment        Mortgage payment including fees
  Interest               Interest portion of payment
  Principal              Principal portion
  Balance                Remaining loan balance
  Equity                 Home value minus loan balance
  Cashflow               Rental cashflow status
  Stock Balance (Buy)    Investments while owning
  Net Worth (Buy)        Equity + investments
  Your Rent Payment      Rent paid if not living in house
  Stock Balance (Rent)   Investments if renting

------------------------------------------------------------------------

# Scenario Simulations

## simulations.py

Creates visual comparisons between parameters.

Running:

python simulations.py

Generates:

Down Payment/ net_worth_down_payment_comparison.png
down_payment_scenarios.xlsx

Sell Year/ net_worth_sell_year_comparison.png sell_year_scenarios.xlsx

------------------------------------------------------------------------

# Combination Analysis

## combinations.py

Runs thousands of parameter combinations and ranks them by final net
worth.

Parameters explored include:

-   down payment
-   years in house
-   sale year
-   extra mortgage payments
-   investing excess cash vs paying down mortgage

Run:

python combinations.py

Output:

combinations.xlsx

Contains:

-   All combinations ranked by best net worth
-   Average results by down payment
-   Average results by sell year
-   Average results by extra payments
-   Detailed data for the top scenarios

------------------------------------------------------------------------

# Tax Modeling

## tax_calculator.py

Implements simplified tax logic including:

Federal tax brackets (2026) Oregon state income tax Capital gains on
home sales Depreciation recapture Net investment income tax

Functions include:

federal_effective_tax_rate() federal_marginal_rate()
oregon_effective_tax_rate() oregon_marginal_tax_rate()
tax_on_home_sale() depreciation_recapture() net_investment_income_tax()

------------------------------------------------------------------------

# Assumptions

This model uses simplified financial assumptions including:

-   constant mortgage rate
-   constant investment returns
-   predictable rent growth
-   fixed inflation rate
-   simplified tax modeling

Actual financial outcomes will vary.

------------------------------------------------------------------------

# Author

Michael C. Hernandez\
michaelhern@hotmail.com
