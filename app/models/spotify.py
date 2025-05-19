from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


# Shared models
class SpotifyImage(BaseModel):
    url: str
    height: Optional[int]
    width: Optional[int]


class SpotifyContext(BaseModel):
    type: Optional[str]
    href: Optional[str]


# Artist model
class SpotifyArtist(BaseModel):
    id: str
    name: str
    type: Optional[str]


# Album model
class SpotifyAlbum(BaseModel):
    id: str
    name: str
    album_type: Optional[str]
    release_date: Optional[str]
    total_tracks: Optional[int]
    images: List[SpotifyImage]


# Track model
class SpotifyTrack(BaseModel):
    id: str
    name: str
    duration_ms: int
    explicit: bool
    preview_url: Optional[str]
    popularity: Optional[int]
    track_number: int
    disc_number: int
    artists: List[SpotifyArtist]
    album: SpotifyAlbum


# Recently played item
class RecentlyPlayedItem(BaseModel):
    played_at: datetime
    context: Optional[SpotifyContext]
    track: SpotifyTrack


class RecentlyPlayedResponse(BaseModel):
    items: List[RecentlyPlayedItem]
    next: Optional[str]
    cursors: Optional[dict]
    limit: int
    href: str


# Spotify user model
class SpotifyUser(BaseModel):
    id: str
    display_name: Optional[str]
    email: Optional[str]
    country: Optional[str]
    product: Optional[str]
    images: List[SpotifyImage]