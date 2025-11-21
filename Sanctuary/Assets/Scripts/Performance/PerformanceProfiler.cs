using UnityEngine;
using UnityEngine.Profiling;
using TMPro;
using System.Collections.Generic;

namespace Sanctuary.Performance
{
    /// <summary>
    /// In-VR performance profiler with visual display
    /// Monitors FPS, memory, draw calls, and custom metrics
    /// </summary>
    public class PerformanceProfiler : MonoBehaviour
    {
        [Header("Display Settings")]
        [SerializeField] private bool showProfiler = true;
        [SerializeField] private KeyCode toggleKey = KeyCode.F3;
        [SerializeField] private GameObject profilerCanvas;
        [SerializeField] private TextMeshProUGUI statsText;

        [Header("Update Settings")]
        [SerializeField] private float updateInterval = 0.5f; // Update display every 0.5s
        [SerializeField] private int fpsHistorySize = 60;

        [Header("Warning Thresholds")]
        [SerializeField] private float fpsWarningThreshold = 60f;
        [SerializeField] private float memoryWarningThreshold = 512f; // MB
        [SerializeField] private int drawCallWarningThreshold = 500;

        // Singleton
        private static PerformanceProfiler instance;
        public static PerformanceProfiler Instance => instance;

        // Performance metrics
        private float fps = 0f;
        private float frameTime = 0f;
        private long totalMemory = 0;
        private long usedMemory = 0;
        private int drawCalls = 0;
        private int triangles = 0;
        private int vertices = 0;

        // FPS tracking
        private List<float> fpsHistory = new List<float>();
        private float[] frameTimes;
        private int frameTimeIndex = 0;

        // Update timing
        private float lastUpdateTime;

        // Custom metrics
        private Dictionary<string, float> customMetrics = new Dictionary<string, float>();

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

            frameTimes = new float[fpsHistorySize];

            if (profilerCanvas != null)
            {
                profilerCanvas.SetActive(showProfiler);
            }
        }

        private void Update()
        {
            // Toggle profiler
            if (Input.GetKeyDown(toggleKey))
            {
                ToggleProfiler();
            }

            if (!showProfiler) return;

            // Track frame time
            frameTimes[frameTimeIndex] = Time.deltaTime;
            frameTimeIndex = (frameTimeIndex + 1) % frameTimes.Length;

            // Update display at intervals
            if (Time.time - lastUpdateTime >= updateInterval)
            {
                UpdateMetrics();
                UpdateDisplay();
                lastUpdateTime = Time.time;
            }
        }

        /// <summary>
        /// Update performance metrics
        /// </summary>
        private void UpdateMetrics()
        {
            // Calculate FPS
            float sum = 0f;
            foreach (float ft in frameTimes)
            {
                sum += ft;
            }

            frameTime = (sum / frameTimes.Length) * 1000f; // Convert to ms
            fps = 1f / (sum / frameTimes.Length);

            // Update FPS history
            fpsHistory.Add(fps);
            if (fpsHistory.Count > fpsHistorySize)
            {
                fpsHistory.RemoveAt(0);
            }

            // Memory metrics
            totalMemory = Profiler.GetTotalReservedMemoryLong() / (1024 * 1024); // Convert to MB
            usedMemory = Profiler.GetTotalAllocatedMemoryLong() / (1024 * 1024);

            // Rendering metrics (Unity Stats)
            drawCalls = UnityEngine.Rendering.DebugManager.instance != null ?
                        GetDrawCallCount() : 0;
            triangles = UnityStats.triangles;
            vertices = UnityStats.vertices;
        }

        /// <summary>
        /// Get draw call count from frame debugger
        /// </summary>
        private int GetDrawCallCount()
        {
            // This is approximation - actual draw calls require frame debugger
            #if UNITY_EDITOR
            return UnityEditor.UnityStats.batches;
            #else
            return 0; // Not available in builds
            #endif
        }

        /// <summary>
        /// Update display
        /// </summary>
        private void UpdateDisplay()
        {
            if (statsText == null) return;

            // Calculate min/max/avg FPS
            float minFPS = float.MaxValue;
            float maxFPS = 0f;
            float avgFPS = 0f;

            foreach (float f in fpsHistory)
            {
                if (f < minFPS) minFPS = f;
                if (f > maxFPS) maxFPS = f;
                avgFPS += f;
            }

            avgFPS /= fpsHistory.Count;

            // Build stats string
            string stats = $"<b>PERFORMANCE METRICS</b>\n\n";

            // FPS
            stats += $"<b>FPS:</b> {fps:F1}\n";
            stats += $"<b>Frame Time:</b> {frameTime:F2} ms\n";
            stats += $"<b>FPS Range:</b> {minFPS:F0} - {maxFPS:F0} (avg: {avgFPS:F0})\n";

            // FPS warning
            if (fps < fpsWarningThreshold)
            {
                stats += $"<color=red>⚠ FPS below {fpsWarningThreshold}</color>\n";
            }

            stats += "\n";

            // Memory
            stats += $"<b>Memory:</b> {usedMemory} / {totalMemory} MB\n";
            stats += $"<b>Mono Heap:</b> {Profiler.GetMonoUsedSizeLong() / (1024 * 1024)} MB\n";
            stats += $"<b>GC Alloc/Frame:</b> {Profiler.GetTotalAllocatedMemoryLong() / (1024 * 1024)} MB\n";

            // Memory warning
            if (usedMemory > memoryWarningThreshold)
            {
                stats += $"<color=red>⚠ Memory above {memoryWarningThreshold} MB</color>\n";
            }

            stats += "\n";

            // Rendering
            #if UNITY_EDITOR
            stats += $"<b>Draw Calls:</b> {drawCalls}\n";
            #else
            stats += $"<b>Draw Calls:</b> N/A (editor only)\n";
            #endif

            stats += $"<b>Triangles:</b> {triangles:N0}\n";
            stats += $"<b>Vertices:</b> {vertices:N0}\n";

            // Draw call warning
            #if UNITY_EDITOR
            if (drawCalls > drawCallWarningThreshold)
            {
                stats += $"<color=red>⚠ Draw calls above {drawCallWarningThreshold}</color>\n";
            }
            #endif

            stats += "\n";

            // LOD System stats (if available)
            if (LODSystem.Instance != null)
            {
                var lodStats = LODSystem.Instance.GetStats();
                stats += $"<b>LOD SYSTEM</b>\n";
                stats += $"Managed Objects: {lodStats.totalObjects}\n";
                stats += $"High Detail: {lodStats.highDetailCount}\n";
                stats += $"Medium Detail: {lodStats.mediumDetailCount}\n";
                stats += $"Low Detail: {lodStats.lowDetailCount}\n";
                stats += $"Culled: {lodStats.culledCount}\n";
                stats += "\n";
            }

            // Quest Performance (if available)
            if (QuestPerformanceManager.Instance != null)
            {
                var perfMetrics = QuestPerformanceManager.Instance.GetMetrics();
                stats += $"<b>QUEST OPTIMIZATION</b>\n";
                stats += $"Target FPS: {perfMetrics.targetFPS}\n";
                stats += $"Render Scale: {perfMetrics.renderScale:F2}\n";
                stats += $"Quality Level: {perfMetrics.qualityLevel}\n";
                stats += $"Shadow Distance: {perfMetrics.shadowDistance:F0}m\n";
                stats += "\n";
            }

            // Custom metrics
            if (customMetrics.Count > 0)
            {
                stats += $"<b>CUSTOM METRICS</b>\n";
                foreach (var metric in customMetrics)
                {
                    stats += $"{metric.Key}: {metric.Value:F2}\n";
                }
            }

            statsText.text = stats;
        }

        /// <summary>
        /// Toggle profiler visibility
        /// </summary>
        public void ToggleProfiler()
        {
            showProfiler = !showProfiler;

            if (profilerCanvas != null)
            {
                profilerCanvas.SetActive(showProfiler);
            }

            Debug.Log($"[Profiler] Profiler {(showProfiler ? "enabled" : "disabled")}");
        }

        /// <summary>
        /// Set profiler visibility
        /// </summary>
        public void SetProfilerVisible(bool visible)
        {
            showProfiler = visible;

            if (profilerCanvas != null)
            {
                profilerCanvas.SetActive(showProfiler);
            }
        }

        /// <summary>
        /// Add custom metric
        /// </summary>
        public void AddCustomMetric(string name, float value)
        {
            customMetrics[name] = value;
        }

        /// <summary>
        /// Remove custom metric
        /// </summary>
        public void RemoveCustomMetric(string name)
        {
            customMetrics.Remove(name);
        }

        /// <summary>
        /// Get current FPS
        /// </summary>
        public float GetFPS()
        {
            return fps;
        }

        /// <summary>
        /// Get current frame time (ms)
        /// </summary>
        public float GetFrameTime()
        {
            return frameTime;
        }

        /// <summary>
        /// Get memory usage (MB)
        /// </summary>
        public long GetMemoryUsage()
        {
            return usedMemory;
        }

        /// <summary>
        /// Log performance snapshot to console
        /// </summary>
        [ContextMenu("Log Performance Snapshot")]
        public void LogSnapshot()
        {
            Debug.Log($"===== PERFORMANCE SNAPSHOT =====\n" +
                     $"FPS: {fps:F1} ({frameTime:F2} ms)\n" +
                     $"Memory: {usedMemory} / {totalMemory} MB\n" +
                     $"Draw Calls: {drawCalls}\n" +
                     $"Triangles: {triangles:N0}\n" +
                     $"Vertices: {vertices:N0}\n" +
                     $"================================");
        }

#if UNITY_EDITOR
        [ContextMenu("Force GC Collect")]
        private void EditorForceGC()
        {
            System.GC.Collect();
            Debug.Log("[Profiler] Forced garbage collection");
        }

        [ContextMenu("Print Custom Metrics")]
        private void EditorPrintCustomMetrics()
        {
            Debug.Log("Custom Metrics:");
            foreach (var metric in customMetrics)
            {
                Debug.Log($"  {metric.Key}: {metric.Value}");
            }
        }
#endif
    }
}
