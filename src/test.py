import requests

rolls = [
    '3d6',
    '4d6k3',
]

results = {}

for query in rolls:
    results[query] = []
    for _ in range(10):
        url = ('https://3jsvls9ekl.execute-api.ca-central-1.amazonaws.com'
               '/dev/rolldice')
        r = requests.get(url, params={'q': query})
        results[query].append(r.json()['result'])

print(results)

for query, rolls in results.items():
    average = sum(rolls) / len(rolls)
    print('average for {} rolls of {} is: {}'.format(len(rolls),
                                                     query,
                                                     average))
