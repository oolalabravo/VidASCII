import cv2
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip
import yt_dlp
from tqdm import tqdm
import numpy as np
import multiprocessing
import shutil
import numba

# ASCII characters ordered from dark to light
CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# ASCII art output settings
FONT_SIZE = 3
WIDTH = 600  # characters per line

# Load monospace font, fallback if not found
try:
    FONT = ImageFont.truetype("DejaVuSansMono.ttf", FONT_SIZE)
except OSError:
    try:
        FONT = ImageFont.truetype("Courier_New.ttf", FONT_SIZE)
    except OSError:
        FONT = ImageFont.load_default()

@numba.njit
def average_color_block_np(image_np, x, y, w, h):
    """
    Compute average RGB color of a rectangular block (NumPy optimized)
    """
    h_img, w_img, _ = image_np.shape
    r_sum = 0
    g_sum = 0
    b_sum = 0
    count = 0
    
    for i in range(y, min(y + h, h_img)):
        for j in range(x, min(x + w, w_img)):
            r_sum += image_np[i, j, 0]
            g_sum += image_np[i, j, 1]
            b_sum += image_np[i, j, 2]
            count += 1

    if count == 0:
        return 0, 0, 0
    return r_sum // count, g_sum // count, b_sum // count

def frame_to_ascii_image(frame, width=WIDTH):
    """
    Convert a single video frame (numpy array) into a colored ASCII art PIL image.
    """
    img = Image.fromarray(frame)
    aspect_ratio = img.height / img.width
    new_height = int(aspect_ratio * width * 0.55)  # Adjust character height scaling

    img = img.resize((width, new_height), Image.LANCZOS)
    img_np = np.array(img)

    gray = img.convert("L")
    pixels = np.array(gray).astype(float)
    gamma = 2.2
    pixels = ((pixels / 255.0) ** gamma) * (len(CHARS) - 1)
    pixels = np.clip(pixels, 0, len(CHARS) - 1).astype(int)
    ascii_chars = np.array([CHARS[i] for i in pixels.flat]).reshape(pixels.shape)

    out_img = Image.new("RGB", (width * FONT_SIZE, new_height * FONT_SIZE), "black")
    draw = ImageDraw.Draw(out_img)

    block_size_x = max(1, img_np.shape[1] // width)
    block_size_y = max(1, img_np.shape[0] // new_height)

    for y in range(new_height):
        y_pos = y * FONT_SIZE
        for x in range(width):
            char = ascii_chars[y, x]
            r, g, b = average_color_block_np(img_np, x * block_size_x, y * block_size_y, block_size_x, block_size_y)
            x_pos = x * FONT_SIZE
            draw.text((x_pos, y_pos), char, font=FONT, fill=(r, g, b))

    enhancer = ImageEnhance.Contrast(out_img)
    out_img = enhancer.enhance(1.1)

    return out_img

def download_youtube(url, filename="yt_video.mp4"):
    """
    Download YouTube video with best quality video+audio and merge to mp4.
    """
    if os.path.exists(filename):
        os.remove(filename)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': filename,
        'merge_output_format': 'mp4',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename

def convert_video_to_ascii_images(video_path, width=WIDTH, chunk_size=80):
    """
    Convert video file to ASCII images in chunks using multiprocessing.
    Saves frames to disk cache and returns list of file paths and FPS.
    """
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24

    temp_cache_dir = os.path.join(os.getcwd(), "cache_ascii_frames")
    os.makedirs(temp_cache_dir, exist_ok=True)
    print(f"Saving cached ASCII frames in {temp_cache_dir}")

    filenames = []
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        frames = []
        frame_index = 0
        print("🎨 Extracting and processing frames in chunks...")
        for _ in tqdm(range(total_frames)):
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)

            if len(frames) == chunk_size:
                ascii_images = pool.starmap(frame_to_ascii_image, [(f, width) for f in frames])
                for i, img in enumerate(ascii_images):
                    fname = os.path.join(temp_cache_dir, f"frame_{frame_index + i:06d}.png")
                    img.save(fname)
                    filenames.append(fname)
                frame_index += chunk_size
                frames.clear()

        if frames:
            ascii_images = pool.starmap(frame_to_ascii_image, [(f, width) for f in frames])
            for i, img in enumerate(ascii_images):
                fname = os.path.join(temp_cache_dir, f"frame_{frame_index + i:06d}.png")
                img.save(fname)
                filenames.append(fname)

    cap.release()
    return filenames, fps

def save_ascii_video_from_diskcache(frame_files, fps, audio_path=None, output_path="ascii_video.mp4"):
    """
    Assemble ASCII images into video, add audio if available, and clean up cache.
    """
    print("📼 Loading ASCII frames from disk cache and generating video...")
    frame_list = [np.array(Image.open(f)) for f in tqdm(frame_files)]
    clip = ImageSequenceClip(frame_list, fps=fps)

    if audio_path and os.path.exists(audio_path):
        audio_clip = AudioFileClip(audio_path)
        clip = clip.set_audio(audio_clip)

    clip.write_videofile(output_path, codec="libx264")

    cache_dir = os.path.dirname(frame_files[0])
    shutil.rmtree(cache_dir)
    print(f"Deleted cache directory: {cache_dir}")

if __name__ == "__main__":
    url = input("Enter YouTube URL: ")
    video_path = "yt_video.mp4"

    print("⬇️ Downloading video...")
    download_youtube(url, video_path)

    audio_path = None
    clip = VideoFileClip(video_path)
    if clip.audio is not None:
        audio_path = "temp_audio.wav"
        clip.audio.write_audiofile(audio_path, fps=44100, verbose=False, logger=None)
    else:
        print("⚠️ No audio track found, skipping audio.")

    frame_cache_files, fps = convert_video_to_ascii_images(video_path, width=WIDTH, chunk_size=120)
    output_file = os.path.join(os.getcwd(), "ascii_video.mp4")
    save_ascii_video_from_diskcache(frame_cache_files, fps, audio_path=audio_path, output_path=output_file)

    if audio_path and os.path.exists(audio_path):
        os.remove(audio_path)

    print(f"✅ ASCII video saved as {output_file}")
