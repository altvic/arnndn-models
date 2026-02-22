import gradio as gr
import subprocess
import os

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "std.rnnn")).replace("\\", "/")


def run_ffmpeg_cmd(command):
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"FFmpeg Error: {process.stderr}")
        raise Exception(f"FFmpeg Error: {process.stderr}")
    return process.stderr


def get_safe_filename(original_path, custom_name, default_prefix, target_ext=None):
    ext = target_ext if target_ext else os.path.splitext(original_path)[1]
    base = os.path.splitext(os.path.basename(original_path))[0]

    if custom_name and custom_name.strip():
        name = custom_name.strip()
        final_name = name if name.endswith(ext) else f"{name}{ext}"
    else:
        final_name = f"{default_prefix}_{base}{ext}"

    return os.path.join(BASE_DIR, final_name)


def is_video(filepath):
    video_extensions = ['.mp4', '.mkv', '.mov', '.avi', '.flv', '.wmv']
    return os.path.splitext(filepath)[1].lower() in video_extensions


# --- PROCESSING LOGIC ---

def universal_compressor(file, intensity, custom_name):
    if not file:
        return None

    is_vid = is_video(file)
    target_ext = ".mp4" if is_vid else ".mp3"
    out_path = get_safe_filename(file, custom_name, "compressed", target_ext)

    if is_vid:
        crf = 18 + (intensity * 2)
        cmd = [
            "ffmpeg", "-y", "-i", file,
            "-c:v", "libx264",
            "-crf", str(int(crf)),
            "-preset", "slow",
            "-c:a", "aac",
            "-b:a", "96k",
            out_path
        ]
    else:
        bitrate = max(32, 320 - (intensity * 28))
        cmd = ["ffmpeg", "-y", "-i", file, "-ab", f"{int(bitrate)}k", out_path]

    run_ffmpeg_cmd(cmd)
    return out_path


def ultra_process(file, hp_f, lp_f, gate, ratio, attack, release, warmth, custom_name):
    if not file:
        return None

    is_vid = is_video(file)
    target_ext = ".mp4" if is_vid else os.path.splitext(file)[1]
    out_path = get_safe_filename(file, custom_name, "ultra_ai", target_ext)

    safe_model_path = MODEL_PATH.replace(":", "\\:").replace("'", "'\\\\''")

    filter_chain = (
        f"highpass=f={hp_f}, lowpass=f={lp_f}, "
        f"arnndn=model='{safe_model_path}', "
        f"agate=threshold={gate}dB:ratio={ratio}:attack={attack}:release={release}, "
        f"speechnorm=e=4:r=0.0005:p=0.9, "
        f"compand=points=-80/-900|-45/-15|-27/-9|0/-7|20/-7:gain={warmth}"
    )

    if is_vid:
        cmd = [
            "ffmpeg", "-y", "-i", file,
            "-af", filter_chain,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-map", "0:v:0",
            "-map", "0:a:0",
            out_path
        ]
    else:
        cmd = ["ffmpeg", "-y", "-i", file, "-af", filter_chain, out_path]

    run_ffmpeg_cmd(cmd)
    return out_path


def standard_process(file, hp_freq, fft_nr, gate_thresh, custom_name):
    if not file:
        return None

    out_path = get_safe_filename(file, custom_name, "standard")
    filter_chain = f"highpass=f={hp_freq}, afftdn=nr={fft_nr}, agate=threshold={gate_thresh}dB"

    run_ffmpeg_cmd(["ffmpeg", "-y", "-i", file, "-af", filter_chain, out_path])
    return out_path


def split_audio(file, split_points_str, custom_prefix):
    if not file or not split_points_str:
        return None

    pts = [p.strip() for p in split_points_str.split(",") if p.strip()]
    prefix = custom_prefix.strip() if custom_prefix.strip() else "split"
    out_pattern = os.path.join(BASE_DIR, f"{prefix}_%03d.wav")

    run_ffmpeg_cmd([
        "ffmpeg", "-y", "-i", file,
        "-f", "segment",
        "-segment_times", ",".join(pts),
        "-c", "copy",
        out_pattern
    ])

    return [
        os.path.join(BASE_DIR, f)
        for f in os.listdir(BASE_DIR)
        if f.startswith(f"{prefix}_") and f.endswith(".wav")
    ]


# FIXED SIGNATURE (4 args now)
def extract_audio_advanced(video_file, fmt, bitrate, channels):
    if not video_file:
        return None

    out_path = get_safe_filename(video_file, "", "extracted", target_ext=fmt)

    cmd = ["ffmpeg", "-y", "-i", video_file, "-vn"]

    ch_val = "1" if channels == "Mono" else "2"
    cmd += ["-ac", ch_val]

    if fmt == ".wav":
        cmd += ["-acodec", "pcm_s16le"]
    elif fmt == ".mp3":
        cmd += ["-acodec", "libmp3lame", "-ab", bitrate]
    elif fmt == ".m4a":
        cmd += ["-acodec", "aac", "-ab", bitrate]

    cmd.append(out_path)

    run_ffmpeg_cmd(cmd)
    return out_path


def merge_video_audio(video_file, audio_file, custom_name, use_compression, crf_val):
    if not video_file or not audio_file:
        return None

    out_path = get_safe_filename(video_file, custom_name, "merged", target_ext=".mp4")

    cmd = ["ffmpeg", "-y", "-i", video_file, "-i", audio_file]

    if use_compression:
        cmd += ["-c:v", "libx264", "-crf", str(crf_val), "-preset", "medium"]
    else:
        cmd += ["-c:v", "copy"]

    cmd += [
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        out_path
    ]

    run_ffmpeg_cmd(cmd)
    return out_path


# --- UI ---
with gr.Blocks(title="Ultra Studio Suite") as demo:
    gr.Markdown("# 🎙️ Ultra Studio Audio Suite")

    with gr.Tabs():

        with gr.TabItem("1. Ultra AI Clean"):
            with gr.Row():
                with gr.Column():
                    u_in = gr.File(label="Input Audio or Video")
                    u_rename = gr.Textbox(label="Rename Output (Optional)")
                    with gr.Accordion("Advanced AI Settings", open=False):
                        u_hp = gr.Slider(50, 500, 100, label="Highpass Hz")
                        u_lp = gr.Slider(3000, 15000, 7500, label="Lowpass Hz")
                        u_gate = gr.Slider(-60, -10, -30, label="Gate Threshold (dB)")
                        u_ratio = gr.Slider(1, 5, 2, label="Gate Ratio")
                        u_attack = gr.Slider(0.1, 50, 5, label="Attack (ms)")
                        u_release = gr.Slider(10, 1000, 150, label="Release (ms)")
                    u_warm = gr.Slider(0, 15, 5, label="Warmth/Gain")
                    u_btn = gr.Button("Master with AI", variant="primary")
                with gr.Column():
                    u_out_vid = gr.Video(label="AI Result (Video)", interactive=False)
                    u_out_aud = gr.Audio(label="AI Result (Audio)")

        with gr.TabItem("2. Standard Clean"):
            with gr.Row():
                with gr.Column():
                    s_in = gr.Audio(type="filepath", label="Input Audio")
                    s_rename = gr.Textbox(label="Rename Output")
                    s_hp = gr.Slider(50, 500, 200, label="Highpass (Hz)")
                    s_fft = gr.Slider(1, 48, 12, step=1, label="FFT Noise Reduction (dB)")
                    s_gate = gr.Slider(-60, -10, -30, label="Gate (dB)")
                    s_btn = gr.Button("Process (Standard)", variant="secondary")
                with gr.Column():
                    s_out = gr.Audio(label="Result")

        with gr.TabItem("3. Precision Splitter"):
            with gr.Row():
                with gr.Column():
                    split_in = gr.Audio(type="filepath", label="Master Playback")
                    split_rename = gr.Textbox(label="Prefix for Segments")
                    split_pts = gr.Textbox(label="Split Points (Seconds)", placeholder="Input Format: 120, 00:02:00, 00:05:30, 00:39")
                    btn_run_split = gr.Button("Execute Split")
                with gr.Column():
                    split_out = gr.File(label="Segments", file_count="multiple")
                    
        with gr.TabItem("4. Video Tools"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🔊 Extraction")
                    v_extract_in = gr.Video(label="Source Video")
                    with gr.Row():
                        v_ext_fmt = gr.Dropdown([".wav", ".mp3", ".m4a"], value=".wav", label="Format")
                        v_ext_bit = gr.Dropdown(["128k", "192k", "320k"], value="192k", label="Bitrate")
                        v_ext_ch = gr.Radio(["Mono", "Stereo"], value="Stereo", label="Channels")
                    btn_extract = gr.Button("Extract Audio")
                    v_extract_preview = gr.Audio(label="Extracted Audio Preview")
                    
                    gr.Markdown("---")
                    gr.Markdown("### 🎬 Merger")
                    
                    v_merge_vid = gr.Video(label="Source Video")
                    v_merge_aud = gr.Audio(type="filepath", label="Source Audio")
                    with gr.Accordion("Compression Options", open=False):
                        v_compress_toggle = gr.Checkbox(label="Enable Video Compression", value=False)
                        v_crf = gr.Slider(18, 35, 23, step=1, label="CRF Level (Higher = Smaller File, lower quality)")
                        gr.Markdown("*Note: 18 is visually lossless, 23 is default, 30+ is heavy compression.*")
                    
                    v_merge_rename = gr.Textbox(label="Rename Merged Video")
                    btn_merge = gr.Button("Merge & Replace Audio", variant="primary")
                with gr.Column():
                    v_out_file = gr.File(label="Download")
                    v_out_preview = gr.Video(label="Preview")                   
                    
        with gr.TabItem("5. Universal Compressor"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📉 Smart Compression Engine")
                    c_in = gr.File(label="Upload Video or Audio")
                    c_intensity = gr.Slider(1, 10, 5, step=1, label="Compression Intensity (10 = Smallest File)")
                    c_rename = gr.Textbox(label="Rename Output (Optional)")
                    c_btn = gr.Button("Compress File", variant="primary")
                with gr.Column():
                    c_out_file = gr.File(label="Compressed Result")
                    gr.Markdown("*Note: Video outputs as .mp4, Audio outputs as .mp3*")

    # --- BINDINGS ---
    u_btn.click(ultra_process,
                [u_in, u_hp, u_lp, u_gate, u_ratio, u_attack, u_release, u_warm, u_rename],
                u_out_vid).then(lambda x: x, u_out_vid, u_out_aud)

    s_btn.click(standard_process,
                [s_in, s_hp, s_fft, s_gate, s_rename],
                s_out)

    btn_run_split.click(split_audio,
                        [split_in, split_pts, split_rename],
                        split_out)

    btn_extract.click(extract_audio_advanced,
                      [v_extract_in, v_ext_fmt, v_ext_bit, v_ext_ch],
                      v_extract_preview)

    btn_merge.click(merge_video_audio,
                    [v_merge_vid, v_merge_aud, v_merge_rename, v_compress_toggle, v_crf],
                    v_out_file)

    btn_merge.click(lambda x: x, v_out_file, v_out_preview)

    c_btn.click(universal_compressor,
                [c_in, c_intensity, c_rename],
                c_out_file)


if __name__ == "__main__":
    demo.queue().launch(
        server_name="127.0.0.1",
        server_port=7860,
        theme=gr.themes.Soft()
    )