using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Sanctuary.Performance
{
    /// <summary>
    /// Quest 3 specific performance optimization manager
    /// Handles render settings, texture quality, and dynamic performance adjustments
    /// Targets 72 FPS for smooth VR experience
    /// </summary>
    public class QuestPerformanceManager : MonoBehaviour
    {
        [Header("Performance Targets")]
        [SerializeField] private int targetFramerate = 72; // Quest 3 default
        [SerializeField] private bool allowHighRefreshRate = true; // Quest 3 supports 90Hz/120Hz
        [SerializeField] private float minAcceptableFPS = 65f;

        [Header("Quality Levels")]
        [SerializeField] private QualityPreset currentPreset = QualityPreset.Balanced;
        [SerializeField] private bool enableDynamicAdjustment = true;
        [SerializeField] private float adjustmentInterval = 2.0f;

        [Header("Render Settings")]
        [SerializeField] private UniversalRenderPipelineAsset questPipelineAsset;
        [SerializeField] private float renderScale = 0.85f; // Quest 3 optimized
        [SerializeField] private int msaaLevel = 2; // Quest 3 can handle 2x MSAA

        [Header("Texture Settings")]
        [SerializeField] private int maxTextureSize = 1024; // Quest limit
        [SerializeField] private bool compressTextures = true;
        [SerializeField] private FilterMode textureFilterMode = FilterMode.Bilinear;

        [Header("Shadow Settings")]
        [SerializeField] private ShadowQuality shadowQuality = ShadowQuality.Medium;
        [SerializeField] private float shadowDistance = 20f;
        [SerializeField] private int shadowCascades = 1;

        [Header("Post-Processing")]
        [SerializeField] private bool enableBloom = true;
        [SerializeField] private bool enableColorGrading = true;
        [SerializeField] private bool enableAmbientOcclusion = false; // Expensive on Quest
        [SerializeField] private bool enableMotionBlur = false; // Can cause motion sickness in VR

        // Singleton
        private static QuestPerformanceManager instance;
        public static QuestPerformanceManager Instance => instance;

        // Performance tracking
        private float[] frameTimes;
        private int frameTimeIndex = 0;
        private float averageFPS = 72f;
        private float lastAdjustmentTime;

        // Quality state
        private int currentQualityLevel = 1; // 0=Low, 1=Medium, 2=High

        public enum QualityPreset
        {
            Performance,  // Prioritize framerate
            Balanced,     // Balance quality and performance
            Quality       // Prioritize visual quality
        }

        private void Awake()
        {
            if (instance == null)
            {
                instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
                return;
            }

            // Initialize performance tracking
            frameTimes = new float[60]; // Track last 60 frames

            // Detect platform
            bool isQuest = DetectQuestHardware();

            if (!isQuest)
            {
                Debug.Log("[QuestPerformance] Not running on Quest, disabling optimizations");
                enabled = false;
                return;
            }

            InitializeQuestOptimizations();
        }

        private void Start()
        {
            ApplyQualityPreset(currentPreset);
        }

        private void Update()
        {
            // Track frame times
            TrackFramerate();

            // Dynamic quality adjustment
            if (enableDynamicAdjustment && Time.time - lastAdjustmentTime >= adjustmentInterval)
            {
                AdjustQualityBasedOnPerformance();
                lastAdjustmentTime = Time.time;
            }
        }

        /// <summary>
        /// Detect if running on Quest hardware
        /// </summary>
        private bool DetectQuestHardware()
        {
            #if UNITY_ANDROID && !UNITY_EDITOR
            string deviceModel = SystemInfo.deviceModel.ToLower();

            if (deviceModel.Contains("quest") || deviceModel.Contains("meta"))
            {
                Debug.Log($"[QuestPerformance] Detected Quest device: {SystemInfo.deviceModel}");
                return true;
            }
            #endif

            return false;
        }

        /// <summary>
        /// Initialize Quest-specific optimizations
        /// </summary>
        private void InitializeQuestOptimizations()
        {
            // Set target framerate
            Application.targetFrameRate = targetFramerate;

            // Set VSync for consistent framerate
            QualitySettings.vSyncCount = 1;

            // Optimize physics
            Time.fixedDeltaTime = 1f / 90f; // Physics at 90Hz for VR

            // Set Quest-optimized quality settings
            QualitySettings.shadows = ShadowQuality.All;
            QualitySettings.shadowDistance = shadowDistance;
            QualitySettings.shadowCascades = shadowCascades;
            QualitySettings.shadowResolution = ShadowResolution.Medium;

            // Texture quality
            QualitySettings.masterTextureLimit = 1; // Reduce by one mip level
            QualitySettings.anisotropicFiltering = AnisotropicFiltering.Disable;

            // LOD settings
            QualitySettings.lodBias = 0.7f; // Reduce LOD distances
            QualitySettings.maximumLODLevel = 0;

            // Disable expensive features
            QualitySettings.softParticles = false;
            QualitySettings.realtimeReflectionProbes = false;

            // Apply URP settings if available
            if (questPipelineAsset != null)
            {
                ApplyURPSettings();
            }

            Debug.Log($"[QuestPerformance] Quest optimizations initialized (Target: {targetFramerate} FPS, Render Scale: {renderScale})");
        }

        /// <summary>
        /// Apply URP-specific settings
        /// </summary>
        private void ApplyURPSettings()
        {
            if (questPipelineAsset == null) return;

            // Set render scale
            questPipelineAsset.renderScale = renderScale;

            // Set MSAA
            questPipelineAsset.msaaSampleCount = msaaLevel;

            // Shadow settings
            questPipelineAsset.shadowDistance = shadowDistance;
            questPipelineAsset.shadowCascadeCount = shadowCascades;

            // Lighting
            questPipelineAsset.supportsLightLayers = false;

            Debug.Log("[QuestPerformance] URP settings applied");
        }

        /// <summary>
        /// Apply quality preset
        /// </summary>
        public void ApplyQualityPreset(QualityPreset preset)
        {
            currentPreset = preset;

            switch (preset)
            {
                case QualityPreset.Performance:
                    ApplyPerformancePreset();
                    currentQualityLevel = 0;
                    break;

                case QualityPreset.Balanced:
                    ApplyBalancedPreset();
                    currentQualityLevel = 1;
                    break;

                case QualityPreset.Quality:
                    ApplyQualityPreset();
                    currentQualityLevel = 2;
                    break;
            }

            Debug.Log($"[QuestPerformance] Applied quality preset: {preset}");
        }

        private void ApplyPerformancePreset()
        {
            if (questPipelineAsset != null)
            {
                questPipelineAsset.renderScale = 0.75f;
                questPipelineAsset.msaaSampleCount = 0; // No MSAA
            }

            QualitySettings.shadowDistance = 15f;
            QualitySettings.lodBias = 0.5f;
            QualitySettings.masterTextureLimit = 2;

            targetFramerate = 90; // Try for higher framerate
            Application.targetFrameRate = targetFramerate;
        }

        private void ApplyBalancedPreset()
        {
            if (questPipelineAsset != null)
            {
                questPipelineAsset.renderScale = 0.85f;
                questPipelineAsset.msaaSampleCount = 2;
            }

            QualitySettings.shadowDistance = 20f;
            QualitySettings.lodBias = 0.7f;
            QualitySettings.masterTextureLimit = 1;

            targetFramerate = 72;
            Application.targetFrameRate = targetFramerate;
        }

        private void ApplyQualityPreset()
        {
            if (questPipelineAsset != null)
            {
                questPipelineAsset.renderScale = 1.0f;
                questPipelineAsset.msaaSampleCount = 4;
            }

            QualitySettings.shadowDistance = 30f;
            QualitySettings.lodBias = 1.0f;
            QualitySettings.masterTextureLimit = 0;

            targetFramerate = 72;
            Application.targetFrameRate = targetFramerate;
        }

        /// <summary>
        /// Track framerate
        /// </summary>
        private void TrackFramerate()
        {
            frameTimes[frameTimeIndex] = Time.deltaTime;
            frameTimeIndex = (frameTimeIndex + 1) % frameTimes.Length;

            // Calculate average every N frames
            if (frameTimeIndex == 0)
            {
                float sum = 0f;
                foreach (float ft in frameTimes)
                {
                    sum += ft;
                }

                float avgFrameTime = sum / frameTimes.Length;
                averageFPS = 1f / avgFrameTime;
            }
        }

        /// <summary>
        /// Dynamically adjust quality based on performance
        /// </summary>
        private void AdjustQualityBasedOnPerformance()
        {
            if (averageFPS < minAcceptableFPS && currentQualityLevel > 0)
            {
                // Reduce quality
                currentQualityLevel--;

                switch (currentQualityLevel)
                {
                    case 0:
                        ApplyPerformancePreset();
                        break;
                    case 1:
                        ApplyBalancedPreset();
                        break;
                }

                Debug.LogWarning($"[QuestPerformance] Performance below target ({averageFPS:F1} FPS), reducing quality to level {currentQualityLevel}");
            }
            else if (averageFPS > targetFramerate * 1.15f && currentQualityLevel < 2)
            {
                // Increase quality
                currentQualityLevel++;

                switch (currentQualityLevel)
                {
                    case 1:
                        ApplyBalancedPreset();
                        break;
                    case 2:
                        ApplyQualityPreset();
                        break;
                }

                Debug.Log($"[QuestPerformance] Performance above target ({averageFPS:F1} FPS), increasing quality to level {currentQualityLevel}");
            }
        }

        /// <summary>
        /// Get current performance metrics
        /// </summary>
        public PerformanceMetrics GetMetrics()
        {
            return new PerformanceMetrics
            {
                averageFPS = averageFPS,
                targetFPS = targetFramerate,
                renderScale = questPipelineAsset != null ? questPipelineAsset.renderScale : renderScale,
                qualityLevel = currentQualityLevel,
                shadowDistance = QualitySettings.shadowDistance,
                textureQuality = 3 - QualitySettings.masterTextureLimit
            };
        }

        /// <summary>
        /// Force specific quality level
        /// </summary>
        public void SetQualityLevel(int level)
        {
            currentQualityLevel = Mathf.Clamp(level, 0, 2);

            switch (currentQualityLevel)
            {
                case 0:
                    ApplyQualityPreset(QualityPreset.Performance);
                    break;
                case 1:
                    ApplyQualityPreset(QualityPreset.Balanced);
                    break;
                case 2:
                    ApplyQualityPreset(QualityPreset.Quality);
                    break;
            }
        }

        /// <summary>
        /// Enable/disable dynamic quality adjustment
        /// </summary>
        public void SetDynamicAdjustment(bool enabled)
        {
            enableDynamicAdjustment = enabled;
        }

#if UNITY_EDITOR
        [ContextMenu("Apply Performance Preset")]
        private void EditorApplyPerformance()
        {
            ApplyQualityPreset(QualityPreset.Performance);
        }

        [ContextMenu("Apply Balanced Preset")]
        private void EditorApplyBalanced()
        {
            ApplyQualityPreset(QualityPreset.Balanced);
        }

        [ContextMenu("Apply Quality Preset")]
        private void EditorApplyQuality()
        {
            ApplyQualityPreset(QualityPreset.Quality);
        }

        [ContextMenu("Print Performance Metrics")]
        private void PrintMetrics()
        {
            var metrics = GetMetrics();
            Debug.Log($"Performance Metrics:\n" +
                     $"FPS: {metrics.averageFPS:F1} (Target: {metrics.targetFPS})\n" +
                     $"Render Scale: {metrics.renderScale:F2}\n" +
                     $"Quality Level: {metrics.qualityLevel}\n" +
                     $"Shadow Distance: {metrics.shadowDistance:F0}m\n" +
                     $"Texture Quality: {metrics.textureQuality}");
        }
#endif
    }

    public struct PerformanceMetrics
    {
        public float averageFPS;
        public int targetFPS;
        public float renderScale;
        public int qualityLevel; // 0=Low, 1=Medium, 2=High
        public float shadowDistance;
        public int textureQuality;
    }
}
