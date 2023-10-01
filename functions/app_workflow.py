from firebase_admin import messaging
import math
import pandas as pd
from geopy.distance import geodesic

# (0) ワークフロー
def workflow(db):
    user_data = get_user_data(db)
    if user_data is not None:
        distances = calculate_distance(user_data[['id', 'latitude', 'longitude']])
        # print(distances)
        update_nearby_user_details(db,user_data, distances)
        return 'Success'
    else:
        return 'Error'

# (1) Firestoreからユーザーデータを取得
def get_user_data(db):
    try:
        users_ref = db.collection(u'users').get()
        user_data = [doc.to_dict() for doc in users_ref]
        return pd.DataFrame(user_data)
    except Exception as e:
        print(f'Error: {e}')
        return None

# (2) 2点間の距離を計算
def calculate_distance(locations):
    distances = {}
    for i, row in locations.iterrows():
        uid = row['id']
        coords = (row['latitude'], row['longitude'])
        distances[uid] = {
            'id': uid,
            'distances': {
                other_uid: geodesic(coords, (locations.loc[locations['id'] == other_uid, 'latitude'].values[0], locations.loc[locations['id'] == other_uid, 'longitude'].values[0])).m
                for other_uid in locations['id'] if other_uid != uid
            }
        }
    return distances

# (3) 近くのユーザー情報を更新
def update_nearby_user_details(db,data, distances):
    for uid, distances_dict in distances.items():
        nearby_users = [other_uid for other_uid, distance in distances_dict['distances'].items() if distance <= 200]
        
        nearby_user_details = []
        for nearby_uid in nearby_users:
            user_data = data[data['id'] == nearby_uid].iloc[0]
            # distances_dict['distances'][nearby_uid]を10m単位で切り上げ
            distance = distances_dict['distances'][nearby_uid]
            rounded_distance = math.ceil(distance / 10) * 10
            m_rounded_distance = str(rounded_distance) + "m圏内"

            # print(f"uid:{uid}, nearby_uid:{nearby_uid}, distance:{m_rounded_distance}")
            nearby_user_details.append({
                'id': nearby_uid,
                'distance': m_rounded_distance,
                'name': user_data['name'],
                'avatarUrl': user_data['avatarUrl'],
                'comment': user_data['comment'],
                'howStrong': int(user_data['howStrong'])
            })
            # print(f"fcmToken:{user_data['fcmToken']}")
            fcmToken = user_data['fcmToken']
            if fcmToken is not None:
                push_notification(fcmToken)
            
        db.collection(u'users').document(uid).update({'nearbyUserDetails': nearby_user_details})

# プッシュ通知
def push_notification(fcmToken):
    registration_token = fcmToken
    message = messaging.Message(
        notification=messaging.Notification(
            title="message from Python",
            body="This is a message from Python",
        ),
        token=registration_token,
    )
    response = messaging.send(message)
    print('Successfully sent message:', response)