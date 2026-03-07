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

Figures out tax rates based on income

Date: March 7, 2026
Author: Michael C. Hernandez
email: michaelhern@hotmail.com
"""

def federal_tax_rate(income: float, filing_status: str="single"):
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
            (640600, float("inf"), 0.37),
        ],
        "married": [
            (0, 24800, 0.10),
            (24800, 100800, 0.12),
            (100800, 211400, 0.22),
            (211400, 403550, 0.24),
            (403550, 512450, 0.32),
            (512450, 768700, 0.35),
            (768700, float("inf"), 0.37),
        ]
    }

    tax = 0
    for lower, upper, rate in brackets[filing_status]:
        taxable = max(0, min(income, upper) - lower)
        tax += taxable * rate

    return tax / income if income > 0 else 0


def oregon_tax_rate(income: float, filing_status: str="single"):
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
            (4550, 11399, 0.675),
            (11400, 124999, 0.0875),
            (125000, float("inf"), 0.099),
        ],
        "married": [
            (0, 9099, 0.0475),
            (9100, 22799, 0.675),
            (22800, 249999, 0.0875),
            (250000, float("inf"), 0.099),
        ]
    }

    tax = 0
    for lower, upper, rate in brackets[filing_status]:
        taxable = max(0, min(income, upper) - lower)
        tax += taxable * rate

    return tax / income if income > 0 else 0


def tax_on_home_sale(income: float, gross_sale_profit: float, current_month: float, months_in_house: float, filing_status: str="single"):
    if filing_status == "single":
        exempt_amount: int = 250000
    else:
        exempt_amount: int = 500000

    taxes_on_sale: float = -1.0

    # If we have lived in the house for less than one year, just pay ordinary income tax
    if current_month < 12:
        taxes_on_sale = federal_tax_rate(income=income + gross_sale_profit, filing_status=filing_status) + oregon_tax_rate(income=income + gross_sale_profit, filing_status=filing_status)
    elif 12 < current_month < 24:
        taxes_on_sale = .15 + oregon_tax_rate(income=income + gross_sale_profit, filing_status=filing_status)
    else:
        # If you have lived in the home for 2 years out of the past five years, you can exempt a certain amount of profit from capital gains tax
        if (current_month) - (months_in_house) <= 60:
            taxes_on_sale = gross_sale_profit - exempt_amount
            if taxes_on_sale < 0:
                taxes_on_sale = 0
            else:
                taxes_on_sale = .15 + oregon_tax_rate(income=income + gross_sale_profit - exempt_amount, filing_status=filing_status)
        else:
            taxes_on_sale = .15 + oregon_tax_rate(income=income + gross_sale_profit, filing_status=filing_status)

    return taxes_on_sale