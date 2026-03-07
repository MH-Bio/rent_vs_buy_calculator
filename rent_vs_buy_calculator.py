"""
This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/

DISCLAIMER:
This software is provided "as is", without warranty of any kind, express or implied.
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

Goal: to find the cost / benefit of a house vs investing

Date: March 7, 2026
Author: Michael C. Hernandez
email: michaelhern@hotmail.com
"""
import os
import sys
import pandas as pd
import argparse
import tax_calculator
from tabulate import tabulate

# Colors
NO_COLOR = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"

# Amoritization stuff
MONTH = "Month"
MONTHLY_PAYMENT = "Monthly Payment"
INTEREST = "Interest"
PRINCIPAL = "Principal"
BALANCE = "Balance"
EQUITY = "Equity"
CASHFLOW = "Cashflow"
STOCK_BALANCE_BUY = "Stock Balance (Buy)"
NET_WORTH_BUY = "Net Worth (Buy)"
STOCK_BALANCE_RENT = "Stock Balance (Rent)"
YOUR_RENT = "Your Rent Payment"

# Cashflow Strings
CASHFLOW_NEGATIVE = "NEGATIVE (---)"
CASHFLOW_NEUTRAL = "NEUTRAL (~0~)"
CASHFLOW_POSITIVE = "POSITIVE (+++)"

pd.set_option('display.float_format', '{:.2f}'.format)

def calculate_monthly_payment(principal, annual_rate, months):
    monthly_rate = annual_rate / 12 / 100
    return principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)

def generate_amortization_schedule(principal, annual_rate, months):
    monthly_payment = calculate_monthly_payment(principal, annual_rate, months)
    balance = principal
    schedule = []

    for month in range(1, months + 1):
        interest = balance * (annual_rate / 12 / 100)
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        schedule.append([month, round(monthly_payment, 2), round(interest, 2), round(principal_payment, 2), round(balance, 2)])
        
    return schedule

def calculator(
        house_price: float = 332900,
        down_payment: float = 0,
        mortgage_interest_rate: float = 6.25,
        taxes: float = 85,
        insurance: float = 39,
        hoa: float = 249,
        hoa_increase: float =3,
        pmi: float = 208,
        rental_management_fee: float = 10.0,
        vacancy_rate: float = 5.0,
        upkeep_cost: float = 1.0,
        years_in_house: float = 1.0,
        house_rent: float = 2000,
        rent_increase: float = 5,
        your_rent: float =700,
        stock_instead_of_house: bool = False,
        sell_house_year: float = -1.0,
        state_capital_gains: float = 9.9,
        annual_extra_payment: float = 0,
        extra_payment_years: float =0.0,
        stock_interest: float = 7,
        annual_house_appreciation: float = 1,
        inflation: float = 3.0,
        married: bool = False,
        income: float = 100000,):
    HOUSE_SOLD = False
    
    # Convert human friendly numbers to actual percentage numbers
    mortgage_interest_rate /= 100
    stock_interest /= 100
    rent_increase/= 100
    hoa_increase /= 100
    inflation /= 100
    rental_management_fee /= 100
    vacancy_rate /= 100
    upkeep_cost /= 100
    state_capital_gains /= 100

    filing_status="single"
    if married:
        filing_status="married"

    annual_house_appreciation = inflation + (annual_house_appreciation / 100)

    # Convert years to months
    total_num_payments: int = 30 * 12
    months_in_house: float = round(years_in_house * 12, 12)
    extra_payment_months: float = round(extra_payment_years * 12, 12)
    sell_house_month: int = int(round(sell_house_year * 12, 12))  # convert the year you will sell the house to months
    
    # Using the default arguements, we are not selling the house
    sell_house_in_this_scenario: bool = True
    if sell_house_year < 0.0:
        sell_house_in_this_scenario: bool = False

    principal = house_price - down_payment

    # equity = home value - outstanding_balance
    home_value: float = house_price
    underwater: bool = False
    building_value = home_value * .8   # The value of the building sans the land it sits on top of

    # Create initial amoritization schedule
    headers: list[str] = [MONTH, MONTHLY_PAYMENT, INTEREST, PRINCIPAL, BALANCE]
    schedule = generate_amortization_schedule(principal=principal, annual_rate=(mortgage_interest_rate * 100), months=total_num_payments)
    df_schedule = pd.DataFrame(data=schedule, columns=headers)
    df_schedule[BALANCE] *= -1

    # Initialize your lists
    equity_col: list[float] = []
    net_worth_buy_scenario_col: list[float] = []
    cashflow_column: list[float] = []
    purchase_house_scenario_stock_market_balance: list[float] = [0]
    your_rent_payment: list[float] = []  # More just FYI rather than useful
    renting_scenario_stock_market_balance: list[float] = [down_payment]
    net_worth_buy_offset_col: list[float] = []

    # Adjust for inflation
    # Adjust the mortgage payment to include extra fees (PMI, HOA, etc.)
    # If you are renting figure out how much rental income you have coming in
    # Figure out what money is going where 
    ## Rental payments are paid into mortgage first
    ## Then you decide if they are going into the loan balance or the stock market
    # Figure out how much equity you have in the house
    # Figure out how much money you have in the stock market

    for month in range(df_schedule.shape[0]):
        # Annual inflation adjustment, these things only go up once per year
        if month % 12 == 0 and month != 0:
            hoa += (hoa * hoa_increase)
            taxes += (taxes * inflation)
            insurance += (insurance * inflation)
            house_rent += (house_rent * rent_increase)
            your_rent += (your_rent * rent_increase)
            building_value += (building_value * .8)
            income += (income * inflation)  # annual pay raise
        
        # Monthly adjustment, these things are always in flux, so we will approximate it by using a predictable average every month
        if month != 0:
            home_value += (home_value * (annual_house_appreciation / 12))
            home_buy_scenario_monthly_stock_interest = purchase_house_scenario_stock_market_balance[-1] * ((stock_interest + inflation) / 12)
            new_purchase_house_scenario_stock_market_balance = purchase_house_scenario_stock_market_balance[-1] + home_buy_scenario_monthly_stock_interest
            purchase_house_scenario_stock_market_balance.append(new_purchase_house_scenario_stock_market_balance)

            renting_scenario_monthly_stock_interest = renting_scenario_stock_market_balance[-1] * ((stock_interest + inflation) / 12)
            new_renting_scenario_stock_market_balance = renting_scenario_stock_market_balance[-1] + renting_scenario_monthly_stock_interest
            renting_scenario_stock_market_balance.append(new_renting_scenario_stock_market_balance)

        # Add in PMI if our equity is < 20%
        if abs(df_schedule.loc[month, BALANCE]) > (house_price * .8):
            if HOUSE_SOLD == False:
                df_schedule.loc[month, MONTHLY_PAYMENT] += pmi

        # Add in extra fees to your mortgage payment
        if HOUSE_SOLD == False:
            df_schedule.loc[month, MONTHLY_PAYMENT] += (hoa + taxes + insurance)

        # If you are making extra payments, figure out how much is going to be paid
        extra_payment = 0
        if month < extra_payment_months:
            extra_payment = annual_extra_payment / 12

         # Next we need to deduct our extra payment from the loan balance
        balance_after_extra_payment = df_schedule.loc[month, BALANCE] + extra_payment
        if balance_after_extra_payment > 0:
            df_schedule.loc[month, BALANCE] = 0
            if len(purchase_house_scenario_stock_market_balance) == 1:  # first month
                purchase_house_scenario_stock_market_balance[-1] = abs(balance_after_extra_payment)
            else:  # all other months
                purchase_house_scenario_stock_market_balance[-1] += purchase_house_scenario_stock_market_balance[-2] + balance_after_extra_payment

        rental_income = 0
        your_rent_payment.append(0)
        # Rent or sell
        if HOUSE_SOLD == False:
            if month >= months_in_house:
                your_rent_payment[-1] = your_rent  # Gotta pay to live somewhere

                # Sell the house
                if sell_house_in_this_scenario == True and sell_house_month == month:
                    profit_after_closing = home_value + df_schedule.loc[month, BALANCE]  # equity = home value - loan balance
                    profit_after_closing -= (home_value * .09)  # closing costs

                    old_monthly_payment_list = df_schedule[MONTHLY_PAYMENT][:month].tolist()
                    old_interest_list = df_schedule[INTEREST][:month].tolist()
                    old_principal_list = df_schedule[PRINCIPAL][:month].tolist()
                    old_balance_list = df_schedule[BALANCE][:month].tolist()
                    # Case 1: our profit_after_closing is positive or 0, add the profit_after_closing to the stock market
                    if profit_after_closing >= 0:
                        new_monthly_payment_list = [0] * (360 - len(old_monthly_payment_list))
                        new_interest_list = [0] * (360 - len(old_interest_list))
                        new_principal_list = [0] * (360 - len(old_principal_list))
                        new_balance_list = [0] * (360 - len(old_balance_list))

                        taxes_on_sale = tax_calculator.tax_on_home_sale(income=income, gross_sale_profit=profit_on_house,current_month=month, months_in_house=months_in_house, filing_status=filing_status)
                        profit_on_house = profit_after_closing * (1 - taxes_on_sale)
                        purchase_house_scenario_stock_market_balance[-1] += purchase_house_scenario_stock_market_balance[-2] + profit_on_house

                    # Case 2: we are underwater on the house, in this case our payments continue until we hit a 0 balance
                    else:
                        df_schedule.loc[month, BALANCE] -= profit_after_closing  # += because we are adding in an already negative number
                        
                        # Next we need to recalculate the remaining amoritization schedule
                        underwater_sched_list: list = generate_amortization_schedule(principal=abs(df_schedule.loc[month, BALANCE]), annual_rate=(mortgage_interest_rate * 100), months=total_num_payments - month)
                        underwater_schedule = pd.DataFrame(data=underwater_sched_list, columns=headers)
                        underwater_schedule[BALANCE] *= -1

                        new_monthly_payment_list = underwater_schedule[MONTHLY_PAYMENT].tolist()
                        new_interest_list = underwater_schedule[INTEREST].tolist()
                        new_principal_list = underwater_schedule[PRINCIPAL].tolist()
                        new_balance_list = underwater_schedule[BALANCE].tolist()

                    df_schedule[MONTHLY_PAYMENT] = old_monthly_payment_list + new_monthly_payment_list
                    df_schedule[INTEREST] = old_interest_list + new_interest_list
                    df_schedule[PRINCIPAL] = old_principal_list + new_principal_list
                    df_schedule[BALANCE] = old_balance_list + new_balance_list

                    HOUSE_SOLD = True
                    rental_income = 0

                # Already sold the house
                elif sell_house_in_this_scenario == True and month > sell_house_month:
                    rental_income = 0
                
                # Renting the house
                else:
                    preliminary_rental_income = house_rent * (1 - rental_management_fee)
                    
                    # Account for operating costs
                    vacency_rate_offset = preliminary_rental_income * (1- vacancy_rate)  # Apply the average vacancy rate every month
                    vacency_rate_adjustment = preliminary_rental_income - vacency_rate_offset

                    upkeep_offset = preliminary_rental_income * (1 - (upkeep_cost / 12))  # Apply the average annual upkeep rate every month
                    upkeep_adjustment = preliminary_rental_income - upkeep_offset

                    preliminary_rental_income -= your_rent  # subtract your rent from rental income because... you are also renting
                    rental_income = preliminary_rental_income - vacency_rate_adjustment - upkeep_adjustment
        
        if HOUSE_SOLD == True:
            your_rent_payment[-1] = your_rent  # Gotta pay to live somewhere

        # deduct the rental income from the mortgage payment
        adjusted_monthly_payment = df_schedule.loc[month, MONTHLY_PAYMENT] - rental_income

        # we can now figure out our cashflow
        # If the rent we bring in is greater than the monthly payment on the house, figure out where the money is going
        if adjusted_monthly_payment < 0:
            extra_income = abs(adjusted_monthly_payment)
            df_schedule.loc[month, MONTHLY_PAYMENT] = 0
            cashflow_column.append(CASHFLOW_POSITIVE)

            # If we have any extra rental income we need to figure out where that is going
            if stock_instead_of_house == False:  # If we decide to put the extra money into the loan balance
                balance_after_rental_income = df_schedule.loc[month, BALANCE] + extra_income
                if balance_after_rental_income > 0:
                    df_schedule.loc[month, BALANCE] = 0
                    
                    # first month
                    if len(purchase_house_scenario_stock_market_balance) == 1:
                        purchase_house_scenario_stock_market_balance[-1] = abs(balance_after_rental_income)
                    
                    # all other months
                    else:
                        purchase_house_scenario_stock_market_balance[-1] += purchase_house_scenario_stock_market_balance[-2] + abs(balance_after_rental_income)
            
            # If we DO want to invest in the stock market instead
            else:
                if len(purchase_house_scenario_stock_market_balance) == 1:  # first month
                    purchase_house_scenario_stock_market_balance[-1] = extra_income
                else:  # all other months
                    purchase_house_scenario_stock_market_balance[-1] += purchase_house_scenario_stock_market_balance[-2] + extra_income
        
        # If the rent we bring in is less than the monthly payment on the house, put the money in the house
        elif adjusted_monthly_payment > 0:
            cashflow_column.append(CASHFLOW_NEGATIVE)
            df_schedule.loc[month, MONTHLY_PAYMENT] -= rental_income
        
        # IF the rent we bring in is equal to the monthly house payment
        else:
            df_schedule.loc[month, MONTHLY_PAYMENT] = 0
            cashflow_column.append(CASHFLOW_NEUTRAL)
            df_schedule.loc[month, MONTHLY_PAYMENT] -= rental_income

        # Now that we have figure out where the money is going we can figure out our home profit_after_closing
        rent_price_diff = df_schedule.loc[month, MONTHLY_PAYMENT] - your_rent
        if HOUSE_SOLD == False:
            equity_col.append(home_value + df_schedule.loc[month, BALANCE])
            net_worth_buy_offset_col.append(equity_col[-1] + purchase_house_scenario_stock_market_balance[-1])
        elif HOUSE_SOLD == True and month == sell_house_month:
            equity_col.append(0)
            if rent_price_diff > 0:
                purchase_house_scenario_stock_market_balance[-1] += rent_price_diff
            net_worth_buy_offset_col.append(equity_col[-1] + purchase_house_scenario_stock_market_balance[-1] + profit_after_closing)
        else:
            equity_col.append(0)
            if rent_price_diff > 0:
                purchase_house_scenario_stock_market_balance[-1] += rent_price_diff
            net_worth_buy_offset_col.append(equity_col[-1] + purchase_house_scenario_stock_market_balance[-1] + profit_after_closing)

        # Next lets figure out the opportunity cost of renting vs buying
        # Assumptions:
        ## Savings from renting go directly into the stock market
        ## The down payment would have gone into the stock market instead on month 0
        ## We only invest in the stock market if the cost of renting is less than the cost of a mortgage payment
        
        # Figure out the price difference between renting and buying
        # At some point the cost of renting would possibly exceed a mortgage payment
        # we also need to consider the scenario where we live in a house for 5 years and then switch to renting

        rent_vs_buy_cost_difference = df_schedule.loc[month, MONTHLY_PAYMENT] - your_rent
        if rent_vs_buy_cost_difference > 0:
            renting_scenario_stock_market_balance[-1] += rent_vs_buy_cost_difference

    df_schedule[EQUITY] = equity_col
    df_schedule[CASHFLOW] = cashflow_column
    df_schedule[STOCK_BALANCE_BUY] = purchase_house_scenario_stock_market_balance
    df_schedule[NET_WORTH_BUY] = df_schedule[EQUITY] + df_schedule[STOCK_BALANCE_BUY] + net_worth_buy_offset_col
    df_schedule[YOUR_RENT] = your_rent_payment
    df_schedule[STOCK_BALANCE_RENT] = renting_scenario_stock_market_balance

    print(df_schedule.to_string())

    return df_schedule


def main():
    parser = argparse.ArgumentParser()

    # Purchase / Mortgage Basics
    parser.add_argument('-p', '--house_price', type=int, default=332900, help="The sell price of the home")
    parser.add_argument('--down_payment', type=int, default=0, help="Down payment on the house")
    parser.add_argument('--mortgage_interest_rate', type=float, default=6.250, help="Mortgage APR")

    # Ongoing Ownership Costs
    parser.add_argument('-t', '--taxes', type=int, default=85, help="Monthly property taxes as a dollar amount")
    parser.add_argument('-i', '--insurance', type=int, default=39, help="Monthly house insurance")
    parser.add_argument('--hoa', type=int, default=249, help="Monthly HOA fee")
    parser.add_argument('--hoa_increase', type=int, default=3, help="Percent increase that you expect the HOA to go up each year")
    parser.add_argument('--pmi', type=int, default=208, help="PMI")
    parser.add_argument('--rental_management_fee', type=float, default=10.0, help="rental management fees (e.g. for 10\% enter 10)")
    parser.add_argument('--vacancy_rate', type=float, default=5.0, help="vacancy rate: enter 5 for 5%")
    parser.add_argument('--upkeep_cost', type=float, default=5.0, help="upkeep costs: enter 1 for 1%")

    # Rental Scenario
    parser.add_argument('--years_in_house', type=float, default=1.0, help="Years in the house before you start renting")
    parser.add_argument('--house_rent', type=int, default=2000, help="Expected rent you extract from the house")
    parser.add_argument('--rent_increase', type=int, default=5, help="Expected annual percent rent increase")
    parser.add_argument('--your_rent', type=int, default=700, help="Your rent if you don’t purchase a house / live elsewhere")
    parser.add_argument('--stock_instead_of_house', action='store_true', help="Invest leftover money from rental into the stock market instead of the house")
    parser.add_argument('--sell_house_year', type=float, default=-1.0, help="Sell the house after X number of years")
    parser.add_argument('--state_capital_gains', type=float, default=9.9, help="Your state's capital gains tax, Oregon is 9.9\% for income above $125K")

    # Extra Payments
    parser.add_argument('--annual_extra_payment', type=int, default=0.0, help="Extra annual payment on the house")
    parser.add_argument('--extra_payment_years', type=float, default=0.0, help="Number of years to make the extra payment")

    # Investment & Economic Assumptions
    parser.add_argument('--stock_interest', type=int, default=7, help="Expected percent stock market appreciation")
    parser.add_argument('--annual_house_appreciation', type=int, default=1, help="Expected percent home value appreciation")
    parser.add_argument('--inflation', type=float, default=3.0, help="Annual inflation rate")

    # Your tax situation
    parser.add_argument('--married', type=bool, action="store_true", help="If you are married enter this arguement, otherwise we assume you are single")
    parser.add_argument('--income', type=float, default=100000, help="Your gross income")

    # Run the parser and places the extracted data in a argparse.Namespace object
    args = parser.parse_args()

    # Run the parser and places the extracted data in a argparse.Namespace object
    #for dp in range(0, 100001, 10000):
    df: pd.DataFrame = calculator(
        # Purchase / Mortgage Basics
        house_price=args.house_price,
        down_payment=args.down_payment,
        mortgage_interest_rate=args.mortgage_interest_rate,

        # Ongoing Ownership Costs
        taxes=args.taxes,
        insurance=args.insurance,
        hoa=args.hoa,
        hoa_increase=args.hoa_increase,
        pmi=args.pmi,
        rental_management_fee=args.rental_management_fee,
        vacancy_rate=args.vacancy_rate,
        upkeep_cost=args.upkeep_cost,

        # Rental Scenario
        years_in_house=args.years_in_house,
        house_rent=args.house_rent,
        rent_increase=args.rent_increase,
        your_rent=args.your_rent,
        stock_instead_of_house=args.stock_instead_of_house,
        sell_house_year=args.sell_house_year,

        # Extra Payments
        annual_extra_payment=args.annual_extra_payment,
        extra_payment_years=args.extra_payment_years,

        # Investment & Economic Assumptions
        stock_interest=args.stock_interest,
        annual_house_appreciation=args.annual_house_appreciation,
        inflation=args.inflation,

        # Your tax situation
        married=args.married
        income=args.income
    )

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit