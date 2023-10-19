from base import aiotest, client, db, TEST_HEADERS

assert client, db


@aiotest
async def test_recommend(client):
    page_contents = {
        'title': 'Ideas',
        'content': 'Sentiment analysis on social media',
        'pageId': 'f4067fc5-80d2-496c-a306-8e8c6f53329a'
    }

    response = await client.post('/v2/recommend/', headers=TEST_HEADERS, json=page_contents)
    assert response.status_code == 200
    json = await response.get_json()
    assert 'recommendations' in json
    assert json['status'] == 'OK'
    assert len(json['recommendations']) == 2
    assert type(json['recommendations'][0]) == list
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
    assert len(json['recommendations']) == 3
    assert type(json['recommendations'][0]) == list
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
        'second_page_id': 'a534013e-93ec-4a18-8ebc-963fa90559d2'
    }
    response = await client.post('/compare/', headers=TEST_HEADERS, json=request_data)
    assert response.status_code == 200
    json = await response.get_json()
    print(json)

