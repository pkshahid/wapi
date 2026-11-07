# Media

```python
# upload → media id (valid ~30 days)
media = client.media.upload("./pic.png")                # path, bytes, or file
media = client.media.upload(open("pic.png","rb"), mime_type="image/png")

# get info incl. temporary download url
info = client.media.get(media.id)
print(info.url, info.mime_type, info.sha256, info.file_size)

# download bytes or to a file
data = client.media.download(info)
path = client.media.download("media-id-or-url", dest="./out.png")

# delete
client.media.delete(media.id)
```

## Resumable uploads

Template headers and profile pictures need an **asset handle** (`h:…`)
from the Resumable Upload API (requires `app_id`):

```python
handle = client.media.resumable_upload("./banner.jpg")
client.profile.update(profile_picture_handle=handle)
```

## Limits

| Type | Formats | Max |
|---|---|---|
| Image | JPEG, PNG | 5 MB |
| Video | MP4, 3GPP (H.264/AAC) | 16 MB |
| Audio | AAC, MP4, MPEG, AMR, OGG-Opus | 16 MB |
| Document | any MIME | 100 MB |
| Sticker | WebP 512×512 | 100 KB / 500 KB |
