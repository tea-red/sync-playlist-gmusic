from itunesLibrary import library
from gmusicapi import Mobileclient
from dotenv import load_dotenv
import time
import os

# プレイリストの曲を削除(プレイリストはそのまま)→新規追加版

# .envファイルから設定値読み込み
load_dotenv()

# itunes music library xmlのパスを取得
ITUNES_MUSIC_LIBLARY_XML_PATH = os.environ["ITUNES_MUSIC_LIBLARY_XML_PATH"]
SYNC_PLAYLIST_NAME = os.environ["SYNC_PLAYLIST_NAME"]
MAX_GPLAYLIST_SONGS_NUM = 1000

print("sync playlistName = {p}".format(p=SYNC_PLAYLIST_NAME))

mc = Mobileclient()
mc.oauth_login(mc.FROM_MAC_ADDRESS)

print('google play music login success')

print('google play music load start')

# google play musicの曲リストを取得
gLibrary = mc.get_all_songs()

print('google play music library loaded')

# google play musicのプレイリストとそのコンテンツを取得
gPlaylistsAndContents = mc.get_all_user_playlist_contents()

print('google play music playlists loaded')

print('itunes load start')

# itunesのライブラリファイル読み込み
iLibrary = library.parse(ITUNES_MUSIC_LIBLARY_XML_PATH)

print('itunes playlists loaded')

# プレイリスト一覧を取得
iPlaylist = iLibrary.getPlaylist(SYNC_PLAYLIST_NAME)

# プレイリスト名を表示
print("playlistName = {p}".format(p=iPlaylist.itunesAttibutes['Name']))

# 曲を登録するプレイリストID保存用変数定義
gPlaylistId = None

# google play musicの一致するプレイリストを取得
filteredPlaylistsAndContentsIter = filter(lambda v: v['name'] == iPlaylist.itunesAttibutes['Name'], gPlaylistsAndContents)

# 一致するプレイリストが見つかったら
for filteredPlaylistAndContents in filteredPlaylistsAndContentsIter:
    # googleplaymusicのプレイリストIDを取得
    gPlaylistId = filteredPlaylistAndContents['id']

    # プレイリストに含まれるトラックidのリストを取得して
    includeTrackIdsIter = map(lambda v: v['id'], filteredPlaylistAndContents['tracks'])

    # プレイリストから消去
    mc.remove_entries_from_playlist([trackId for trackId in includeTrackIdsIter])
    break

# プレイリストの登録曲数がgoogle play musicの最大登録数よりも多い場合は
iPlaylistItems = len(iPlaylist.items)
if(iPlaylistItems > MAX_GPLAYLIST_SONGS_NUM):
    # オーバーしている旨のメッセージを出す
    print("playlistName = {p} is over max playlist song size :{n}".format(p=iPlaylist.itunesAttibutes['Name'], n=iPlaylistItems))
    # プレイリストが存在している場合は削除する。
    if gPlaylistId != None:
        mc.delete_playlist(gPlaylistId)
    # return
    exit()

# プレイリストが見つからなかったら新たに作成する。
if gPlaylistId == None:
    gPlaylistId = mc.create_playlist(iPlaylist.itunesAttibutes['Name'])

# google play musicのsong idを取得
def getGSongId(songName, artist, album):
    # itunesのタイトル、アルバム、アーティストに一致するgoogle play musicのトラックを取得
    foundGTrack = [
        gTrack for gTrack in gLibrary
        if gTrack['title'] == songName
        and gTrack['album'] == album
        and gTrack['artist'] == artist
    ]

    # (1曲に特定できない、一致する曲がない)
    if(len(foundGTrack) != 1):
        # メッセージを出力
        print("not found {n}".format(n=songName))
        return None

    return foundGTrack[0]['id']

# 登録対象のgoogle play musicのidリストを取得
addGTrackIdIter = map(
    lambda song: getGSongId(
        song.itunesAttibutes['Name'],
        song.itunesAttibutes['Artist'],
        song.itunesAttibutes['Album'],
    ),
    iPlaylist.items
)
addGTrackIdList = [id for id in addGTrackIdIter]

# スリープ
time.sleep(1)

# 対象のidを登録対象のプレイリストへ追加
addResult = mc.add_songs_to_playlist(gPlaylistId, addGTrackIdList)

