using UnityEngine;
using System.Collections;
using System.Collections.Generic;

namespace Sanctuary.Biomes
{
    /// <summary>
    /// Muir Glacier - Climate Awareness Biome
    /// Educational biome inspired by John Muir's glaciology work
    /// Features time-lapse glacial retreat and climate data visualization
    /// </summary>
    public class MuirGlacierBiome : BiomeController
    {
        [Header("Muir Glacier Specific")]
        [SerializeField] private Transform glacierCenter;
        [SerializeField] private float glacierRadius = 100f;

        [Header("Glacier Visualization")]
        [SerializeField] private GameObject glacierMeshPrefab;
        [SerializeField] private Material iceMaterial;
        [SerializeField] private Material snowMaterial;
        [SerializeField] private bool enableTimeLapse = true;

        [Header("Climate Data")]
        [SerializeField] private ClimateDataPoint[] climateDataPoints;
        [SerializeField] private int currentYear = 2024;
        [SerializeField] private int historicalStartYear = 1850;
        [SerializeField] private float timeLapseSpeed = 1.0f; // Years per second

        [Header("Environmental Effects")]
        [SerializeField] private ParticleSystem snowfallSystem;
        [SerializeField] private ParticleSystem meltWaterSystem;
        [SerializeField] private AudioSource glacierCreakingSound;
        [SerializeField] private AudioSource meltWaterSound;

        [Header("Visual Settings")]
        [SerializeField] private Color iceColor = new Color(0.7f, 0.85f, 0.95f, 0.8f);
        [SerializeField] private Color skyColor = new Color(0.5f, 0.7f, 0.9f);
        [SerializeField] private float iceTransparency = 0.8f;

        [Header("Education Settings")]
        [SerializeField] private bool showClimateOverlay = false;
        [SerializeField] private GameObject climateDataOverlayPrefab;

        // Glacier state
        private float currentGlacierScale = 1.0f;
        private float targetGlacierScale = 1.0f;
        private int timeLapseYear = 2024;
        private bool isTimeLapsePlaying = false;
        private List<GameObject> glacierSegments = new List<GameObject>();

        // Climate metrics
        private float currentTemperature = -5.0f; // Celsius
        private float currentCO2Level = 420.0f; // PPM
        private float glacialRetreatMeters = 0f;

        protected override void Awake()
        {
            // Set biome info
            biomeName = "The Muir Glacial Observatory";
            biomeDescription = "A frozen wilderness inspired by John Muir's glaciology. " +
                               "Witness the dramatic retreat of glaciers through time and understand climate change impacts.";

            // Set environmental defaults
            fogColor = new Color(0.8f, 0.9f, 0.95f);
            fogDensity = 0.015f;

            base.Awake();

            SetupGlacialEnvironment();
        }

        /// <summary>
        /// Configure glacial environment
        /// </summary>
        private void SetupGlacialEnvironment()
        {
            // Setup lighting for arctic clarity
            Light directionalLight = RenderSettings.sun;
            if (directionalLight != null)
            {
                directionalLight.color = new Color(0.95f, 0.95f, 1f);
                directionalLight.intensity = 1.2f;
                directionalLight.transform.rotation = Quaternion.Euler(35f, -60f, 0f);
                directionalLight.shadows = LightShadows.Soft;
            }

            // Setup ambient light for snow reflection
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Skybox;
            RenderSettings.ambientLight = new Color(0.6f, 0.65f, 0.7f);

            // Setup fog
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = fogColor;

            // Setup skybox color
            if (RenderSettings.skybox != null)
            {
                RenderSettings.skybox.SetColor("_Tint", skyColor);
            }

            Debug.Log("[MuirGlacier] Glacial environment configured");
        }

        protected override void Start()
        {
            base.Start();

            // Generate glacier geometry
            if (glacierMeshPrefab != null)
            {
                GenerateGlacierGeometry();
            }

            // Setup climate data points
            SetupClimateDataPoints();

            // Start environmental effects
            StartSnowfall();
            StartGlacierAmbience();

            // Start time-lapse if enabled
            if (enableTimeLapse)
            {
                StartCoroutine(TimeLapseSimulation());
            }

            Debug.Log($"[MuirGlacier] Biome initialized at year {currentYear}");
        }

        private void Update()
        {
            // Smooth glacier scale transitions
            if (Mathf.Abs(currentGlacierScale - targetGlacierScale) > 0.01f)
            {
                currentGlacierScale = Mathf.Lerp(currentGlacierScale, targetGlacierScale, Time.deltaTime * 0.5f);
                UpdateGlacierScale();
            }

            // Update ice material based on temperature
            UpdateIceMaterial();

            // Update climate overlay if active
            if (showClimateOverlay)
            {
                UpdateClimateOverlay();
            }
        }

        /// <summary>
        /// Generate procedural glacier geometry
        /// </summary>
        private void GenerateGlacierGeometry()
        {
            Debug.Log("[MuirGlacier] Generating glacier geometry...");

            // Create glacier in segments for dynamic retreat
            int segments = 10;
            float segmentLength = glacierRadius / segments;

            for (int i = 0; i < segments; i++)
            {
                Vector3 position = glacierCenter.position + Vector3.forward * (i * segmentLength);
                position.y = CalculateGlacierElevation(i, segments);

                GameObject segment = Instantiate(glacierMeshPrefab, position, Quaternion.identity);
                segment.name = $"GlacierSegment_{i}";
                segment.transform.SetParent(transform);

                // Apply ice material
                Renderer renderer = segment.GetComponent<Renderer>();
                if (renderer != null && iceMaterial != null)
                {
                    renderer.material = iceMaterial;
                    renderer.material.color = iceColor;
                }

                // Scale segment based on distance (terminus is smaller)
                float scaleMultiplier = 1.0f - (i * 0.05f);
                segment.transform.localScale = new Vector3(
                    segmentLength * 2f * scaleMultiplier,
                    10f * scaleMultiplier,
                    segmentLength * scaleMultiplier
                );

                glacierSegments.Add(segment);
            }

            Debug.Log($"[MuirGlacier] Generated {segments} glacier segments");
        }

        /// <summary>
        /// Calculate glacier elevation profile
        /// </summary>
        private float CalculateGlacierElevation(int segmentIndex, int totalSegments)
        {
            // Create a realistic glacier profile (higher at accumulation zone)
            float normalizedPosition = (float)segmentIndex / totalSegments;

            // Parabolic profile
            float elevation = Mathf.Lerp(50f, 5f, normalizedPosition * normalizedPosition);

            return elevation;
        }

        /// <summary>
        /// Update glacier scale based on climate data
        /// </summary>
        private void UpdateGlacierScale()
        {
            // Retreat glacier from terminus (far segments disappear first)
            for (int i = 0; i < glacierSegments.Count; i++)
            {
                GameObject segment = glacierSegments[i];
                if (segment == null) continue;

                // Calculate if this segment should be visible
                float segmentThreshold = (float)i / glacierSegments.Count;

                if (segmentThreshold > currentGlacierScale)
                {
                    // Segment has melted away
                    segment.SetActive(false);
                }
                else
                {
                    segment.SetActive(true);

                    // Reduce scale near the new terminus
                    float distanceFromTerminus = currentGlacierScale - segmentThreshold;
                    float terminusScale = Mathf.Clamp01(distanceFromTerminus * 10f);

                    Vector3 originalScale = segment.transform.localScale;
                    segment.transform.localScale = new Vector3(
                        originalScale.x,
                        originalScale.y * terminusScale,
                        originalScale.z
                    );
                }
            }
        }

        /// <summary>
        /// Setup climate data educational nodes
        /// </summary>
        private void SetupClimateDataPoints()
        {
            if (climateDataPoints == null || climateDataPoints.Length == 0)
            {
                Debug.LogWarning("[MuirGlacier] No climate data points configured");
                return;
            }

            foreach (ClimateDataPoint dataPoint in climateDataPoints)
            {
                if (dataPoint != null && dataPoint.dataNode != null)
                {
                    dataPoint.dataNode.Activate();

                    // Spawn data visualization
                    if (climateDataOverlayPrefab != null)
                    {
                        Vector3 spawnPos = dataPoint.dataNode.transform.position + Vector3.up * 3f;
                        GameObject overlay = Instantiate(climateDataOverlayPrefab, spawnPos, Quaternion.identity);
                        overlay.transform.SetParent(dataPoint.dataNode.transform);

                        // Display data on overlay
                        UpdateDataOverlay(overlay, dataPoint);
                    }
                }
            }

            Debug.Log($"[MuirGlacier] Configured {climateDataPoints.Length} climate data points");
        }

        /// <summary>
        /// Update data overlay with current climate metrics
        /// </summary>
        private void UpdateDataOverlay(GameObject overlay, ClimateDataPoint dataPoint)
        {
            // This would update UI text meshes or canvas elements
            // Implementation depends on overlay prefab structure
            TMPro.TextMeshPro textMesh = overlay.GetComponentInChildren<TMPro.TextMeshPro>();
            if (textMesh != null)
            {
                textMesh.text = $"Year: {dataPoint.year}\n" +
                               $"Temp: {dataPoint.temperature:F1}°C\n" +
                               $"CO₂: {dataPoint.co2Level:F0} ppm\n" +
                               $"Retreat: {dataPoint.retreatMeters:F0}m";
            }
        }

        /// <summary>
        /// Time-lapse simulation of glacier retreat
        /// </summary>
        private IEnumerator TimeLapseSimulation()
        {
            Debug.Log("[MuirGlacier] Starting time-lapse simulation...");

            isTimeLapsePlaying = true;
            timeLapseYear = historicalStartYear;

            while (isTimeLapsePlaying && timeLapseYear <= currentYear)
            {
                // Calculate glacier scale for current year
                float yearProgress = (float)(timeLapseYear - historicalStartYear) / (currentYear - historicalStartYear);

                // Glacier retreat accelerates over time (exponential)
                float retreatFactor = Mathf.Lerp(1.0f, 0.3f, yearProgress * yearProgress);
                targetGlacierScale = retreatFactor;

                // Update climate metrics
                UpdateClimateMetricsForYear(timeLapseYear);

                // Update glacial retreat calculation
                glacialRetreatMeters = (1.0f - retreatFactor) * glacierRadius;

                Debug.Log($"[MuirGlacier] Year {timeLapseYear}: Glacier at {retreatFactor * 100:F0}% of original size ({glacialRetreatMeters:F0}m retreat)");

                // Wait based on time-lapse speed
                yield return new WaitForSeconds(1.0f / timeLapseSpeed);

                timeLapseYear++;
            }

            isTimeLapsePlaying = false;
            Debug.Log("[MuirGlacier] Time-lapse simulation complete");
        }

        /// <summary>
        /// Update climate metrics based on historical year
        /// </summary>
        private void UpdateClimateMetricsForYear(int year)
        {
            // Simplified climate model (based on real trends)
            float yearsSince1850 = year - 1850;

            // Temperature increase (roughly 1.2°C over 174 years)
            currentTemperature = -5.0f + (yearsSince1850 * 0.007f);

            // CO2 increase (280 ppm in 1850 to 420 ppm in 2024)
            currentCO2Level = 280f + (yearsSince1850 * 0.8f);

            // Update ice material transparency based on temperature
            if (iceMaterial != null)
            {
                // Warmer = more melt water = more transparent ice
                float transparencyAdjustment = Mathf.Clamp01(currentTemperature / 10f);
                Color adjustedColor = iceColor;
                adjustedColor.a = iceTransparency - (transparencyAdjustment * 0.2f);
                iceMaterial.color = adjustedColor;
            }
        }

        /// <summary>
        /// Update ice material based on environmental conditions
        /// </summary>
        private void UpdateIceMaterial()
        {
            if (iceMaterial == null) return;

            // Pulsing transparency effect to show ice movement
            float pulse = Mathf.Sin(Time.time * 0.2f) * 0.05f;
            Color currentColor = iceMaterial.color;
            currentColor.a = iceTransparency + pulse;
            iceMaterial.color = currentColor;
        }

        /// <summary>
        /// Start snowfall particle system
        /// </summary>
        private void StartSnowfall()
        {
            if (snowfallSystem == null) return;

            snowfallSystem.Play();

            // Adjust snowfall based on temperature
            var emission = snowfallSystem.emission;
            float snowRate = Mathf.Lerp(100f, 10f, Mathf.Clamp01((currentTemperature + 10f) / 20f));
            emission.rateOverTime = snowRate;

            Debug.Log($"[MuirGlacier] Snowfall started at {snowRate} particles/sec");
        }

        /// <summary>
        /// Start glacier ambient sounds
        /// </summary>
        private void StartGlacierAmbience()
        {
            if (glacierCreakingSound != null)
            {
                glacierCreakingSound.Play();
                glacierCreakingSound.volume = 0.3f;
            }

            if (meltWaterSound != null && currentTemperature > 0f)
            {
                meltWaterSound.Play();
                meltWaterSound.volume = Mathf.Clamp01(currentTemperature / 10f) * 0.5f;
            }
        }

        /// <summary>
        /// Update climate data overlay UI
        /// </summary>
        private void UpdateClimateOverlay()
        {
            // This would update a UI canvas showing current climate metrics
            // Implementation depends on UI structure
        }

        /// <summary>
        /// Scrub to a specific year in the time-lapse
        /// </summary>
        public void ScrubToYear(int year)
        {
            if (year < historicalStartYear || year > currentYear)
            {
                Debug.LogWarning($"[MuirGlacier] Year {year} out of range [{historicalStartYear}-{currentYear}]");
                return;
            }

            timeLapseYear = year;

            float yearProgress = (float)(year - historicalStartYear) / (currentYear - historicalStartYear);
            float retreatFactor = Mathf.Lerp(1.0f, 0.3f, yearProgress * yearProgress);

            targetGlacierScale = retreatFactor;
            UpdateClimateMetricsForYear(year);

            Debug.Log($"[MuirGlacier] Scrubbed to year {year}");
        }

        /// <summary>
        /// Toggle time-lapse playback
        /// </summary>
        public void ToggleTimeLapse()
        {
            if (isTimeLapsePlaying)
            {
                StopTimeLapse();
            }
            else
            {
                StartCoroutine(TimeLapseSimulation());
            }
        }

        /// <summary>
        /// Stop time-lapse simulation
        /// </summary>
        public void StopTimeLapse()
        {
            isTimeLapsePlaying = false;
            Debug.Log("[MuirGlacier] Time-lapse stopped");
        }

        /// <summary>
        /// Toggle climate data overlay
        /// </summary>
        public void ToggleClimateOverlay()
        {
            showClimateOverlay = !showClimateOverlay;
            Debug.Log($"[MuirGlacier] Climate overlay: {(showClimateOverlay ? "ON" : "OFF")}");
        }

        /// <summary>
        /// Get current climate metrics
        /// </summary>
        public (float temperature, float co2, float retreat) GetCurrentMetrics()
        {
            return (currentTemperature, currentCO2Level, glacialRetreatMeters);
        }

        /// <summary>
        /// Trigger educational content for a specific data point
        /// </summary>
        public void TriggerClimateDataPoint(int index)
        {
            if (climateDataPoints == null || index < 0 || index >= climateDataPoints.Length)
            {
                Debug.LogWarning($"[MuirGlacier] Invalid data point index: {index}");
                return;
            }

            ClimateDataPoint dataPoint = climateDataPoints[index];
            if (dataPoint != null && dataPoint.dataNode != null)
            {
                dataPoint.dataNode.TriggerNode();
                ScrubToYear(dataPoint.year);
                Debug.Log($"[MuirGlacier] Triggered data point: Year {dataPoint.year}");
            }
        }

        protected override void OnDrawGizmos()
        {
            base.OnDrawGizmos();

            // Draw glacier area
            if (glacierCenter != null)
            {
                Gizmos.color = new Color(0.7f, 0.85f, 0.95f, 0.3f);
                Gizmos.DrawWireSphere(glacierCenter.position, glacierRadius);

                // Draw glacier flow direction
                Gizmos.color = Color.cyan;
                Vector3 flowStart = glacierCenter.position;
                Vector3 flowEnd = flowStart + Vector3.forward * glacierRadius;
                Gizmos.DrawLine(flowStart, flowEnd);
                Gizmos.DrawWireSphere(flowEnd, 5f); // Terminus marker
            }

            // Draw climate data points
            if (climateDataPoints != null)
            {
                Gizmos.color = Color.yellow;
                foreach (ClimateDataPoint dataPoint in climateDataPoints)
                {
                    if (dataPoint != null && dataPoint.dataNode != null)
                    {
                        Vector3 pos = dataPoint.dataNode.transform.position;
                        Gizmos.DrawWireCube(pos, Vector3.one * 2f);
                        Gizmos.DrawLine(pos, pos + Vector3.up * 3f);
                    }
                }
            }
        }
    }

    /// <summary>
    /// Data structure for climate data points
    /// </summary>
    [System.Serializable]
    public class ClimateDataPoint
    {
        public int year;
        public float temperature; // Celsius
        public float co2Level; // PPM
        public float retreatMeters; // Glacier retreat in meters

        [TextArea(3, 10)]
        public string historicalContext;

        [TextArea(2, 5)]
        public string muirQuote;

        public EducationalNode dataNode;
        public AudioClip audioNarration;
        public Sprite graphicVisualization;
    }
}
