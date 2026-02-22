import gradio as gr
import subprocess
import os
import re

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "std.rnnn")).replace("\\", "/")

def run_ffmpeg_cmd(command):
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        raise Exception(f"FFmpeg Error: {process.stderr}")
    return process.stderr

def get_safe_filename(original_path, custom_name, default_prefix):
    """Generates the output path based on user input or defaults."""
    ext = os.path.splitext(original_path)[1]
    base = os.path.splitext(os.path.basename(original_path))[0]
    
    if custom_name and custom_name.strip():
        # If user provides a name, use it. If it doesn't have an extension, add the original one.
        final_name = custom_name.strip() if custom_name.endswith(ext) else f"{custom_name.strip()}{ext}"
    else:
        final_name = f"{default_prefix}_{base}{ext}"
        
    return os.path.join(BASE_DIR, final_name)

# --- PROCESSING LOGIC ---

def ultra_process(file, hp_f, lp_f, gate, ratio, attack, release, warmth, custom_name):
    if not file: return None
    out_path = get_safe_filename(file, custom_name, "ultra")
    safe_model_path = MODEL_PATH.replace(":", "\\:").replace("'", "'\\\\''")
    
    filter_chain = (
        f"highpass=f={hp_f}, lowpass=f={lp_f}, "
        f"arnndn=model='{safe_model_path}', "
        f"agate=threshold={gate}dB:ratio={ratio}:attack={attack}:release={release}, "
        f"speechnorm=e=4:r=0.0005:p=0.9, "
        f"compand=points=-80/-900|-45/-15|-27/-9|0/-7|20/-7:gain={warmth}"
    )
    run_ffmpeg_cmd(["ffmpeg", "-y", "-i", file, "-af", filter_chain, out_path])
    return out_path

def standard_process(file, hp_freq, gate_thresh, custom_name):
    if not file: return None
    out_path = get_safe_filename(file, custom_name, "standard")
    filter_chain = f"highpass=f={hp_freq}, afftdn, agate=threshold={gate_thresh}dB"
    run_ffmpeg_cmd(["ffmpeg", "-y", "-i", file, "-af", filter_chain, out_path])
    return out_path

def split_audio(file, split_points_str, custom_prefix):
    if not file or not split_points_str: return None
    pts = [p.strip() for p in split_points_str.split(",") if p.strip()]
    
    # Use custom prefix or default to 'split'
    prefix = custom_prefix.strip() if custom_prefix.strip() else "split"
    out_pattern = os.path.join(BASE_DIR, f"{prefix}_%03d.wav")
    
    run_ffmpeg_cmd(["ffmpeg", "-y", "-i", file, "-f", "segment", "-segment_times", ",".join(pts), "-c", "copy", out_pattern])
    
    # Return all files matching the new prefix
    return [os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) 
            if f.startswith(f"{prefix}_") and f.endswith(".wav")]

# --- UI INTERFACE ---
with gr.Blocks(title="Ultra Studio Suite", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎙️ Ultra Studio Audio Suite")

    with gr.Tabs():
        # TAB 1: ULTRA CLEAN
        with gr.TabItem("1. Ultra AI Clean"):
            with gr.Row():
                with gr.Column():
                    u_in = gr.Audio(type="filepath", label="Input Audio")
                    u_rename = gr.Textbox(label="Rename Output (Optional)", placeholder="e.g. My_Clean_Audio")
                    with gr.Accordion("Advanced Settings", open=False):
                        u_hp = gr.Slider(50, 500, 100, label="Highpass Hz")
                        u_lp = gr.Slider(3000, 15000, 7500, label="Lowpass Hz")
                        u_gate = gr.Slider(-60, -10, -30, label="Threshold (dB)")
                        u_ratio = gr.Slider(1, 5, 2, label="Ratio")
                        u_attack = gr.Slider(0.1, 50, 5, label="Attack (ms)")
                        u_release = gr.Slider(10, 1000, 150, label="Release (ms)")
                    u_warm = gr.Slider(0, 15, 5, label="Output Warmth")
                    u_btn = gr.Button("Master with AI", variant="primary")
                with gr.Column():
                    u_out = gr.Audio(label="AI Result")

        # TAB 2: STANDARD CLEAN
        with gr.TabItem("2. Standard Clean"):
            with gr.Row():
                with gr.Column():
                    s_in = gr.Audio(type="filepath", label="Input Audio")
                    s_rename = gr.Textbox(label="Rename Output (Optional)", placeholder="e.g. Standard_Clean")
                    s_hp = gr.Slider(50, 500, 200, label="Highpass (Hz)")
                    s_gate = gr.Slider(-60, -10, -30, label="Gate (dB)")
                    s_btn = gr.Button("Process (No Model)", variant="secondary")
                with gr.Column():
                    s_out = gr.Audio(label="Standard Result")

        # TAB 3: PRECISION SPLITTER
        with gr.TabItem("3. Precision Splitter"):
            with gr.Row():
                with gr.Column():
                    split_in = gr.Audio(type="filepath", label="Master Playback")
                    split_rename = gr.Textbox(label="Prefix for Segments", placeholder="e.g. Chapter_One")
                    split_pts = gr.Textbox(label="Split Points (Seconds)", placeholder="00:02:00, 00:05:30, 120, 10, 45.5 ")
                    btn_run_split = gr.Button("Execute Split", variant="primary")
                with gr.Column():
                    split_out = gr.File(label="Exported Segments", file_count="multiple")

    # Bindings updated to include rename strings
    u_btn.click(ultra_process, [u_in, u_hp, u_lp, u_gate, u_ratio, u_attack, u_release, u_warm, u_rename], u_out)
    s_btn.click(standard_process, [s_in, s_hp, s_gate, s_rename], s_out)
    btn_run_split.click(split_audio, [split_in, split_pts, split_rename], split_out)

if __name__ == "__main__":
    demo.queue().launch(server_name="127.0.0.1", server_port=7860)