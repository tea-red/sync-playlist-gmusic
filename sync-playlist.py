from libpytunes import Library
from gmusicapi import Mobileclient
from dotenv import load_dotenv
import time
import os

# プレイリストの曲を削除(プレイリストはそのまま)→新規追加版

# .envファイルから設定値読み込み
load_dotenv()

# itunes music library xmlのパスを取得
ITUNES_MUSIC_LIBLARY_XML_PATH = os.environ["ITUNES_MUSIC_LIBLARY_XML_PATH"]
MAX_GPLAYLIST_SONGS_NUM = 1000

mc = Mobileclient()
mc.oauth_login(mc.FROM_MAC_ADDRESS)

# google play musicの曲リストを取得
gLibrary = mc.get_all_songs()

# google play musicのプレイリストとそのコンテンツを取得
gPlaylistsAndContents = mc.get_all_user_playlist_contents()

# itunesのライブラリファイル読み込み
iLibrary = Library(ITUNES_MUSIC_LIBLARY_XML_PATH)

# プレイリスト一覧を取得
iAllPlaylists = iLibrary.il['Playlists']

# プレイリスト一覧からスマートプレイリスト、自作のプレイリスト以外を除く
iPlaylists = filter(lambda v: (('Distinguished Kind') not in v) and (('Master') not in v) , iAllPlaylists)

print('load end')

# itunesのプレイリストごとに
for iPlaylist in iPlaylists:
    # プレイリスト名を表示
    print("playlistName = {p}".format(p=iPlaylist['Name']))

    # 曲を登録するプレイリストID保存用変数定義
    gPlaylistId = None

    # google play musicの一致するプレイリストを取得
    filteredPlaylistsAndContentsIter = filter(lambda v: v['name'] == iPlaylist['Name'], gPlaylistsAndContents)

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
    iPlaylistItems = len(iPlaylist['Playlist Items'])
    if(iPlaylistItems > MAX_GPLAYLIST_SONGS_NUM):
        # オーバーしている旨のメッセージを出す
        print("playlistName = {p} is over max playlist song size :{n}".format(p=iPlaylist['Name'], n=iPlaylistItems))
        # プレイリストが存在している場合は削除する。
        if gPlaylistId != None:
            mc.delete_playlist(gPlaylistId)
        continue

    # プレイリストが見つからなかったら新たに作成する。
    if gPlaylistId == None:
        gPlaylistId = mc.create_playlist(iPlaylist['Name'])

    # itunesのプレイリストに含まれるTrack IDのリストを取得
    iPlTrIds = map(lambda v: v['Track ID'], iPlaylist['Playlist Items'])

    # itunesのtrackidからgoogle play musicのsong idリストを取得
    def getGSongIdFromITrackId(iTrackId):
        # 紐づくitunesの曲情報を取得
        iSong = iLibrary.songs.get(iTrackId)

        # itunesのタイトル、アルバム、アーティストに一致するgoogle play musicのトラックを取得
        foundGTrack = [
            gTrack for gTrack in gLibrary
            if gTrack['title'] == iSong.name
            and gTrack['album'] == iSong.album
            and gTrack['artist'] == iSong.artist
        ]

        # (1曲に特定できない、一致する曲がない)
        if(len(foundGTrack) != 1):
            # メッセージを出力
            print("not found {n}".format(n=iSong.name))
            return None

        return foundGTrack[0]['id']

    # 登録対象のgoogle play musicのidリストを取得
    addGTrackIdIter = map(lambda id: getGSongIdFromITrackId(id),iPlTrIds)
    addGTrackIdList = [id for id in addGTrackIdIter]

    # スリープ
    time.sleep(1)

    # 対象のidを登録対象のプレイリストへ追加
    addResult = mc.add_songs_to_playlist(gPlaylistId, addGTrackIdList)

