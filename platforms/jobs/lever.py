import requests


def fetch_jobs(boards):
    output = []
    for company, slug in boards.items():
        try:
            r = requests.get(f'https://api.lever.co/v0/postings/{slug}', params={'mode': 'json'}, timeout=25)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list):
                raise ValueError('Unexpected Lever response')
            for j in data:
                cat = j.get('categories') or {}
                sections = j.get('lists') or []
                extra = ' '.join(str(s.get('content') or '') for s in sections if isinstance(s, dict))
                output.append({
                    'id': str(j.get('id') or ''), 'title': j.get('text') or '',
                    'company': company, 'location': cat.get('location') or '',
                    'category': ', '.join(str(cat.get(k) or '') for k in ('team', 'commitment', 'department')),
                    'description': (j.get('descriptionPlain') or j.get('description') or '') + ' ' + extra,
                    'url': j.get('hostedUrl') or j.get('applyUrl') or '', 'source': 'Lever',
                    'work_mode': j.get('workplaceType') or '',
                })
        except (requests.RequestException, ValueError, TypeError) as e:
            print(f'Lever board {slug}: {e}')
    return output