# My discord bot



# Dependencies

## The transcription module
Requires ffmpeg, mediainfo and sox (from the audiophile module)
`sudo apt-get install ffmpeg mediainfo sox`

on windows TorchCodec requires ffmpeg installation with shared libraries


If you have Cuda install cuda capable torch 
`pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126`


# Installing it yourself

1. Install Python and create your virtual environment
2. Use the following command in your venv to install requirements `pip install --require-virtualenv -r requirements.txt`
3. Create a `.env` file by filling in the `.env.example` file. 
4. Run main.py