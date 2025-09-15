# DaddyLive TV

DaddyLive is a platform that offers live TV and sports streaming via browser. For added flexibility, this repository provides an M3U playlist featuring DaddyLive's channels. With this, you can load the streams into TiviMate.

You can view the full list of channels provided by DaddyLive [here](https://daddylivestream.com/24-7-channels.php). 

At the time of compiling this list, a few streams were down so if they existed in TVPass, they were used as a substitute, otherwise they were removed entirely.

Adult channels have been omitted <sub>(you gooners)</sub>.

# Instructions
Download **Termux** from the Google Play Store on your Android TV box.

_I also recommend the **Google TV** app for it's remote keyboard._


Open Termux and install both git and python by typing:
```
pkg install git python -y
```
You'll also want to install the requests python module:
```
pip install requests
```
Once finished, clone the repo and enter the directory:
```
git clone https://github.com/phosani/daddylive-m3u.git
cd daddylive-m3u
```
Now run the daddy.py script:
```
python3 daddy.py
```
This will begin scraping all the necessary keys, compiling them into URLs, and then curling them. During the curl process, you should see a bunch of URLs flying by followed by a "SUCCESS. HTTP/2 200". This will all take a while to complete. Do not interrupt it.

When finished, you'll see "Daddy script completed."

Some URLs may result in 403 (418 in TiviMate) due to how long it takes to process everything (URL timestamps expiring). As you go through the channels in TiviMate, if you discover one that is returning a 418, run:
```
python3 manual_daddy.py
```
and enter the ID of that channel (you can find the ID in the tivimate_playlist.m3u8 "premiumXX").

# Playlist
That's it. TiviMate should be ready to go.

Load the URLs below into Tivimate as an "M3U Playlist."
  
  **Playlist:** `https://tinyurl.com/2wrkh9tw`
  
   **EPG URL:** `https://tinyurl.com/2hu2f68t`

<sub>If you don't have TiviMate Premium, your EPG data (TV schedule) does not get auto updated and may say "No information" after 3 days (my list saves up to 3 days worth of information), so you'll just have to refresh it manually in settings. Every few weeks, I have to manually login to keep my EPG playlist active and sometimes I just forget about it so if it's been a while since any new information has populated the guide, either leave a comment on the Issues page, or just wait for me to notice.</sub>

# Disclaimer:

This repository has no control over the streams, links, or the legality of the content provided by daddylive.dad (including all mirror sites). It is the end user's responsibility to ensure the legal use of these streams, and we strongly recommend verifying that the content complies with the laws and regulations of your country before use.

