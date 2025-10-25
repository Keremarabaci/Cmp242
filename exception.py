def withdraw(balances, amounts):
    if amounts > balances:
        raise ValueError("Insufficient Balance")
    else:
        balances -= amounts
        print("Withdraw successful, Remaining balance:", balances)
    return balances

try:
    amounts = float(input("Enter the amount to withdraw: "))
    withdraw(1000, amounts)
except ValueError as e:
    if "could not convert string to float" in str(e):
        print("Transaction Error: Please enter a valid amount")
    else:
        print("Transaction Error:", e)