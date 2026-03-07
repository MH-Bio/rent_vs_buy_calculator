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

Figures out tax rates based on income

Date: March 7, 2026
Author: Michael C. Hernandez
email: michaelhern@hotmail.com
"""

def federal_effective_tax_rate(income: float, filing_status: str="single") -> float:
    """
    Figure out the federal tax rate
    https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill
    
    Federal Income Tax Brackets

    Rate | Single Income Range        | Married Filing Jointly Range
    -----|----------------------------|------------------------------
    10%  | $0 – $12,400               | $0 – $24,800
    12%  | $12,401 – $50,400          | $24,801 – $100,800
    22%  | $50,401 – $105,700         | $100,801 – $211,400
    24%  | $105,701 – $201,775        | $211,401 – $403,550
    32%  | $201,776 – $256,225        | $403,551 – $512,450
    35%  | $256,226 – $640,600        | $512,451 – $768,700
    37%  | $640,601+                  | $768,701+
    """
    brackets = {
        "single": [
            (0, 12400, 0.10),
            (12400, 50400, 0.12),
            (50400, 105700, 0.22),
            (105700, 201775, 0.24),
            (201775, 256225, 0.32),
            (256225, 640600, 0.35),
            (640601, float("inf"), 0.37),
        ],
        "married": [
            (0, 24800, 0.10),
            (24800, 100800, 0.12),
            (100800, 211400, 0.22),
            (211400, 403550, 0.24),
            (403550, 512450, 0.32),
            (512450, 768700, 0.35),
            (768701, float("inf"), 0.37),
        ]
    }

    tax = 0
    for lower, upper, rate in brackets[filing_status]:
        taxable = max(0, min(income, upper) - lower)
        tax += taxable * rate

    return tax / income if income > 0 else 0


def federal_marginal_rate(income: float, filing_status: str="single") -> float:
    """
    Returns the marginal tax rate
    https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill
    
    Federal Income Tax Brackets

    Rate | Single Income Range        | Married Filing Jointly Range
    -----|----------------------------|------------------------------
    10%  | $0 – $12,400               | $0 – $24,800
    12%  | $12,401 – $50,400          | $24,801 – $100,800
    22%  | $50,401 – $105,700         | $100,801 – $211,400
    24%  | $105,701 – $201,775        | $211,401 – $403,550
    32%  | $201,776 – $256,225        | $403,551 – $512,450
    35%  | $256,226 – $640,600        | $512,451 – $768,700
    37%  | $640,601+                  | $768,701+
    """
    marginal_rate: float = -1.0

    if filing_status == "single":
        if income > 640601:
            marginal_rate = .37
        elif income > 256225:
            marginal_rate = .35
        elif income > 201775:
            marginal_rate = .32
        elif income > 105700:
            marginal_rate = .24
        elif income > 50400:
            marginal_rate = .22
        elif income > 12400:
            marginal_rate = .12
        else:
            marginal_rate = .1
    
    elif filing_status == "married":
        if income > 768701:
            marginal_rate = .37
        elif income > 512450:
            marginal_rate = .35
        elif income > 403550:
            marginal_rate = .32
        elif income > 211400:
            marginal_rate = .24
        elif income > 100800:
            marginal_rate = .22
        elif income > 24800:
            marginal_rate = .12
        else:
            marginal_rate = .1

    return marginal_rate


def oregon_effective_tax_rate(income: float, filing_status: str="single") -> float:
    """
    Figure out the Oregon tax rate
    https://taxfoundation.org/data/all/state/state-income-tax-rates-2026/

    Oregon Income Tax Brackets

    Rate   | Single Income Range        | Married Filing Jointly Range
    -------|----------------------------|------------------------------
    4.75%  | $0 – $4,549                | $0 – $9,099
    6.75%  | $4,550 – $11,399           | $9,100 – $22,799
    8.75%  | $11,400 – $124,999         | $22,800 – $249,999
    9.90%  | $125,000+                  | $250,000+
    """
    brackets = {
        "single": [
            (0, 4549, 0.0475),
            (4550, 11399, 0.0675),
            (11400, 124999, 0.0875),
            (125000, float("inf"), 0.099),
        ],
        "married": [
            (0, 9099, 0.0475),
            (9100, 22799, 0.0675),
            (22800, 249999, 0.0875),
            (250000, float("inf"), 0.099),
        ]
    }

    tax = 0
    for lower, upper, rate in brackets[filing_status]:
        taxable = max(0, min(income, upper) - lower)
        tax += taxable * rate

    return tax / income if income > 0 else 0


def oregon_marginal_tax_rate(income: float, filing_status: str="single") -> float:
    """
    Figure out the Oregon marginal rate
    https://taxfoundation.org/data/all/state/state-income-tax-rates-2026/

    Oregon Income Tax Brackets

    Rate   | Single Income Range        | Married Filing Jointly Range
    -------|----------------------------|------------------------------
    4.75%  | $0 – $4,549                | $0 – $9,099
    6.75%  | $4,550 – $11,399           | $9,100 – $22,799
    8.75%  | $11,400 – $124,999         | $22,800 – $249,999
    9.90%  | $125,000+                  | $250,000+
    """
    marginal_rate: float = -1.0

    if filing_status == "single":
        if income > 125000:
            marginal_rate = .099
        elif income > 11400:
            marginal_rate = .0875
        elif income > 4550:
            marginal_rate = .0675
        else:
            marginal_rate = .0475
    
    if filing_status == "married":
        if income > 250000:
            marginal_rate = .099
        elif income > 22800:
            marginal_rate = .0875
        elif income > 9100:
            marginal_rate = .0675
        else:
            marginal_rate = .0475

    return marginal_rate


def tax_on_home_sale(income: float, gross_sale_profit: float, current_month: float, months_in_house: float, filing_status: str="single"):
    if filing_status == "single":
        exempt_amount: int = 250000
    else:
        exempt_amount: int = 500000

    taxes_on_sale: float = -1.0
    
    # If we have lived in the house for less than one year, just pay ordinary income tax
    if current_month < 12:
        taxes_on_sale = federal_marginal_rate(income=income + gross_sale_profit, filing_status=filing_status) + oregon_marginal_tax_rate(income=income + gross_sale_profit, filing_status=filing_status)
    elif 12 < current_month < 24:
        taxes_on_sale = .15 + oregon_marginal_tax_rate(income=income + gross_sale_profit, filing_status=filing_status)
    else:
        # If you have lived in the home for 2 years out of the past five years, you can exempt a certain amount of profit from capital gains tax
        if (current_month) - (months_in_house) <= 60:
            taxable_profit = gross_sale_profit - exempt_amount
            if taxable_profit < 0:
                taxes_on_sale = 0
            else:
                taxes_on_sale = .15 + oregon_marginal_tax_rate(income=income + gross_sale_profit - exempt_amount, filing_status=filing_status)
        else:
            taxes_on_sale = .15 + oregon_marginal_tax_rate(income=income + gross_sale_profit, filing_status=filing_status)

    return taxes_on_sale


def depreciation_recapture(current_month: float, months_in_house: float, monthly_depreciation_value: float):
    """
    Calculate the dollar value that you have to pay on depreciation recapture
    https://www.investopedia.com/articles/investing/060815/how-rental-property-depreciation-works.asp
    """
    # Figure out depreciation recapture.  This is applied before applying your exempt amount
    months_renting = current_month - months_in_house
    depreciated_amount = months_renting * monthly_depreciation_value
    depreciation_recapture = depreciated_amount * .25

    return depreciation_recapture


def net_investment_income_tax(investment_income: float, filing_status: str="single"):
    """
    https://www.investopedia.com/terms/n/netinvestmentincome.asp
    """
    # Figure out what the limits are
    if filing_status == "single":
        limit = 200000
    elif filing_status == "married":
        limit = 250000

    nii_tax: float = 0.0
    if investment_income > limit:
        nii_tax = .038

    return nii_tax