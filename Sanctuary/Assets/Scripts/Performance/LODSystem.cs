using System.Collections.Generic;
using UnityEngine;

namespace Sanctuary.Performance
{
    /// <summary>
    /// Advanced LOD (Level of Detail) system for Quest 3 optimization
    /// Manages model quality, texture resolution, and shader complexity based on distance and performance
    /// </summary>
    public class LODSystem : MonoBehaviour
    {
        [Header("LOD Configuration")]
        [SerializeField] private Transform viewerTransform; // Usually the VR camera
        [SerializeField] private bool autoDetectViewer = true;
        [SerializeField] private float updateInterval = 0.2f; // 5Hz update rate

        [Header("Distance Thresholds")]
        [SerializeField] private float lodHighDistance = 5f;
        [SerializeField] private float lodMediumDistance = 15f;
        [SerializeField] private float lodLowDistance = 30f;
        [SerializeField] private float cullDistance = 50f;

        [Header("Quest Optimization")]
        [SerializeField] private bool isQuestBuild = false;
        [SerializeField] private float questDistanceMultiplier = 0.7f; // Reduce LOD distances on Quest
        [SerializeField] private int maxVisibleObjects = 50;

        [Header("Performance Settings")]
        [SerializeField] private bool enableDynamicQuality = true;
        [SerializeField] private int targetFramerate = 72; // Quest 3 target
        [SerializeField] private float performanceCheckInterval = 1.0f;

        // Singleton
        private static LODSystem instance;
        public static LODSystem Instance => instance;

        // Managed objects
        private List<LODObject> managedObjects = new List<LODObject>();
        private List<LODObject> visibleObjects = new List<LODObject>();

        // Performance tracking
        private float lastUpdateTime;
        private float lastPerformanceCheckTime;
        private float averageFPS;
        private int frameCount;
        private float frameTimeSum;

        // LOD stats
        private int highDetailCount = 0;
        private int mediumDetailCount = 0;
        private int lowDetailCount = 0;
        private int culledCount = 0;

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

            // Detect platform
            DetectPlatform();

            // Auto-detect viewer (main camera)
            if (autoDetectViewer && viewerTransform == null)
            {
                Camera mainCam = Camera.main;
                if (mainCam != null)
                {
                    viewerTransform = mainCam.transform;
                }
            }

            Debug.Log($"[LODSystem] Initialized (Platform: {(isQuestBuild ? "Quest" : "PCVR")}, Target FPS: {targetFramerate})");
        }

        private void Update()
        {
            // Update LODs at fixed interval
            if (Time.time - lastUpdateTime >= updateInterval)
            {
                UpdateLODs();
                lastUpdateTime = Time.time;
            }

            // Track performance
            TrackPerformance();

            // Dynamic quality adjustment
            if (enableDynamicQuality && Time.time - lastPerformanceCheckTime >= performanceCheckInterval)
            {
                AdjustQualityBasedOnPerformance();
                lastPerformanceCheckTime = Time.time;
            }
        }

        /// <summary>
        /// Detect if running on Quest
        /// </summary>
        private void DetectPlatform()
        {
            #if UNITY_ANDROID && !UNITY_EDITOR
            isQuestBuild = true;
            #else
            isQuestBuild = false;
            #endif

            // Apply Quest distance multiplier
            if (isQuestBuild)
            {
                lodHighDistance *= questDistanceMultiplier;
                lodMediumDistance *= questDistanceMultiplier;
                lodLowDistance *= questDistanceMultiplier;
                cullDistance *= questDistanceMultiplier;
            }
        }

        /// <summary>
        /// Register an object for LOD management
        /// </summary>
        public void RegisterObject(LODObject lodObject)
        {
            if (!managedObjects.Contains(lodObject))
            {
                managedObjects.Add(lodObject);
                Debug.Log($"[LODSystem] Registered object: {lodObject.gameObject.name}");
            }
        }

        /// <summary>
        /// Unregister an object from LOD management
        /// </summary>
        public void UnregisterObject(LODObject lodObject)
        {
            managedObjects.Remove(lodObject);
            visibleObjects.Remove(lodObject);
        }

        /// <summary>
        /// Update LOD levels for all managed objects
        /// </summary>
        private void UpdateLODs()
        {
            if (viewerTransform == null) return;

            // Reset counters
            highDetailCount = 0;
            mediumDetailCount = 0;
            lowDetailCount = 0;
            culledCount = 0;
            visibleObjects.Clear();

            // Sort objects by distance
            managedObjects.Sort((a, b) =>
            {
                float distA = Vector3.Distance(viewerTransform.position, a.transform.position);
                float distB = Vector3.Distance(viewerTransform.position, b.transform.position);
                return distA.CompareTo(distB);
            });

            // Update each object
            for (int i = 0; i < managedObjects.Count; i++)
            {
                LODObject obj = managedObjects[i];

                if (obj == null || !obj.gameObject.activeInHierarchy)
                    continue;

                float distance = Vector3.Distance(viewerTransform.position, obj.transform.position);

                // Determine LOD level
                LODLevel newLevel;

                if (distance > cullDistance)
                {
                    newLevel = LODLevel.Culled;
                    culledCount++;
                }
                else if (distance > lodLowDistance)
                {
                    newLevel = LODLevel.Low;
                    lowDetailCount++;
                }
                else if (distance > lodMediumDistance)
                {
                    newLevel = LODLevel.Medium;
                    mediumDetailCount++;
                }
                else if (distance > lodHighDistance)
                {
                    newLevel = LODLevel.High;
                    highDetailCount++;
                }
                else
                {
                    newLevel = LODLevel.Ultra;
                    highDetailCount++;
                }

                // Enforce max visible objects limit on Quest
                if (isQuestBuild && visibleObjects.Count >= maxVisibleObjects && newLevel != LODLevel.Culled)
                {
                    newLevel = LODLevel.Culled;
                    culledCount++;
                }
                else if (newLevel != LODLevel.Culled)
                {
                    visibleObjects.Add(obj);
                }

                // Apply LOD level
                obj.SetLODLevel(newLevel, distance);
            }
        }

        /// <summary>
        /// Track performance metrics
        /// </summary>
        private void TrackPerformance()
        {
            frameCount++;
            frameTimeSum += Time.deltaTime;

            if (frameCount >= 10)
            {
                averageFPS = frameCount / frameTimeSum;
                frameCount = 0;
                frameTimeSum = 0f;
            }
        }

        /// <summary>
        /// Dynamically adjust quality based on performance
        /// </summary>
        private void AdjustQualityBasedOnPerformance()
        {
            if (averageFPS < targetFramerate * 0.9f) // Below 90% of target
            {
                // Reduce quality
                lodHighDistance *= 0.95f;
                lodMediumDistance *= 0.95f;
                lodLowDistance *= 0.95f;

                Debug.LogWarning($"[LODSystem] Performance below target ({averageFPS:F1} FPS), reducing LOD distances");
            }
            else if (averageFPS > targetFramerate * 1.1f) // Above 110% of target
            {
                // Increase quality
                lodHighDistance = Mathf.Min(lodHighDistance * 1.05f, 10f);
                lodMediumDistance = Mathf.Min(lodMediumDistance * 1.05f, 25f);
                lodLowDistance = Mathf.Min(lodLowDistance * 1.05f, 40f);

                Debug.Log($"[LODSystem] Performance above target ({averageFPS:F1} FPS), increasing LOD distances");
            }
        }

        /// <summary>
        /// Get current LOD statistics
        /// </summary>
        public LODStats GetStats()
        {
            return new LODStats
            {
                totalObjects = managedObjects.Count,
                ultraDetailCount = 0, // Not tracked separately
                highDetailCount = highDetailCount,
                mediumDetailCount = mediumDetailCount,
                lowDetailCount = lowDetailCount,
                culledCount = culledCount,
                averageFPS = averageFPS,
                targetFPS = targetFramerate
            };
        }

        /// <summary>
        /// Force update all LODs immediately
        /// </summary>
        public void ForceUpdate()
        {
            UpdateLODs();
        }

        /// <summary>
        /// Set viewer transform manually
        /// </summary>
        public void SetViewer(Transform viewer)
        {
            viewerTransform = viewer;
        }

#if UNITY_EDITOR
        private void OnDrawGizmos()
        {
            if (viewerTransform == null) return;

            // Draw LOD distance spheres
            Gizmos.color = new Color(0, 1, 0, 0.1f);
            Gizmos.DrawWireSphere(viewerTransform.position, lodHighDistance);

            Gizmos.color = new Color(1, 1, 0, 0.1f);
            Gizmos.DrawWireSphere(viewerTransform.position, lodMediumDistance);

            Gizmos.color = new Color(1, 0.5f, 0, 0.1f);
            Gizmos.DrawWireSphere(viewerTransform.position, lodLowDistance);

            Gizmos.color = new Color(1, 0, 0, 0.1f);
            Gizmos.DrawWireSphere(viewerTransform.position, cullDistance);
        }

        [ContextMenu("Print LOD Stats")]
        private void PrintStats()
        {
            var stats = GetStats();
            Debug.Log($"LOD Stats:\n" +
                     $"Total: {stats.totalObjects}\n" +
                     $"High: {stats.highDetailCount}\n" +
                     $"Medium: {stats.mediumDetailCount}\n" +
                     $"Low: {stats.lowDetailCount}\n" +
                     $"Culled: {stats.culledCount}\n" +
                     $"FPS: {stats.averageFPS:F1} (Target: {stats.targetFPS})");
        }
#endif
    }

    public enum LODLevel
    {
        Ultra = 0,   // < 5m (all features enabled)
        High = 1,    // 5-15m (high quality)
        Medium = 2,  // 15-30m (medium quality)
        Low = 3,     // 30-50m (low quality)
        Culled = 4   // > 50m (disabled)
    }

    public struct LODStats
    {
        public int totalObjects;
        public int ultraDetailCount;
        public int highDetailCount;
        public int mediumDetailCount;
        public int lowDetailCount;
        public int culledCount;
        public float averageFPS;
        public int targetFPS;
    }
}
