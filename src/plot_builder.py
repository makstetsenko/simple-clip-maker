import librosa
import numpy as np
import matplotlib.pyplot as plt
import src.peaks_detector as peaks_detector

# Plot the normalized energy and detected peaks
def plot_energy_with_peaks(norm_energy, peaks, sr, hop_length, audio_file_path):
    times = librosa.frames_to_time(np.arange(len(norm_energy)), sr=sr, hop_length=hop_length)

    plt.figure(figsize=(12, 4))
    plt.plot(times, norm_energy, label="Normalized Energy")
    plt.plot(times[peaks], norm_energy[peaks], "rx", label="Peaks")
    plt.title("Energy with Detected Peaks")
    plt.xlabel("Time (s)")
    plt.ylabel("Normalized Energy")
    plt.legend()
    plt.tight_layout()
    
    # plt.savefig(output_file_name)
    plt.show()


def build_plot(audio_file_path):
    criteria=peaks_detector.GetPeaksCriteria(
            peaks_distance=15,
            peaks_prominence=0.5,
            peaks_height=[0, 1],
            hop_length=512
    )
    
    response = peaks_detector.get_peaks_with_sample_rate_with_normalized_energy_with_amplitude_values(audio_file_path, criteria)
    
    plot_energy_with_peaks(response.norm_energy, response.peaks, response.sample_rate, criteria.hop_length, audio_file_path)
