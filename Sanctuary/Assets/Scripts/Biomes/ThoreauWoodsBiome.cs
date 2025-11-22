using UnityEngine;
using System.Collections;

namespace Sanctuary.Biomes
{
    /// <summary>
    /// Thoreau Woods - New England Forest Biome
    /// Educational biome inspired by Henry David Thoreau and Walden Pond
    /// Focuses on themes of simplicity, nature observation, and self-reliance
    /// </summary>
    public class ThoreauWoodsBiome : BiomeController
    {
        [Header("Thoreau Woods Specific")]
        [SerializeField] private Transform waldenPondCenter;
        [SerializeField] private float pondRadius = 20f;

        [Header("Lighting")]
        [SerializeField] private Light sunLight;
        [SerializeField] private float dawnHour = 6f;
        [SerializeField] private float duskHour = 18f;
        [SerializeField] private bool enableDayNightCycle = false;

        [Header("Weather")]
        [SerializeField] private ParticleSystem rainSystem;
        [SerializeField] private float rainChance = 0.2f;
        [SerializeField] private float rainDuration = 120f;

        [Header("Wildlife")]
        [SerializeField] private AudioClip[] birdCalls;
        [SerializeField] private float birdCallFrequency = 30f;
        private float lastBirdCallTime = 0f;

        [Header("Walden Content")]
        [SerializeField] private WaldenChapter[] waldenChapters;

        private bool isRaining = false;

        protected override void Awake()
        {
            // Set biome info
            biomeName = "The Thoreau Woods";
            biomeDescription = "A New England forest inspired by Henry David Thoreau's Walden. " +
                               "Explore themes of simplicity, self-reliance, and harmony with nature.";

            // Set environmental defaults
            fogColor = new Color(0.7f, 0.8f, 0.85f, 1f);
            fogDensity = 0.015f;

            base.Awake();

            SetupForestEnvironment();
        }

        /// <summary>
        /// Configure forest-specific environment
        /// </summary>
        private void SetupForestEnvironment()
        {
            // Setup sun light
            if (sunLight == null)
            {
                GameObject sunObj = GameObject.Find("Directional Light");
                if (sunObj != null)
                {
                    sunLight = sunObj.GetComponent<Light>();
                }
            }

            if (sunLight != null)
            {
                sunLight.color = new Color(1f, 0.95f, 0.8f); // Warm natural sunlight
                sunLight.intensity = 1.2f;
                sunLight.transform.rotation = Quaternion.Euler(45f, -30f, 0f);
            }

            // Setup ambient light
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 0.8f;

            Debug.Log("[ThoreauWoods] Forest environment configured");
        }

        protected override void Start()
        {
            base.Start();

            // Random chance of starting with rain
            if (Random.value < rainChance)
            {
                StartCoroutine(StartRain());
            }

            // Setup Walden chapters as educational nodes
            SetupWaldenChapters();
        }

        private void Update()
        {
            // Day/night cycle
            if (enableDayNightCycle)
            {
                UpdateDayNightCycle();
            }

            // Random bird calls
            if (Time.time - lastBirdCallTime > birdCallFrequency)
            {
                PlayRandomBirdCall();
                lastBirdCallTime = Time.time;
            }
        }

        /// <summary>
        /// Setup Walden chapter content nodes
        /// </summary>
        private void SetupWaldenChapters()
        {
            if (waldenChapters == null || waldenChapters.Length == 0)
            {
                Debug.LogWarning("[ThoreauWoods] No Walden chapters configured");
                return;
            }

            foreach (WaldenChapter chapter in waldenChapters)
            {
                if (chapter != null && chapter.chapterNode != null)
                {
                    chapter.chapterNode.Activate();
                }
            }

            Debug.Log($"[ThoreauWoods] Configured {waldenChapters.Length} Walden chapters");
        }

        /// <summary>
        /// Update day/night cycle lighting
        /// </summary>
        private void UpdateDayNightCycle()
        {
            if (sunLight == null)
                return;

            // Simple day/night cycle (24-hour cycle = 1200 seconds = 20 minutes)
            float cycleDuration = 1200f;
            float currentTime = (Time.time % cycleDuration) / cycleDuration * 24f;

            // Calculate sun angle
            float sunAngle = ((currentTime - 6f) / 12f) * 180f;
            sunLight.transform.rotation = Quaternion.Euler(sunAngle - 90f, -30f, 0f);

            // Adjust light intensity based on time
            if (currentTime >= dawnHour && currentTime <= duskHour)
            {
                // Daytime
                float dayProgress = (currentTime - dawnHour) / (duskHour - dawnHour);
                sunLight.intensity = Mathf.Sin(dayProgress * Mathf.PI) * 1.2f + 0.3f;
            }
            else
            {
                // Nighttime
                sunLight.intensity = 0.1f;
            }

            // Adjust fog based on time of day
            if (currentTime >= 5f && currentTime <= 8f)
            {
                // Morning mist
                RenderSettings.fogDensity = 0.03f;
            }
            else
            {
                RenderSettings.fogDensity = 0.015f;
            }
        }

        /// <summary>
        /// Play a random bird call
        /// </summary>
        private void PlayRandomBirdCall()
        {
            if (birdCalls == null || birdCalls.Length == 0)
                return;

            AudioClip randomCall = birdCalls[Random.Range(0, birdCalls.Length)];

            if (randomCall != null)
            {
                // Play bird call at a random position near the player
                Vector3 birdPosition = Camera.main.transform.position + Random.insideUnitSphere * 20f;
                birdPosition.y = Random.Range(5f, 15f); // Birds are in the air

                AudioSource.PlayClipAtPoint(randomCall, birdPosition, 0.5f);
            }
        }

        /// <summary>
        /// Start rain weather effect
        /// </summary>
        private IEnumerator StartRain()
        {
            if (rainSystem == null || isRaining)
                yield break;

            isRaining = true;

            Debug.Log("[ThoreauWoods] Rain starting");

            // Enable rain particle system
            rainSystem.Play();

            // Adjust lighting for rain
            if (sunLight != null)
            {
                float originalIntensity = sunLight.intensity;
                sunLight.intensity = originalIntensity * 0.6f;
            }

            // Wait for rain duration
            yield return new WaitForSeconds(rainDuration);

            // Stop rain
            rainSystem.Stop();

            if (sunLight != null)
            {
                sunLight.intensity = 1.2f;
            }

            isRaining = false;

            Debug.Log("[ThoreauWoods] Rain stopped");
        }

        /// <summary>
        /// Get distance to Walden Pond center
        /// </summary>
        public float GetDistanceToPond(Vector3 position)
        {
            if (waldenPondCenter == null)
                return float.MaxValue;

            return Vector3.Distance(position, waldenPondCenter.position);
        }

        /// <summary>
        /// Check if position is near Walden Pond
        /// </summary>
        public bool IsNearPond(Vector3 position)
        {
            return GetDistanceToPond(position) <= pondRadius;
        }

        /// <summary>
        /// Trigger a specific Walden chapter
        /// </summary>
        public void TriggerWaldenChapter(int chapterIndex)
        {
            if (waldenChapters == null || chapterIndex < 0 || chapterIndex >= waldenChapters.Length)
            {
                Debug.LogWarning($"[ThoreauWoods] Invalid chapter index: {chapterIndex}");
                return;
            }

            WaldenChapter chapter = waldenChapters[chapterIndex];
            if (chapter != null && chapter.chapterNode != null)
            {
                chapter.chapterNode.TriggerNode();
                Debug.Log($"[ThoreauWoods] Triggered chapter: {chapter.chapterTitle}");
            }
        }

        protected override void OnDrawGizmos()
        {
            base.OnDrawGizmos();

            // Draw Walden Pond area
            if (waldenPondCenter != null)
            {
                Gizmos.color = new Color(0, 0.5f, 1f, 0.3f);
                Gizmos.DrawWireSphere(waldenPondCenter.position, pondRadius);

                // Draw surface
                Gizmos.color = new Color(0, 0.5f, 1f, 0.1f);
                Vector3 pondSurface = waldenPondCenter.position;
                pondSurface.y = 0; // Ground level
                Gizmos.DrawSphere(pondSurface, pondRadius);
            }

            // Draw Walden chapter nodes
            if (waldenChapters != null)
            {
                Gizmos.color = Color.yellow;
                foreach (WaldenChapter chapter in waldenChapters)
                {
                    if (chapter != null && chapter.chapterNode != null)
                    {
                        Gizmos.DrawCube(chapter.chapterNode.transform.position, Vector3.one * 0.5f);
                    }
                }
            }
        }
    }

    /// <summary>
    /// Data structure for Walden chapter content
    /// </summary>
    [System.Serializable]
    public class WaldenChapter
    {
        public string chapterTitle;
        [TextArea(2, 5)]
        public string chapterExcerpt;
        public EducationalNode chapterNode;
        public AudioClip audioReading;
    }
}
