from mastodon import Mastodon
from mastodon_config import client_id, client_secret, access_token, api_base_url

# User auth information
# Connect to Mastodon API.
mastodon = Mastodon(
    client_id=client_id,
    client_secret=client_secret,
    access_token=access_token,
    api_base_url=api_base_url
)

# Load the image
image_path = "src/tmp/cat.png"
media = mastodon.media_post(image_path)

# Post the toot text along with the image
toot_text = "This is Mister Cat! 🐱"
mastodon.status_post(toot_text, media_ids=[media['id']])
