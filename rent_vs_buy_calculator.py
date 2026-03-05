"""
This work is licensed under the Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/

Goal: to find the cost / benefit of a house vs investing

Date: August 3, 2025
Author: Michael C. Hernandez
email: michaelhern@hotmail.com
"""
import sys
import pandas as pd
import argparse
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
STOCK_BALANCE_RENT = "Stock Balance (Rent)"
YOUR_RENT = "Your Rent Payment"

# Cashflow Strings
CASHFLOW_NEGATIVE = f"{RED}NEGATIVE (---){NO_COLOR}"
CASHFLOW_NEUTRAL = f"{YELLOW}NEUTRAL (~0~){NO_COLOR}"
CASHFLOW_POSITIVE = f"{GREEN}POSITIVE (+++){NO_COLOR}"


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
        house_price=332900,
        down_payment=0,
        mortgage_interest_rate=6.25,
        taxes=85,
        insurance=39,
        hoa=249,
        hoa_increase=3,
        pmi=208,
        rental_management_fee=.1,
        years_in_house=1.0,
        house_rent=2000,
        rent_increase=5,
        your_rent=700,
        stock_instead_of_house=False,
        annual_extra_payment=0,
        extra_payment_years=0.0,
        stock_interest=7,
        annual_house_appreciation=1,
        inflation=3.0):
    
    # Find out when you quit paying PMI
    mortgage_interest_rate /= 100
    
    stock_interest /= 100
    rent_increase/= 100
    hoa_increase /= 100
    inflation /= 100

    annual_house_appreciation = inflation + (annual_house_appreciation / 100)

    total_num_payments = 30 * 12
    principal = house_price - down_payment

    months_in_house = round(years_in_house * 12, 12)
    extra_payment_months = round(extra_payment_years * 12, 12)

    # Create initial amoritization schedule
    headers = [MONTH, MONTHLY_PAYMENT, INTEREST, PRINCIPAL, BALANCE]
    schedule = generate_amortization_schedule(principal=principal, annual_rate=(mortgage_interest_rate * 100), months=total_num_payments)
    df_schedule = pd.DataFrame(data=schedule, columns=headers)
        
    
    # equity = home value - outstanding_balance
    home_value = house_price

    # Now that we have an amoritization schedule, we need to adjust the monthly payment to account for HOA, taxes, etc.
    equity_col = []
    cashflow_column = []
    purchase_house_scenario_stock_market_balance = [0]
    your_rent_payment = []  # More just FYI rather than useful
    renting_scenario_stock_market_balance = [down_payment]

    # adjust for inflation
    # Adjust the mortgage payment to include extra fees (PMI, HOA, etc.)
    # If you are renting figure out how much rental income you have coming in
    # Figure out what money is going where 
    ## Rental payments are paid into mortgage first
    ## Then you decide if they are going into the loan balance or the stock market
    # figure out how much equity you have in the house
    # Figure out how much money you have in the stock market

    renting_more_expensive_flag = False
    renting_more_expensive_month = 0

    for month in range(df_schedule.shape[0]):
        # Annual inflation adjustment, these things only go up once per year
        if month % 12 == 0 and month != 0:
            hoa += (hoa * hoa_increase)
            taxes += (taxes * inflation)
            insurance += (insurance * inflation)
            house_rent += (house_rent * rent_increase)
            your_rent += (your_rent * rent_increase)
        
        # Monthly adjustment, these things are always in flux, so we will approximate it by using a predictable average every month
        if month != 0:
            home_value += (home_value * (annual_house_appreciation / 12))
            purchase_house_scenario_stock_market_balance.append(purchase_house_scenario_stock_market_balance[-1] * ((stock_interest + inflation) / 12))  # add interest
            renting_scenario_stock_market_balance.append((renting_scenario_stock_market_balance[-1] * ((stock_interest + inflation) / 12)) + renting_scenario_stock_market_balance[-1])  # add interest

        # Add in PMI if our equity is < 20%
        if df_schedule.loc[month, BALANCE] > (house_price * .8):
            df_schedule.loc[month, MONTHLY_PAYMENT] += pmi

        # Add in extra fees to your mortgage payment
        df_schedule.loc[month, MONTHLY_PAYMENT] += (hoa + taxes + insurance)

        # If you are making extra payments, figure out how much is going to be paid
        extra_payment = 0
        if month < extra_payment_months:
            extra_payment = annual_extra_payment / 12

         # Next we need to deduct our extra payment from the loan balance
        balance_after_extra_payment = df_schedule.loc[month, BALANCE] - extra_payment
        if balance_after_extra_payment < 0:
            df_schedule.loc[month, BALANCE] = 0
            if len(purchase_house_scenario_stock_market_balance) == 1:  # first month
                purchase_house_scenario_stock_market_balance[-1] = abs(balance_after_extra_payment)
            else:  # all other months
                purchase_house_scenario_stock_market_balance[-1] += purchase_house_scenario_stock_market_balance[-2] + abs(balance_after_extra_payment)

        # If you are renting out the house, figure out rental income
        rental_income = 0
        if month > months_in_house:
            your_rent_payment.append(your_rent)
            rental_income = house_rent * (1 - rental_management_fee) - your_rent # subtract your rent from rental income because... you are also renting
        else:
            your_rent_payment.append(0)
        
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
                balance_after_rental_income = df_schedule.loc[month, BALANCE] - extra_income
                if balance_after_rental_income < 0:
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

        # Now that we have figure out where the money is going we can figure out our home equity
        equity_col.append(home_value - df_schedule.loc[month, BALANCE])

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
    df_schedule["Net Worth (Buy)"] = df_schedule[EQUITY] + df_schedule[STOCK_BALANCE_BUY]
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
    parser.add_argument('--rental_management_fee', type=float, default=.1, help="rental management fees as a percent (e.g. for 10\% enter .1)")

    # Rental Scenario
    parser.add_argument('--years_in_house', type=float, default=1.0, help="Years in the house before you start renting")
    parser.add_argument('--house_rent', type=int, default=2000, help="Expected rent you extract from the house")
    parser.add_argument('--rent_increase', type=int, default=5, help="Expected annual percent rent increase")
    parser.add_argument('--your_rent', type=int, default=700, help="Your rent if you don’t purchase a house / live elsewhere")
    parser.add_argument('--stock_instead_of_house', action='store_true', help="Invest leftover money from rental into the stock market instead of the house")

    # Extra Payments
    parser.add_argument('--annual_extra_payment', type=int, default=0.0, help="Extra annual payment on the house")
    parser.add_argument('--extra_payment_years', type=float, default=0.0, help="Number of years to make the extra payment")

    # Investment & Economic Assumptions
    parser.add_argument('--stock_interest', type=int, default=7, help="Expected percent stock market appreciation")
    parser.add_argument('--annual_house_appreciation', type=int, default=1, help="Expected percent home value appreciation")
    parser.add_argument('--inflation', type=float, default=3.0, help="Annual inflation rate")


    # Run the parser and places the extracted data in a argparse.Namespace object
    args = parser.parse_args()
    with pd.ExcelWriter("Variable_Down_Payment.xlsx", engine="xlsxwriter") as writer:
        for dp in range(0, 100001, 10000):
            df: pd.DataFrame = calculator(
                # Purchase / Mortgage Basics
                house_price=args.house_price,
                down_payment=dp,
                mortgage_interest_rate=args.mortgage_interest_rate,

                # Ongoing Ownership Costs
                taxes=args.taxes,
                insurance=args.insurance,
                hoa=args.hoa,
                hoa_increase=args.hoa_increase,
                pmi=args.pmi,
                rental_management_fee=args.rental_management_fee,

                # Rental Scenario
                years_in_house=args.years_in_house,
                house_rent=args.house_rent,
                rent_increase=args.rent_increase,
                your_rent=args.your_rent,
                stock_instead_of_house=args.stock_instead_of_house,

                # Extra Payments
                annual_extra_payment=args.annual_extra_payment,
                extra_payment_years=args.extra_payment_years,

                # Investment & Economic Assumptions
                stock_interest=args.stock_interest,
                annual_house_appreciation=args.annual_house_appreciation,
                inflation=args.inflation,
            )

            month_col = df.columns.get_loc("Month")
            monthly_payment_col = df.columns.get_loc("Monthly Payment")
            interest_col = df.columns.get_loc("Interest")
            principal_col = df.columns.get_loc("Principal")
            loan_balance_col = df.columns.get_loc("Balance")
            equity_col = df.columns.get_loc("Equity")
            cashflow_col = df.columns.get_loc("Cashflow")
            buy_stock_balance = df.columns.get_loc("Stock Balance (Buy)")
            your_rent_payment_col = df.columns.get_loc("Your Rent Payment")
            rent_stock_balance = df.columns.get_loc("Stock Balance (Rent)")
            net_worth_buy_column = df.columns.get_loc("Net Worth (Buy)")
            
            df.to_excel(
                excel_writer=writer,
                sheet_name=f"Scenario: {dp}",
                float_format="%.2f",
                columns=[month_col, monthly_payment_col, interest_col, principal_col, loan_balance_col, equity_col, buy_stock_balance, net_worth_buy_column, your_rent_payment_col, rent_stock_balance],
                index=False,
            )

if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit