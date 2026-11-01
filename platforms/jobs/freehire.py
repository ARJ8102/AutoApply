import requests

URL = 'https://freehire.me/api/v1/jobs/search'

def fetch_jobs(keyword='', pages=2, remote_only=False, junior_only=False, yc_only=False):
    output = []
    pages = max(1, min(int(pages), 10))
    for page in range(pages):
        params = {'limit': 100, 'offset': page * 100}
        if keyword.strip():
            params['q'] = keyword.strip()
        if remote_only:
            params['work_mode'] = 'remote'
        if junior_only:
            params['seniority'] = 'intern,junior'
        if yc_only:
            params['collections'] = 'yc'
        r = requests.get(URL, params=params, timeout=35)
        r.raise_for_status()
        payload = r.json()
        ignored = payload.get('meta', {}).get('ignored_params', [])
        if ignored:
            raise ValueError(f'freehire ignored filters: {ignored}')
        jobs = payload.get('data', [])
        for j in jobs:
            output.append({
                'id': str(j.get('public_slug') or j.get('external_id') or ''),
                'title': j.get('title') or '', 'company': j.get('company') or '',
                'location': j.get('location') or '',
                'category': ', '.join(str(s) for s in (j.get('skills') or [])),
                'description': j.get('description') or '',
                'url': j.get('url') or '', 'source': 'freehire',
                'countries': j.get('countries') or [],
                'posted_at': j.get('posted_at') or '',
                'work_mode': j.get('work_mode') or '',
                'seniority': j.get('seniority') or '',
            })
        if len(jobs) < 100 or len(output) >= payload.get('meta', {}).get('total', 10**12):
            break
    return output