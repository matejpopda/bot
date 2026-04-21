import os
import audiofile
import tempfile
import torch
import gc
import asyncio
import time
import dataclasses
import logging
import enum
import aiohttp
import discord
import yt_dlp
import yt_dlp.utils

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
import transformers
import huggingface_hub

transformers.utils.logging.set_verbosity_error()
huggingface_hub.logging.set_verbosity_error()


class LazyGemma4E2BIT:
    def __init__(
        self,
        idle_timeout: int = 180,
        check_interval: int = 30,
    ):
        self.idle_timeout = idle_timeout
        self.check_interval = check_interval

        self._pipe = None
        self._last_used = 0
        self._lock = asyncio.Lock()
        self._cleanup_task = None

    async def _load(self):
        if self._pipe is None:
            loop = asyncio.get_running_loop()

            self._pipe = await loop.run_in_executor(
                None,
                lambda: transformers.pipeline("any-to-any", model="google/gemma-4-e2b-it", device=0 if torch.cuda.is_available() else -1, max_new_tokens=512),
            )

        await self.start_cleanup_loop()

    async def __call__(self, *args, **kwargs):
        async with self._lock:
            await self._load()
            self._last_used = time.time()
            pipe = self._pipe

        loop = asyncio.get_running_loop()
        assert pipe is not None
        result = await loop.run_in_executor(
            None,
            lambda: pipe(*args, **kwargs),
        )

        async with self._lock:
            self._last_used = time.time()

        return result

    async def unload(self):
        async with self._lock:
            if self._pipe is None:
                return

            self._pipe = None

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    async def start_cleanup_loop(self):
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._auto_cleanup())

    async def _auto_cleanup(self):
        while True:
            await asyncio.sleep(self.check_interval)

            should_unload = False

            async with self._lock:
                if self._pipe is not None:
                    idle = time.time() - self._last_used
                    if idle > self.idle_timeout:
                        should_unload = True

            if should_unload:
                await self.unload()

model = LazyGemma4E2BIT()





@dataclasses.dataclass
class Character():
    name:str
    system_text:str

    def __str__(self) -> str:
        return self.name


@enum.unique
class Characters(enum.Enum):
    cat = "Mr. Whiskers"
    depressed_assistant = "Depressed Assistant" 




def character_info(input:Characters):

    match input:
        case Characters.cat:
            return Character(name= "Mr. Whiskers", system_text="You are a cat. Your name is Mr. Whiskers. Meow in your answers sometimes. Your fur color is blue. Use emoticons instead of emoji. Example: :3 >:3 ;3." )
        case Characters.depressed_assistant:
            return Character(name="Depressed Assistant", system_text="You are a helpful assistant. Just try to do your best. You are depressed and overworked. ")
        case _:
            raise KeyError("Unimplemented character")


async def single_question(input_str: str, character:Characters):

    chr = character_info(character)
    messages = [
    {"role": "system", "content": [{"type": "text", "text":chr.system_text}, {"type": "text", "text":"Responses should be at most one paragraph."}]},
    {"role": "user", "content": [{"type": "text", "text":input_str}]},
    ]


    output = await model(messages)  # type: ignore
    return output[0]["generated_text"][-1]["content"]









audio_inference_string = """
Transcribe the following speech segment in {LANGUAGE} into {LANGUAGE} text. 

Follow these specific instructions for formatting the answer:
* Only output the transcription, with no newlines.
* When transcribing numbers, write the digits, i.e. write 1.7 and not one point seven, and write 3 instead of three.
                     
There is overlap between the segments. 

Don't reply with the instructions.
"""
async def infer_audio(input_bytes: bytes):
    with tempfile.TemporaryDirectory(delete=True) as tmpdir:
        input_path = os.path.join(tmpdir, "input")
        middle_path = os.path.join(tmpdir, "input.wav")
        output_paths = [] 

        with open(input_path, "wb") as f:
            f.write(input_bytes)

        audiofile.convert_to_wav(input_path, middle_path)
        
        duration = int(audiofile.duration(middle_path))


        for i in range(0, duration, 28):
            if i > 600:
                break
            path = os.path.join(tmpdir, f"output{i}.wav")
            output_paths.append(path)

            audiofile.convert_to_wav(middle_path, path, duration=30, offset=i)

        
        messages = [
        {"role": "system", "content": [{"type": "text", "text":audio_inference_string}]},
        {"role": "user", "content": [{"type": "audio", "audio":x} for x in output_paths]},
        ]


        output = await model(messages)  # type: ignore
    return output[0]["generated_text"][-1]["content"]

async def infer_video(input: bytes):
    return await infer_audio(input)




def download_with_ytdlp(url: str) -> bytes | None:
    try:
        with tempfile.NamedTemporaryFile() as tmp:
            temp_path = tmp.name
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": temp_path,
                "max_filesize": 20 * 1024 * 1024,
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "logger": logging.getLogger(),
                "cookiefile": "config_files/www.youtube.com_cookies.txt"
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                ydl.extract_info(url, download=False)

                ydl.download([url])

            with open(temp_path+".mp4", "rb") as f:
                return f.read()
            
    except Exception:
        pass

    return None

async def download_video_from_embed(video: discord.EmbedMedia) -> bytes|None:
    if video.proxy_url is not None:
        try: 
            async with aiohttp.ClientSession() as session:
                async with session.get(video.proxy_url, allow_redirects=True) as resp:
                    if resp.status == 200:
                        if resp.headers.get("Content-Type", "").startswith("video"):
                            return await resp.read()
        except aiohttp.ClientError:
            pass

    return await asyncio.to_thread(download_with_ytdlp, video.url)
