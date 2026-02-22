<b><h1>🎙️ Ultra Studio Audio Suite</h1></b><br>
A high-performance Gradio-based professional audio & video processing suite powered by FFmpeg and Neural Network denoising (ARNNDN).
<br>
Ultra Studio Suite transforms raw recordings, interviews, podcasts, and videos into studio-grade productions using intelligent filter chains, mastering controls, precision splitting, and smart compression.
<br> std.rnnn is originally bundled with Xiph RNNoise implementation. others are created by Gregor Richards.
<br><br>
<h3><b>🌟 Key Features</b></h3>

<ol><li> Ultra AI Clean (Neural Processing): The flagship module uses a Recurrent Neural Network (RNN) to intelligently separate human speech from background noise.

<ol><li>Intelligent Speech Isolation</li>  
<ul>
<li>Deep Denoising: Powered by the std.rnnn model to eliminate fans, traffic, and static.</li>
<li>Granular Mastering: Full control over EQ (Highpass/Lowpass), Gate (Threshold/Ratio/Attack/Release), and Studio Warmth.</li>
<li>Speech Normalization: Integrated speechnorm and compand filters to ensure consistent volume levels.</li>
</ul>
<li>Advanced Features</li>
<ul>
  <li>Highpass filter:</strong> Rumble removal (low-end cleanup)</li>
  <li>Lowpass filter:</strong> Harshness control (high-end smoothing)</li>
  <li>Noise gate:</strong> Includes Threshold, Ratio, Attack, and Release controls</li>
  <li>Speech normalization:</strong> Consistent volume levels throughout the track</li>
  <li>Dynamic companding:</strong> Intelligent compression and expansion</li>
  <li>Adjustable warmth:</strong> Output gain shaping for a richer sound</li>
</ul>
<li>🎬 Works on BOTH Audio & Video</li>
<ul>
  <li>Audio files → processed audio output</li>
  <li>Video files → keeps original video stream, replaces processed audio</li>
  <li>Video output encoded to AAC (192k)</li>
</ul>
</ol>
</li>

<br><br>

<li> Standard Clean (Mathematical Filtering): A lightweight, model-free cleaning utility for quick processing.

<ol><li>⚡ Features</li>  
<ul>
<li>FFT De-noise: Uses Fast Fourier Transform (afftdn) to subtract constant noise profiles</li>
<li>Highpass Filtering: Removes low-end rumble and mechanical vibrations.</li>
<li>Audio Gating: Eliminates "dead air" noise between sentences</li>
</ul>
<li>Best For</li>
<ul>
  <li>Light hiss removal</li>
  <li>Quick cleanup</li>
  <li>Low CPU environments</li>
</ul>
</ol>
</li>


<br><br>

<li> Precision Splitter: Frame-accurate audio segmentation using FFmpeg's lossless stream copy muxer.

<ol><li>✂ Capabilities</li>  
<ul>
<li>Manual time split points (supports seconds or HH:MM:SS)</li>
<li>Batch export large files instantly</li>
<li>Lossless segmentation (no re-encoding)</li>
<li>Custom prefix naming</li>
</ul>
</ol>
</li>


<br><br>

<li>Universal Compressor: Smart compression engine for reducing file sizes.

<ol><li>🎥 Video Compression</li>  
<ul>
<li>H.264 encoding</li>
<li>Adjustable intensity (1–10)</li>
<li>CRF scaling logic</li>
<li>Preset: slow (better compression efficiency)</li>
<li>Audio re-encoded to AAC 96k</li>
</ul>
<li>🎧 Audio Compression</li>
<ul>
  <li>Outputs as .mp3</li>
  <li>Adaptive bitrate scaling</li>
  <li>Minimum 32k safeguard</li>
  <li>Ideal for upload size limits</li>
</ul>
</ol>
</li>

<br><br>

<li> Advanced Video Tools: A professional video/audio utility suite.

<ol>
  <li>🔊 Advanced Audio Extraction: Extract audio from video with format control</li>  
<ul>
<li>Output formats:
  <ul>
    <li>.wav (PCM 16-bit)</li>
    <li>.mp3</li>
    <li>.m4a</li>
  </ul>
</li>
<li>Bitrate selection (128k / 192k / 320k)</li>
<li>Channel selection (Mono / Stereo)</li>

<li>Best For</li>
<ul>
  <li>Podcast extraction</li>
  <li>YouTube audio repurposing</li>
  <li>Dialogue isolation</li>
</ul>
</ul>
<li>🎬 Video + Audio Merger: Replace a video's soundtrack with new audio.</li>
<ul>
  <li>Options:
  <ul>
  <li>Keep original video quality (stream copy)</li>
  <li>Enable video compression
  <ul>
  <li>H.264 encoding</li>
  <li>Adjustable CRF level</li>
  <li>Preset-based compression control</li>
  </ul>
  </li>
  <li>AAC 192k audio output</li>
  <li>Auto-sync with -shortest</li>
  </ul>
  </li>
  
  <li>Ideal for
   <ul>
  <li>Replacing narration</li>
  <li>Adding mastered soundtracks</li>
  <li>Re-dubbing content</li>
  </ul>
  </li>
</li>

</ol>
<br><br>
<h3><b>🛠️ Installation & Setup</b></h3>

<h4><b>Prerequisites</b></h4>
<ul>
  <li>Python 3.8+</li>
  <li>FFmpeg: Must be installed and added to your System PATH.</li>
  <li> ARNNDN Model: Place the std.rnnn model file in the project root directory.</li>
</ul>
  
<br>
<h4><b><b>Quick Start</b></b></h4>
<ol> <li>Clone the repository:
<ul><li>git clone https://github.com/your-username/ultra-studio-suite.git</li>
<li>cd ultra-studio-suite</li>
</ul></li>
<li>Install dependencies:
<ul><li>cd ultra-studio-suite</li>
<li>pip install gradio</li>
</ul></li>
<li>Launch the Suite:
<ul>
<li>python app.py</li>
</ul></li>
<li>Access the UI:
  <ul><li>Open http://127.0.0.1:7860 in your browser.</li>
    </ul></li>
</ol>
<br>
<h4><b>Summary of Path Dependencies</b></h4>
<ul>
<li><b>Item >	Dependency Type  >	Requirement</b></li> <br>
<li> Project Folder >	Dynamic >	Can be moved anywhere.</li> <br>
<li>Model File >	Name-locked >	Must be named std.rnnn and sit next to app.py.</li><br>
<li>Output Audio >	Local	> Always saved to the script's location.</li><br>
<li>FFmpeg >	System-locked	> Must be accessible via the command line/terminal.</li>
</ul>

<br>
<h3><b>🎛️ Technical Workflow</b></h3>
The suite processes audio by piping it through complex FFmpeg filtergraphs.<br><br> A typical Ultra Clean string looks like this:

$$\text{Input} \rightarrow \text{Highpass} \rightarrow \text{Lowpass} \rightarrow \text{ARNNDN} \rightarrow \text{Agate} \rightarrow \text{Speechnorm} \rightarrow \text{Compand} \rightarrow \text{Output}$$

<br>
<h3><b>Renaming Logic</b></h3>
Across all tabs, you have the option to define custom output names.
- Single Files: If you input Interview_Final, the system exports Interview_Final.wav.Split
- Segments: If you input Segment, the system exports Segment_000.wav, Segment_001.wav, etc.

<br><br>
<h3><b>📜 Open Source & License</b></h3>

This project is Open Source and distributed under the MIT License.
<br><br><br>
<b>MIT License Summary:</b>

✅ Commercial Use: You can use this tool for paid audio production.

✅ Modification: You can change the code to fit your specific studio needs.

✅ Distribution: You can share your modified version of this suite.<br>

⚠️ Liability: The software is provided "as is," without warranty of any kind.
<br><br><br>
Note: This project utilizes FFmpeg, which is licensed under LGPL/GPL. Please ensure your use of FFmpeg complies with their respective licensing terms.
