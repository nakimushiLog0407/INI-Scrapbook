import os
import json
import urllib.parse
import urllib.request

API_KEY = os.environ["YOUTUBE_API_KEY"]
CHANNEL_ID = "UCc-itdQHxLvUlPrDxIiSJrA"


def youtube_api(endpoint, params):
    params["key"] = API_KEY
    url = "https://www.googleapis.com/youtube/v3/" + endpoint
    url += "?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url) as response:
        return json.load(response)


# ① INIのチャンネル情報から「アップロード動画一覧」のIDを取得
channel_data = youtube_api(
    "channels",
    {
        "part": "contentDetails",
        "id": CHANNEL_ID,
    },
)

uploads_playlist_id = (
    channel_data["items"][0]
    ["contentDetails"]
    ["relatedPlaylists"]
    ["uploads"]
)

# ② アップロード動画一覧から最新5件を取得
video_data = youtube_api(
    "playlistItems",
    {
        "part": "snippet,contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": 5,
    },
)

# ③ 必要な情報だけ取り出す
videos = []

for item in video_data["items"]:
    video_id = item["contentDetails"]["videoId"]

    videos.append(
        {
            "video_id": video_id,
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
        }
    )

print(json.dumps(videos, ensure_ascii=False, indent=2))
