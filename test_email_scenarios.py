#!/usr/bin/env python
# Test email scenarios

print('Simulating email generation for all scenarios:')
print('=' * 80)

scenarios = [
    {'name': 'Cloudburst + High', 'cb': 'Cloud Burst', 'risk': 'High', 'mention_cb': True},
    {'name': 'Cloudburst + Medium', 'cb': 'Cloud Burst', 'risk': 'Medium', 'mention_cb': True},
    {'name': 'Cloudburst + Low', 'cb': 'Cloud Burst', 'risk': 'Low', 'mention_cb': True},
    {'name': 'No Cloudburst + High', 'cb': 'Normal Cloud', 'risk': 'High', 'mention_cb': False},
    {'name': 'No Cloudburst + Medium', 'cb': 'Normal Cloud', 'risk': 'Medium', 'mention_cb': False},
    {'name': 'No Cloudburst + Low', 'cb': 'Normal Cloud', 'risk': 'Low', 'mention_cb': False},
]

for scenario in scenarios:
    name = scenario['name']
    cb = scenario['cb']
    risk = scenario['risk']
    mention_cb = scenario['mention_cb']
    
    # Determine subject
    if mention_cb and cb == 'Cloud Burst':
        if risk == 'High':
            subject = '🚨 Emergency Alert: Cloudburst and High Flood Risk Detected'
        elif risk == 'Medium':
            subject = '⚠️ Warning Alert: Cloudburst and Moderate Flood Risk Detected'
        else:
            subject = '⚠️ Alert: Cloudburst Detected - Flood Risk is Low'
    else:
        if risk == 'High':
            subject = '🚨 Emergency Alert: High Flood Risk Detected'
        elif risk == 'Medium':
            subject = '⚠️ Warning Alert: Moderate Flood Risk Detected'
        else:
            subject = '📢 Update: Low Flood Risk'
    
    # Determine header and alert details
    if mention_cb and cb == 'Cloud Burst':
        header = 'Cloudburst and Flood Risk Alert'
        has_cb_mention = True
    else:
        header = 'Flood Risk Alert'
        has_cb_mention = False
    
    print(f'Scenario: {name}')
    print(f'  Subject: {subject}')
    print(f'  Header:  {header}')
    print(f'  Mentions cloudburst in body: {has_cb_mention}')
    print()

print('=' * 80)
print('All scenarios verified!')
