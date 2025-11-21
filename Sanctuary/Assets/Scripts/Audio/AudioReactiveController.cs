using UnityEngine;
using System.Collections.Generic;

namespace Sanctuary.Audio
{
    /// <summary>
    /// Audio reactive controller for bioluminescent effects
    /// Analyzes microphone input and drives shader parameters
    /// </summary>
    [RequireComponent(typeof(AudioSource))]
    public class AudioReactiveController : MonoBehaviour
    {
        [Header("Microphone Settings")]
        [SerializeField] private bool startOnAwake = true;
        [SerializeField] private string selectedMicrophone = null; // null = default microphone
        [SerializeField] private int sampleRate = 44100;
        [SerializeField] private int fftSize = 256; // Power of 2: 64, 128, 256, 512, 1024, 2048

        [Header("Analysis Settings")]
        [SerializeField] private float sensitivity = 1.0f;
        [SerializeField] private float smoothing = 0.1f; // Lower = more responsive
        [SerializeField] private float threshold = 0.01f; // Noise gate

        [Header("Frequency Bands")]
        [SerializeField] private int frequencyBands = 8; // 8 frequency bands
        [SerializeField] private bool useLogarithmicBands = true;

        [Header("Debug")]
        [SerializeField] private bool showDebugGUI = false;

        // Audio components
        private AudioSource audioSource;
        private AudioClip microphoneClip;
        private float[] samples;
        private float[] spectrum;

        // Analyzed data
        private float[] bandValues;
        private float[] bandBuffered;
        private float[] bufferDecrease;

        // Output values
        private float volume = 0f;
        private float volumeBuffered = 0f;
        private bool isVoiceActive = false;
        private float voiceIntensity = 0f;

        // Constants
        private readonly float[] FreqLimits = { 60, 250, 500, 2000, 4000, 6000, 8000, 16000 };

        public bool IsVoiceActive => isVoiceActive;
        public float VoiceIntensity => voiceIntensity;
        public float Volume => volume;
        public float[] FrequencyBands => bandValues;

        private void Awake()
        {
            audioSource = GetComponent<AudioSource>();

            // Initialize arrays
            samples = new float[fftSize];
            spectrum = new float[fftSize];
            bandValues = new float[frequencyBands];
            bandBuffered = new float[frequencyBands];
            bufferDecrease = new float[frequencyBands];
        }

        private void Start()
        {
            if (startOnAwake)
            {
                StartListening();
            }
        }

        private void Update()
        {
            if (microphoneClip == null || !Microphone.IsRecording(selectedMicrophone))
                return;

            // Get audio data
            GetAudioData();

            // Analyze audio
            AnalyzeAudio();

            // Update voice detection
            UpdateVoiceDetection();
        }

        /// <summary>
        /// Start listening to microphone
        /// </summary>
        public void StartListening()
        {
            #if UNITY_WEBGL
            Debug.LogWarning("[AudioReactive] Microphone not supported on WebGL");
            return;
            #endif

            // Request microphone permission (on mobile platforms)
            #if UNITY_ANDROID || UNITY_IOS
            if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
            {
                Application.RequestUserAuthorization(UserAuthorization.Microphone);
            }
            #endif

            // Get available microphones
            string[] devices = Microphone.devices;

            if (devices.Length == 0)
            {
                Debug.LogError("[AudioReactive] No microphone devices found");
                return;
            }

            // Use specified microphone or default
            if (string.IsNullOrEmpty(selectedMicrophone) || !System.Array.Exists(devices, d => d == selectedMicrophone))
            {
                selectedMicrophone = devices[0];
            }

            Debug.Log($"[AudioReactive] Starting microphone: {selectedMicrophone}");

            // Start recording
            microphoneClip = Microphone.Start(selectedMicrophone, true, 1, sampleRate);

            // Wait for microphone to start
            int timeoutFrames = 100;
            while (!(Microphone.GetPosition(selectedMicrophone) > 0) && timeoutFrames > 0)
            {
                timeoutFrames--;
            }

            if (timeoutFrames == 0)
            {
                Debug.LogError("[AudioReactive] Microphone timeout");
                return;
            }

            // Setup audio source
            audioSource.clip = microphoneClip;
            audioSource.loop = true;
            audioSource.Play();

            Debug.Log("[AudioReactive] Listening started");
        }

        /// <summary>
        /// Stop listening to microphone
        /// </summary>
        public void StopListening()
        {
            if (Microphone.IsRecording(selectedMicrophone))
            {
                Microphone.End(selectedMicrophone);
                Debug.Log("[AudioReactive] Listening stopped");
            }

            if (audioSource != null && audioSource.isPlaying)
            {
                audioSource.Stop();
            }

            isVoiceActive = false;
            voiceIntensity = 0f;
        }

        /// <summary>
        /// Get audio data from audio source
        /// </summary>
        private void GetAudioData()
        {
            audioSource.GetOutputData(samples, 0); // Get waveform data
            audioSource.GetSpectrumData(spectrum, 0, FFTWindow.BlackmanHarris); // Get frequency data
        }

        /// <summary>
        /// Analyze audio data
        /// </summary>
        private void AnalyzeAudio()
        {
            // Calculate volume (RMS)
            float sum = 0f;
            for (int i = 0; i < samples.Length; i++)
            {
                sum += samples[i] * samples[i];
            }

            volume = Mathf.Sqrt(sum / samples.Length) * sensitivity;

            // Smooth volume
            volumeBuffered = Mathf.Lerp(volumeBuffered, volume, smoothing);

            // Analyze frequency bands
            AnalyzeFrequencyBands();
        }

        /// <summary>
        /// Analyze frequency spectrum into bands
        /// </summary>
        private void AnalyzeFrequencyBands()
        {
            int spectrumIndex = 0;
            int sampleCount = 1;
            int power = 0;

            for (int i = 0; i < frequencyBands; i++)
            {
                float average = 0f;

                if (useLogarithmicBands)
                {
                    // Logarithmic distribution (more resolution in low frequencies)
                    sampleCount = (int)Mathf.Pow(2, i) * 2;

                    if (i == frequencyBands - 1)
                    {
                        sampleCount += 2;
                    }

                    for (int j = 0; j < sampleCount; j++)
                    {
                        if (spectrumIndex < spectrum.Length)
                        {
                            average += spectrum[spectrumIndex] * (spectrumIndex + 1);
                            spectrumIndex++;
                        }
                    }

                    average /= spectrumIndex;
                }
                else
                {
                    // Linear distribution
                    int bandSize = spectrum.Length / frequencyBands;
                    int startIndex = i * bandSize;
                    int endIndex = Mathf.Min((i + 1) * bandSize, spectrum.Length);

                    for (int j = startIndex; j < endIndex; j++)
                    {
                        average += spectrum[j];
                    }

                    average /= (endIndex - startIndex);
                }

                // Store band value
                bandValues[i] = average * sensitivity;

                // Buffer for smoother visualization
                if (bandValues[i] > bandBuffered[i])
                {
                    bandBuffered[i] = bandValues[i];
                    bufferDecrease[i] = 0.005f;
                }

                if (bandValues[i] < bandBuffered[i])
                {
                    bandBuffered[i] -= bufferDecrease[i];
                    bufferDecrease[i] *= 1.2f;
                }
            }
        }

        /// <summary>
        /// Update voice detection
        /// </summary>
        private void UpdateVoiceDetection()
        {
            // Check if volume exceeds threshold
            isVoiceActive = volumeBuffered > threshold;

            // Calculate voice intensity (0-1)
            if (isVoiceActive)
            {
                // Focus on mid-range frequencies (human voice: 300-3400 Hz)
                float midRangeEnergy = 0f;
                for (int i = 1; i < Mathf.Min(4, frequencyBands); i++)
                {
                    midRangeEnergy += bandBuffered[i];
                }

                voiceIntensity = Mathf.Clamp01(midRangeEnergy * 2f);
            }
            else
            {
                voiceIntensity = Mathf.Lerp(voiceIntensity, 0f, smoothing);
            }
        }

        /// <summary>
        /// Get buffered frequency band value
        /// </summary>
        public float GetBand(int index)
        {
            if (index >= 0 && index < bandBuffered.Length)
            {
                return bandBuffered[index];
            }

            return 0f;
        }

        /// <summary>
        /// Get average of all frequency bands
        /// </summary>
        public float GetAverageBand()
        {
            float sum = 0f;
            foreach (float band in bandBuffered)
            {
                sum += band;
            }

            return sum / bandBuffered.Length;
        }

        private void OnDestroy()
        {
            StopListening();
        }

        private void OnDisable()
        {
            StopListening();
        }

#if UNITY_EDITOR
        private void OnGUI()
        {
            if (!showDebugGUI) return;

            GUILayout.BeginArea(new Rect(10, 10, 300, 400));

            GUILayout.Label($"Voice Active: {isVoiceActive}");
            GUILayout.Label($"Voice Intensity: {voiceIntensity:F2}");
            GUILayout.Label($"Volume: {volumeBuffered:F3}");

            GUILayout.Space(10);
            GUILayout.Label("Frequency Bands:");

            for (int i = 0; i < frequencyBands; i++)
            {
                float value = bandBuffered[i];
                GUILayout.Label($"Band {i}: {value:F3}");

                // Visual bar
                Rect barRect = GUILayoutUtility.GetRect(250, 20);
                GUI.DrawTexture(new Rect(barRect.x, barRect.y, barRect.width * value * 10f, barRect.height), Texture2D.whiteTexture);
            }

            GUILayout.EndArea();
        }

        [ContextMenu("Start Listening")]
        private void EditorStartListening()
        {
            StartListening();
        }

        [ContextMenu("Stop Listening")]
        private void EditorStopListening()
        {
            StopListening();
        }
#endif
    }
}
