# DaddyLive TV (OUTDATED)

DaddyLive is a platform that offers live TV and sports streaming across selected categories. Users can stream and watch live TV directly through their browser without the need for an account or subscription.

For added flexibility, this repository provides an M3U playlist featuring DaddyLive's channels. With this, you can load the streams into any IPTV application that supports M3U-formatted playlists, however this repo will only provide the playlist format for Tivimate. Figure out how to format it for other applications yourself.

You can view the full list of channels provided by DaddyLive [here](https://daddylive.dad/24-7-channels.php). 

<ins>**IN ORDER FOR STREAMS TO PLAY YOU NEED TO HAVE SOME SORT OF FORWARD PROXY SERVER RUNNING.**</ins>

At the time of compiling this list, a few streams were down so if they existed in TVPass, they were used as a substitute, otherwise they were removed entirely.

Adult channels have been omitted <sub>(you gooners)</sub>.

**These scripts were made with linux commands in mind so in order for them to work properly, you either need to be running Linux or Windows Subsystem for Linux (WSL).**


# Instructions (NO LONGER WORKS)
~~Choose somewhere you wanna save these files, cd into that directory in terminal, and clone the project.~~
```
git clone https://github.com/phosani/daddylive-m3u.git
```
~~cd into the project and run **generate_auth_list.py**. This will compile each streams channel key, authTs, authRnd, and authSig.~~
```
cd daddylive-m3u
python3 generate_auth_list.py
```
~~This will take a minute to enumerate. Do not interrupt it.~~

~~When it finishes, run **generate_signature_urls.py** to compile all of the stream signatures into URLs that are used to unlock the decryption keys.~~
```
python3 generate_signature_urls.py
```
~~run **curl.py** to curl each URL. This is essentially what your browser does anytime you load a stream on the daddylive website.~~
```
python3 curl.py
```
~~This should begin returning HTTP/2 200 for every source. Do not interrupt it.~~

~~The signature URLs generated expire after a certain interval so if you wait too long to perform this curl, you'll likely encounter HTTP/2 403. If that happens, delete the channelAuth.txt file created, and start over from generate_auth_list.py.~~

~~Now enable whatever forward proxy you have or if you choose to use the one provided:~~
```
python3 fproxy.py
```
~~In your Android TV box network settings, add the IP of the device hosting the proxy, port 8866, and remove localhost as an exception.~~

# Playlist
~~That's it. All streams should now be ready for decryption upon playback.~~

~~Load the URLs below into Tivimate as an "M3U Playlist."~~
  
  ~~**Playlist:** `https://tinyurl.com/2wrkh9tw`~~
  
   ~~**EPG URL:** `https://tinyurl.com/2hu2f68t`~~

~~If you ever receive Error 403 in the future, they may have refreshed their streams. In that case delete the ChannelAuth.txt created by generate_auth_list.py and repeat the above instructions.~~

# Disclaimer:

This repository has no control over the streams, links, or the legality of the content provided by daddylive.dad (including all mirror sites). It is the end user's responsibility to ensure the legal use of these streams, and we strongly recommend verifying that the content complies with the laws and regulations of your country before use.

