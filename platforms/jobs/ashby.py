import requests


def fetch_jobs(boards):
    output = []
    for company, slug in boards.items():
        try:
            r = requests.get(f'https://api.ashbyhq.com/posting-api/job-board/{slug}', params={'includeCompensation': 'true'}, timeout=25)
            r.raise_for_status()
            for j in r.json().get('jobs', []):
                output.append({
                    'id': str(j.get('id') or j.get('jobUrl') or ''),
                    'title': j.get('title') or '', 'company': company,
                    'location': j.get('location') or '',
                    'category': ', '.join(str(j.get(k) or '') for k in ('department', 'team', 'employmentType')),
                    'description': j.get('descriptionPlain') or j.get('descriptionHtml') or '',
                    'url': j.get('jobUrl') or j.get('applyUrl') or '', 'source': 'Ashby',
                    'work_mode': j.get('workplaceType') or ('remote' if j.get('isRemote') else ''),
                    'posted_at': j.get('publishedAt') or '',
                })
        except (requests.RequestException, ValueError, TypeError) as e:
            print(f'Ashby board {slug}: {e}')
    return output