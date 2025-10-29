# WiSeeYou: Privacy-Preserving WiFi Gesture Recognition

WiSeeYou is an open-source privacy-focused gesture control system that leverages WiFi Channel State Information (CSI) and embedded machine learning to recognize hand gestures in real time, without the need for cameras, microphones, or specialized sensors.

---

## Overview

WiSeeYou turns commodity ESP32 hardware into a powerful sensing device by analyzing subtle changes in WiFi signals caused by hand or body movements. This enables gesture detection even in low-light, obstructed, or non-line-of-sight scenarios—preserving user privacy and lowering hardware costs.

**Key Features:**
- No cameras, microphones, or wearables required
- Works in the dark and through walls
- Real-time, local detection (no cloud dependency)
- Runs on affordable ESP32 hardware
- Visual feedback via LEDs and Python GUI/web dashboard

---

## Theory & Approach

### WiFi Sensing and CSI

WiFi devices transmit signals across multiple frequencies (subcarriers). As these signals bounce off moving objects like hands or bodies, the wireless channel changes. CSI captures these fine-grained channel properties (amplitude and phase) for each packet and subcarrier. By analyzing CSI over time, we can distinguish unique gesture patterns (e.g., swipe vs punch) [web:119][web:118].

### Machine Learning Model

WiSeeYou uses a **Random Forest classifier** trained on a large open-source Chinese gesture dataset (125,000+ samples). The model learns to classify CSI time-series profiles for different gestures. All processing and inference happen locally.

### Hardware & Components

- **ESP32 Dev Board:** Collects CSI, runs ML inference, controls LEDs, communicates with PC
- **LEDs:** Blue = swipe, Red = punch
- **Python Tools:** Data logging, visualization, GUI dashboard

---

## Repository Structure

```
/
│   LICENSE
│   README.md
│
├───.vscode
│       settings.json
│
├───dataset
│   ├───frontandafter
│   │       frontandafter.csv
│   │       frontandafter1.csv
│   │       frontandafter2.csv
│   │       frontandafter3.csv
│   │       frontandafter4.csv
│   │       frontandafter5.csv
│   │       frontandafter6.csv
│   │       frontandafter7.csv
│   │
│   ├───leftandright
│   │       leftandright.csv
│   │       leftandright1.csv
│   │       leftandright2.csv
│   │       leftandright3.csv
│   │       leftandright4.csv
│   │       leftandright5.csv
│   │       leftandright6.csv
│   │       leftandright7.csv
│   │
│   └───upanddown
│           upanddown.csv
│           upanddown1.csv
│           upanddown2.csv
│           upanddown3.csv
│           upanddown4.csv
│           upanddown5.csv
│           upanddown6.csv
│           upanddown7.csv
│
├───realtime
│       3_realtime_detection.py
│
├───training
│       1_process_dataset.py
│       2_train_model.py
│
└───web_interface
    │   app.py
    │
    ├───static
    │       style.css
    │
    └───templates
            index.html
```

---

## Usage Instructions

1. **Preprocess Your Dataset**
   ```
   python training/1_process_dataset.py
   ```
   This step cleans and prepares the CSI data for model training.

2. **Train the Model**
   ```
   python training/2_train_model.py
   ```
   This trains the Random Forest classifier on the processed data. Output: trained model file.

3. **Run Realtime Detection**
   ```
   python realtime/3_realtime_detection.py
   ```
   Detect gestures live with your ESP32 and display the output.

4. **Launch Web Dashboard**
   ```
   python web_interface/app.py
   ```
   View predictions and analytics in a browser-based GUI.

---

## Dataset

- Model is trained on a publicly available Chinese WiFi gesture dataset (~125k samples).
- To use your own files, log CSI using `log_csi.py` and place them in the appropriate folder.
- Supported formats: Clean CSV time-series with amplitude values.

---

## License

MIT License. See LICENSE for full details.

---

## References

- [WiSee Project, U. Washington](https://wisee.cs.washington.edu)  
- [WiFi Sensing: Theory & Applications](https://en.wikipedia.org/wiki/Channel_state_information)  
- [WiFi-based Multi-User Gesture Recognition](https://ieeexplore.ieee.org/document/8908808)  
- [Original Dataset Source – Chinese WiFi Gesture Recognition](link-to-dataset-if-public)

---

## Contributors

- M Arjun
- S Hariram
- Chappidi Venkata Vigneshwara Reddy
- Krish S
- Kunal Gupta
- Garikapati Hareesh

---

## Get Started

Clone the repo, follow the usage steps, and unleash WiFi-powered gesture sensing!

```
git clone https://github.com/yourusername/wiseeyou.git
cd wiseeyou
```


[1](https://ieeexplore.ieee.org/ielaam/7755/9346168/8908808-aam.pdf)
[2](https://pmc.ncbi.nlm.nih.gov/articles/PMC6165566/)
[3](https://dl.acm.org/doi/10.1145/3463504)
[4](https://arxiv.org/pdf/2106.00857.pdf)
[5](https://www.youtube.com/watch?v=VZ7Nz942yAY)
[6](https://wisee.cs.washington.edu)
[7](https://raghavhv.wordpress.ncsu.edu/files/2018/06/mobisys18-31-hampapur.pdf)
