#!/usr/bin/env python
"""
Test the email trigger logic matches requirements
"""

def should_send_email_and_mention_cloudburst(cloudburst_result, flood_risk):
    """
    Returns: (should_send_email, mention_cloudburst_in_email)
    """
    email_sent = False
    mention_cloudburst = False
    
    if cloudburst_result == "Cloud Burst":
        # Always send email if cloudburst is detected
        email_sent = True
        mention_cloudburst = True
    elif flood_risk in ["High", "Medium"]:
        # Send email for High/Medium without mentioning cloudburst
        email_sent = True
        mention_cloudburst = False
    # else: No email for Low risk without cloudburst
    
    return email_sent, mention_cloudburst


print("=" * 80)
print("TESTING EMAIL TRIGGER LOGIC")
print("=" * 80)

test_cases = [
    # (cloudburst, flood_risk, expected_send, expected_mention, description)
    ("Cloud Burst", "High", True, True, "Cloudburst + High: send with mention"),
    ("Cloud Burst", "Medium", True, True, "Cloudburst + Medium: send with mention"),
    ("Cloud Burst", "Low", True, True, "Cloudburst + Low: send with mention (NEW)"),
    ("Normal Cloud", "High", True, False, "No Cloudburst + High: send without mention (NEW)"),
    ("Normal Cloud", "Medium", True, False, "No Cloudburst + Medium: send without mention (NEW)"),
    ("Normal Cloud", "Low", False, False, "No Cloudburst + Low: no email"),
]

all_pass = True
for cloudburst, flood_risk, exp_send, exp_mention, desc in test_cases:
    send, mention = should_send_email_and_mention_cloudburst(cloudburst, flood_risk)
    
    send_ok = send == exp_send
    mention_ok = mention == exp_mention if send else True  # mention only matters if sending
    test_ok = send_ok and mention_ok
    
    status = "✅ PASS" if test_ok else "❌ FAIL"
    print(f"{status}: {desc}")
    print(f"       Cloudburst: {cloudburst:12} | Flood Risk: {flood_risk:6}")
    print(f"       Send: {send} (expected {exp_send}) | Mention CB: {mention} (expected {exp_mention})")
    
    if not test_ok:
        all_pass = False
        if not send_ok:
            print(f"       ERROR: Email send mismatch!")
        if not mention_ok:
            print(f"       ERROR: Mention cloudburst mismatch!")
    print()

print("=" * 80)
if all_pass:
    print("✅ ALL TESTS PASSED - Email logic is correct!")
else:
    print("❌ SOME TESTS FAILED - Check the implementation!")
print("=" * 80)
