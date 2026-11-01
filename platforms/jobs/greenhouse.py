import requests


def fetch_jobs(boards):
    output = []
    for company, slug in boards.items():
        try:
            r = requests.get(f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs', params={'content': 'true'}, timeout=25)
            r.raise_for_status()
            for j in r.json().get('jobs', []):
                output.append({
                    'id': str(j.get('id') or ''), 'title': j.get('title') or '',
                    'company': company, 'location': (j.get('location') or {}).get('name') or '',
                    'category': ', '.join(d.get('name', '') for d in (j.get('departments') or [])),
                    'description': j.get('content') or '',
                    'url': j.get('absolute_url') or '', 'source': 'Greenhouse',
                    'posted_at': j.get('first_published') or j.get('updated_at') or '',
                })
        except (requests.RequestException, ValueError, TypeError) as e:
            print(f'Greenhouse board {slug}: {e}')
    return output