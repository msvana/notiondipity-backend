from base import aiotest, client, db, TEST_HEADERS

assert client, db


@aiotest
async def test_recommend(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media is a difficult problem',
        'pageId': 'a80b1e5a5c8f440da67047680b2f82ce'
    }

    response = await client.post('/v2/recommend/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json = await response.get_json()
    assert 'recommendations' in json
    assert json['status'] == 'OK'

    # Page with matching ID is ignored so only 4 out of 5 test pages are returned
    assert len(json['recommendations']) == 4

    assert type(json['recommendations'][0]) is list
    assert len(json['recommendations'][0]) == 3


@aiotest
async def test_recommend_no_page_id(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
    }

    response = await client.post('/v2/recommend/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json = await response.get_json()
    assert 'recommendations' in json
    assert json['status'] == 'OK'

    # There is no matching page ID in the request, so all 5 test pages are returned
    assert len(json['recommendations']) == 5
    assert type(json['recommendations'][0]) is list
    assert len(json['recommendations'][0]) == 3


@aiotest
async def test_compare(client):
    request_data = {
        'title': 'Prince',
        'content': '''
            One way of how the strength of a country should be measured is by its ability to defend itself. 
            In other words, each country needs two things - a good army and good laws. These two things go 
            hand in hand. 

            There are three ways of acquiring an army: having your own, hiring mercenaries or relying of 
            foreign aid. The first option is the best one. For one an army of your own men is more loyal and 
            individual soldiers have a lot to lose if they fail to defend their country. 

            Mercenaries are unreliable. They are good only in peace. No one is willing to get killed for money. 
            If their commanders are incompetent, then the army will likely fail. And if they are competent, they might 
            have their own goals. 

            Foreign aid is the worst option. You are completely reliant on some other Prince. You are giving them 
            too much power.

            Leading an army might be the most important skill a prince might have. And he should train this skill 
            even during a period of peace. He should let his army practice and he himself should study strategies, 
            history and geography. If the prince indulges in pleasures instead of improving his military skills, 
            then he is quite sure to lose his princedom.
        ''',
        'pageId': 'c82b2d8f6eb647bba272cc77288f9d96',
        'secondPageId': 'ebc5adb46616447f883646215ccd62da'
    }
    response = await client.post('/compare/', headers=TEST_HEADERS, json=request_data)
    assert response.status_code == 200
    json = await response.get_json()
    assert json['status'] == 'OK'
    assert json['comparison']['cached'] is False
    assert len(json['comparison']['similarities']) > 0
    assert len(json['comparison']['differences']) > 0
    assert len(json['comparison']['combinations']) > 0

    # The response should be cached now
    response = await client.post('/compare/', headers=TEST_HEADERS, json=request_data)
    assert response.status_code == 200
    json_cached = await response.get_json()
    assert json_cached['comparison']['cached'] is True
    assert json['comparison']['similarities'] == json_cached['comparison']['similarities']
    assert json['comparison']['differences'] == json_cached['comparison']['differences']
    assert json['comparison']['combinations'] == json_cached['comparison']['combinations']

    # After changing the text the comparison cache should be no longer valid
    request_data['content'] = '''
        One way of how the strength of a country should be measured is by its ability to defend itself.
        In other words, each country needs two things - a good army and good laws. These two things go
        hand in hand.

        There are three ways of acquiring an army: having your own, hiring mercenaries or relying of
        foreign aid. The first option is the best one. For one an army of your own men is more loyal and
        individual soldiers have a lot to lose if they fail to defend their country.

        Mercenaries are unreliable. They are good only in peace. No one is willing to get killed for money.
        If their commanders are incompetent, then the army will likely fail. And if they are competent, they might
        have their own goals.

        Foreign aid is the worst option. You are completely reliant on some other Prince. You are giving them
        too much power.

        Leading an army might be the most important skill a prince might have. And he should train this skill
        even during a period of peace. He should let his army practice and he himself should study strategies,
        history and geography. If the prince indulges in pleasures instead of improving his military skills,
        then he is quite sure to lose his princedom.
        
        Machiavelli distinguishes between princes that acquired their new kingdom by luck and princes who acquired 
        it by merit. The latter is a better option. It might be difficult to build a princedom based on your merit. 
        But it will be quite easy to stay at power afterwards.

        Even princes with merit need a bit of luck - a good opportunity that would allow them to kick-start their 
        princedom. But everything afterwards is a question of skill.
        
        A new prince has to be able to use force when needed. “All armed prophets have been victorious, and all 
        unarmed prophets have been destroyed”.
    '''

    response = await client.post('/compare/', headers=TEST_HEADERS, json=request_data)
    assert response.status_code == 200
    json_modified = await response.get_json()
    assert json_modified['comparison']['cached'] is False
    assert len(json_modified['comparison']['similarities']) > 0
    assert len(json_modified['comparison']['differences']) > 0
    assert len(json_modified['comparison']['combinations']) > 0
    assert json_modified['comparison']['similarities'] != json_cached['comparison']['similarities']
    assert json_modified['comparison']['differences'] != json_cached['comparison']['differences']
    assert json_modified['comparison']['combinations'] != json_cached['comparison']['combinations']
