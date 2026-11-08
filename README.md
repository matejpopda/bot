# My discord bot


# Running using Docker Compose

Example compose.yaml in docker/ 



# Running without Docker 

## The transcription module
Requires ffmpeg, mediainfo and sox (from the audiophile module)
`sudo apt-get install ffmpeg mediainfo sox`

on windows TorchCodec requires ffmpeg installation with shared libraries

# Installing it yourself
1. Install Python and create your virtual environment
2. Use the following command in your venv to install requirements `pip install --require-virtualenv -r requirements.txt`
3. Create a `config_files/.env` file by filling in the `.env.example` file. 
4. For transcribing Yt-dl requires a cookie file, follow the tutorial on its website and then put it in the `config_files/www.youtube.com_cookies.txt`
4. Run main.py
