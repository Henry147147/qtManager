Project: Auto qBittorrent manager. 

Goal:

Scan files downloaded from qbittorrent, move them without needing manual intervention

Should be configurable via JSON and maybe a webGUI.

Planned features:

- Scan list of directories for movie files (including auto un-rar)
- Move the finished downloads to the hosting directory
- Rename the file (.mkv, .mp4, etc.) to known schema where a prompt can be written
- Switch the category of the seeded file.

Eventaually should be do able with TV shows as well.
- must determine if the downloaded files are a pack, single episode, etc.
- must determine which show it is in
- must determine which season it is in
- must copy to <dest>/<series>/<season>/file.mkv

MiSC
- Should be able to work with IMDB such that it is assured that a show name is valid and the imdb id is inserted into the filename
- Should be able to be a docker service such that is can be started easily
- Should be configruable for N number of categories and outputing destinations
- Should work with openAI API compat LLM to do this.


Useful links:
- https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-5.0)
