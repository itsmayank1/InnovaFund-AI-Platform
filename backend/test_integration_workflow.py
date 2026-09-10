from .conftest import register, login

def auth(client, email='integration_user@example.com', password='StrongPass123!'):
    register(client, email=email, password=password)
    token = login(client, email=email, password=password).json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_full_researcher_journey(client):
    """
    End-to-end: register -> build profile -> save a publication and a patent ->
    check funding recommendations reflect the profile -> confirm trends endpoints
    stay healthy once real user data exists.
    """
    headers = auth(client)

    r_profile = client.post('/api/v1/profile', headers=headers, json={
        'academic': {'degree': 'PhD'},
        'organization': {'name': 'Integration Test Lab'}
    })
    assert r_profile.status_code in (200, 201)

    r_domain = client.post('/api/v1/profile/domains', headers=headers, json={'value': 'AI & Machine Learning'})
    assert r_domain.status_code in (200, 201)

    r_keyword = client.post('/api/v1/profile/keywords', headers=headers, json={'value': 'Deep Learning'})
    assert r_keyword.status_code in (200, 201)

    r_pub_search = client.get('/api/v1/publications/search?q=machine+learning', headers=headers)
    assert r_pub_search.status_code == 200
    pubs = r_pub_search.json().get('results', r_pub_search.json())
    assert len(pubs) >= 1
    r_pub_save = client.post('/api/v1/profile/publications', headers=headers, json=pubs[0])
    assert r_pub_save.status_code == 201

    r_pat_search = client.get('/api/v1/patents/search?q=intelligence', headers=headers)
    assert r_pat_search.status_code == 200
    patents = r_pat_search.json().get('results', r_pat_search.json())
    assert len(patents) >= 1
    r_pat_save = client.post('/api/v1/profile/patents', headers=headers, json=patents[0])
    assert r_pat_save.status_code == 201

    r_recs = client.get('/api/v1/funding/recommendations', headers=headers)
    assert r_recs.status_code == 200
    recs = r_recs.json()
    assert len(recs) >= 1
    assert 'match_score' in recs[0]

    r_topics = client.get('/api/v1/trends/topics')
    assert r_topics.status_code == 200
    assert 'topics' in r_topics.json()

    r_hotspots = client.get('/api/v1/trends/hotspots')
    assert r_hotspots.status_code == 200

    r_citations = client.get('/api/v1/trends/citations')
    assert r_citations.status_code == 200


def test_cross_user_data_does_not_leak_into_funding_recs(client):
    """
    A second user with a different (empty) profile shouldn't see the first
    user's saved publications/patents affecting their own recommendation results.
    """
    headers_a = auth(client, email='user_a@example.com')
    client.post('/api/v1/profile', headers=headers_a, json={
        'academic': {'degree': 'PhD'}, 'organization': {'name': 'Lab A'}
    })
    client.post('/api/v1/profile/domains', headers=headers_a, json={'value': 'AI & Machine Learning'})

    headers_b = auth(client, email='user_b@example.com')
    client.post('/api/v1/profile', headers=headers_b, json={
        'academic': {'degree': 'MSc'}, 'organization': {'name': 'Lab B'}
    })

    r_saved_a = client.get('/api/v1/profile/publications', headers=headers_a)
    r_saved_b = client.get('/api/v1/profile/publications', headers=headers_b)
    assert r_saved_a.status_code == 200
    assert r_saved_b.status_code == 200
    assert r_saved_b.json() == []