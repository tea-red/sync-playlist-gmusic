from gmusicapi import Mobileclient

# google play musicのプレイリストを順に削除

mc = Mobileclient()
mc.oauth_login(mc.FROM_MAC_ADDRESS)

# google play musicのプレイリストを取得
gPlaylists = mc.get_all_playlists()

for gPlaylist in gPlaylists:
    mc.delete_playlist(gPlaylist['id'])
    print("deleted playlistName = {p}".format(p=gPlaylist['name']))
