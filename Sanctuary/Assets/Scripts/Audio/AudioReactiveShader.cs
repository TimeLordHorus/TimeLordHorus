using UnityEngine;
using Sanctuary.Audio;

namespace Sanctuary.Avatar
{
    /// <summary>
    /// Links audio reactivity to shader parameters
    /// Specifically designed for bioluminescent jellyfish avatar
    /// </summary>
    [RequireComponent(typeof(Renderer))]
    public class AudioReactiveShader : MonoBehaviour
    {
        [Header("Audio Source")]
        [SerializeField] private AudioReactiveController audioController;
        [SerializeField] private bool autoFindAudioController = true;

        [Header("Shader Properties")]
        [SerializeField] private string glowIntensityProperty = "_GlowIntensity";
        [SerializeField] private string glowPulseSpeedProperty = "_GlowPulseSpeed";
        [SerializeField] private string glowPulseAmplitudeProperty = "_GlowPulseAmplitude";
        [SerializeField] private string emissionColorProperty = "_EmissionColor";

        [Header("Reactivity Settings")]
        [SerializeField] private float baseGlowIntensity = 1.0f;
        [SerializeField] private float maxGlowIntensity = 3.0f;
        [SerializeField] private float basePulseSpeed = 1.0f;
        [SerializeField] private float maxPulseSpeed = 5.0f;
        [SerializeField] private float basePulseAmplitude = 0.3f;
        [SerializeField] private float maxPulseAmplitude = 0.8f;

        [Header("Color Modulation")]
        [SerializeField] private bool modulateColor = true;
        [SerializeField] private Color baseEmissionColor = new Color(0f, 1f, 1f); // Cyan
        [SerializeField] private Color activeEmissionColor = new Color(0f, 1f, 0.5f); // Green-cyan
        [SerializeField] private float colorTransitionSpeed = 2.0f;

        [Header("Frequency-Based Effects")]
        [SerializeField] private bool useFrequencyBands = true;
        [SerializeField] private int lowFrequencyBand = 0; // Bass
        [SerializeField] private int midFrequencyBand = 2; // Mid (voice)
        [SerializeField] private int highFrequencyBand = 6; // Highs

        // Components
        private Renderer meshRenderer;
        private MaterialPropertyBlock propertyBlock;

        // State
        private float currentGlowIntensity;
        private float currentPulseSpeed;
        private float currentPulseAmplitude;
        private Color currentEmissionColor;

        private void Awake()
        {
            meshRenderer = GetComponent<Renderer>();
            propertyBlock = new MaterialPropertyBlock();

            // Get renderer's current property block
            meshRenderer.GetPropertyBlock(propertyBlock);

            // Initialize current values from shader
            currentGlowIntensity = baseGlowIntensity;
            currentPulseSpeed = basePulseSpeed;
            currentPulseAmplitude = basePulseAmplitude;
            currentEmissionColor = baseEmissionColor;
        }

        private void Start()
        {
            // Auto-find audio controller
            if (autoFindAudioController && audioController == null)
            {
                audioController = FindObjectOfType<AudioReactiveController>();

                if (audioController == null)
                {
                    Debug.LogWarning("[AudioReactiveShader] No AudioReactiveController found");
                }
            }
        }

        private void Update()
        {
            if (audioController == null || !audioController.enabled) return;

            // Update shader parameters based on audio
            UpdateShaderParameters();
        }

        /// <summary>
        /// Update shader parameters based on audio input
        /// </summary>
        private void UpdateShaderParameters()
        {
            // Get audio intensity
            float voiceIntensity = audioController.VoiceIntensity;
            bool isActive = audioController.IsVoiceActive;

            // Calculate target values
            float targetGlowIntensity;
            float targetPulseSpeed;
            float targetPulseAmplitude;
            Color targetEmissionColor;

            if (isActive)
            {
                // Voice is active - increase glow based on intensity
                targetGlowIntensity = Mathf.Lerp(baseGlowIntensity, maxGlowIntensity, voiceIntensity);
                targetPulseSpeed = Mathf.Lerp(basePulseSpeed, maxPulseSpeed, voiceIntensity);
                targetPulseAmplitude = Mathf.Lerp(basePulseAmplitude, maxPulseAmplitude, voiceIntensity);

                if (modulateColor)
                {
                    targetEmissionColor = Color.Lerp(baseEmissionColor, activeEmissionColor, voiceIntensity);
                }
                else
                {
                    targetEmissionColor = baseEmissionColor;
                }

                // Frequency-based modulation
                if (useFrequencyBands && audioController.FrequencyBands != null)
                {
                    float lowFreq = audioController.GetBand(lowFrequencyBand);
                    float midFreq = audioController.GetBand(midFrequencyBand);
                    float highFreq = audioController.GetBand(highFrequencyBand);

                    // Pulse speed influenced by high frequencies
                    targetPulseSpeed += highFreq * 2f;

                    // Pulse amplitude influenced by low frequencies
                    targetPulseAmplitude += lowFreq * 0.2f;
                }
            }
            else
            {
                // Voice is not active - return to base values
                targetGlowIntensity = baseGlowIntensity;
                targetPulseSpeed = basePulseSpeed;
                targetPulseAmplitude = basePulseAmplitude;
                targetEmissionColor = baseEmissionColor;
            }

            // Smooth transition to target values
            currentGlowIntensity = Mathf.Lerp(currentGlowIntensity, targetGlowIntensity, Time.deltaTime * colorTransitionSpeed);
            currentPulseSpeed = Mathf.Lerp(currentPulseSpeed, targetPulseSpeed, Time.deltaTime * colorTransitionSpeed);
            currentPulseAmplitude = Mathf.Lerp(currentPulseAmplitude, targetPulseAmplitude, Time.deltaTime * colorTransitionSpeed);
            currentEmissionColor = Color.Lerp(currentEmissionColor, targetEmissionColor, Time.deltaTime * colorTransitionSpeed);

            // Apply to shader via property block
            ApplyToShader();
        }

        /// <summary>
        /// Apply current values to shader
        /// </summary>
        private void ApplyToShader()
        {
            // Get current property block
            meshRenderer.GetPropertyBlock(propertyBlock);

            // Set properties
            propertyBlock.SetFloat(glowIntensityProperty, currentGlowIntensity);
            propertyBlock.SetFloat(glowPulseSpeedProperty, currentPulseSpeed);
            propertyBlock.SetFloat(glowPulseAmplitudeProperty, currentPulseAmplitude);

            if (modulateColor)
            {
                propertyBlock.SetColor(emissionColorProperty, currentEmissionColor);
            }

            // Apply property block
            meshRenderer.SetPropertyBlock(propertyBlock);
        }

        /// <summary>
        /// Set custom audio controller
        /// </summary>
        public void SetAudioController(AudioReactiveController controller)
        {
            audioController = controller;
        }

        /// <summary>
        /// Get current glow intensity
        /// </summary>
        public float GetGlowIntensity()
        {
            return currentGlowIntensity;
        }

        /// <summary>
        /// Manually set glow intensity (overrides audio reactivity temporarily)
        /// </summary>
        public void SetGlowIntensity(float intensity)
        {
            currentGlowIntensity = intensity;
            ApplyToShader();
        }

        /// <summary>
        /// Enable/disable audio reactivity
        /// </summary>
        public void SetAudioReactive(bool enabled)
        {
            this.enabled = enabled;

            if (!enabled)
            {
                // Reset to base values
                currentGlowIntensity = baseGlowIntensity;
                currentPulseSpeed = basePulseSpeed;
                currentPulseAmplitude = basePulseAmplitude;
                currentEmissionColor = baseEmissionColor;
                ApplyToShader();
            }
        }

#if UNITY_EDITOR
        [ContextMenu("Force Max Glow")]
        private void EditorForceMaxGlow()
        {
            currentGlowIntensity = maxGlowIntensity;
            currentEmissionColor = activeEmissionColor;
            ApplyToShader();
        }

        [ContextMenu("Force Base Glow")]
        private void EditorForceBaseGlow()
        {
            currentGlowIntensity = baseGlowIntensity;
            currentEmissionColor = baseEmissionColor;
            ApplyToShader();
        }

        [ContextMenu("Test Pulse")]
        private void EditorTestPulse()
        {
            StartCoroutine(TestPulseCoroutine());
        }

        private System.Collections.IEnumerator TestPulseCoroutine()
        {
            float duration = 2f;
            float elapsed = 0f;

            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;

                currentGlowIntensity = Mathf.Lerp(baseGlowIntensity, maxGlowIntensity, Mathf.Sin(t * Mathf.PI));
                currentEmissionColor = Color.Lerp(baseEmissionColor, activeEmissionColor, Mathf.Sin(t * Mathf.PI));

                ApplyToShader();

                yield return null;
            }

            currentGlowIntensity = baseGlowIntensity;
            currentEmissionColor = baseEmissionColor;
            ApplyToShader();
        }
#endif
    }
}
