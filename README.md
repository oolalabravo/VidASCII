
# YouTube Video to ASCII Art Video 🎨🖥️

Convert any YouTube video into a high-resolution **colored ASCII art video** using Python. Supports full video processing with optional audio retention, live frame-to-ASCII conversion, and multiprocessed acceleration.

---

## Features

- Downloads YouTube videos automatically using `yt_dlp`.
- Converts video frames into **colored ASCII art** images.
- Supports **ultra-high resolution ASCII rendering** using custom monospace fonts.
- Uses **multiprocessing** for faster frame processing.
- Optional audio retention from the original video.
- Temporary disk caching for efficient memory usage.
- Final video exported as MP4 (`libx264` codec).

---

## Dependencies

```bash
pip install opencv-python pillow moviepy yt-dlp tqdm numpy numba
````

* Make sure you have a monospace font like `DejaVuSansMono.ttf` or `Courier_New.ttf` installed. The script falls back to a default font if not found.

---

## Usage

1. Clone the repository:

```bash
git clone <repo_url>
cd <repo_name>
```

2. Run the script:

```bash
python video_to_ascii.py
```

3. Enter the **YouTube URL** when prompted.
4. ASCII video will be saved at:
   `F:\programs\ASCII video\ascii_video.mp4` (customizable in the script).

---

## How it Works

1. Download the video from YouTube using `yt_dlp`.
2. Extract frames using OpenCV.
3. Convert frames to ASCII art:

   * Grayscale brightness → ASCII character mapping.
   * RGB average per block → colored characters.
4. Use multiprocessing for batch frame conversion.
5. Compile ASCII images back into a video using `moviepy`.
6. Add original audio (if available).
7. Clean up temporary cache.

---

## Customization

* **ASCII Characters:** Modify `CHARS` string to change character style.
* **Resolution:** Adjust `WIDTH` and `FONT_SIZE`.
* **Output Path:** Change `output_path` in `save_ascii_video_from_diskcache`.
* **Chunk Size:** Modify `chunk_size` to balance memory & speed.

---

## Notes

* Works best with **short to medium-length videos** due to memory & processing constraints.
* Real-time colored terminal preview is not included but can be added for fun.

---

## Example

Input: YouTube video of your choice
Output: Colorful ASCII video retaining audio, ready to share or showcase.

---

🎉 Have fun turning any video into a retro ASCII masterpiece!



Do you want me to make that version too?
```
