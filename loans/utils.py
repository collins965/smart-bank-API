def check_loan_eligibility(user):
    profile = user.profile
    wallet = user.wallet

    if not profile.is_verified:
        return 0  # Not eligible at all

    # Simple scoring: based on balance and past transactions
    score = 0
    if wallet.balance >= 500:
        score += 30
    if user.transactions_sent.count() >= 3:
        score += 30
    if profile.national_id and profile.phone_number:
        score += 40

    return min(score, 100)
