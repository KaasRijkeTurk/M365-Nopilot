import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# SSL scope is nodig om playlists aan te passen (insert/delete)
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

# -------------------
# AUTH (Met Token Caching)
# -------------------
def get_youtube():
    creds = None
    
    # Het bestand token.json slaat de toegangs- en refresh-tokens van de gebruiker op
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    # Als er geen geldige inloggegevens zijn, laat de gebruiker inloggen
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # Als hernieuwen mislukt, dwingen we een nieuwe login af
                creds = None
                
        if not creds:
            if not os.path.exists("client_secret.json"):
                raise FileNotFoundError(
                    "❌ client_secret.json mist! Download deze uit de Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Sla de inloggegevens op voor de volgende keer
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

# -------------------
# GET PLAYLIST ITEMS (Met volledige paginering)
# -------------------
def get_playlist_items_full(youtube, playlist_id):
    print("YOUTUBE playlist_id RAW =", repr(playlist_id))
    
    items = []
    next_page_token = None

    try:
        # Blijf loops draaien zolang er pagina's zijn
        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            res = request.execute()

            for item in res.get("items", []):
                items.append({
                    "title": item["snippet"]["title"],
                    "video_id": item["snippet"]["resourceId"]["videoId"],
                    "playlist_item_id": item["id"]
                })

            # Check of er nog een pagina met video's is
            next_page_token = res.get("nextPageToken")
            if not next_page_token:
                break

    except Exception as e:
        print(f"[YOUTUBE ERROR] Kon playlist items niet ophalen: {e}")
        raise e

    return items

# -------------------
# ADD TO PLAYLIST
# -------------------
def add_to_playlist(youtube, playlist_id, video_id):
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
    except Exception as e:
        print(f"[YOUTUBE ERROR] Kon video {video_id} niet toevoegen aan playlist {playlist_id}: {e}")
        raise e