using UnityEngine;
using UnityEngine.SceneManagement;

namespace Sanctuary.Core
{
    /// <summary>
    /// Central Hub Manager
    /// Manages "The Station" - the main social lobby and portal hub
    /// Solarpunk-inspired design with portals to biomes and creation realms
    /// </summary>
    public class CentralHubManager : MonoBehaviour
    {
        [Header("Hub Settings")]
        [Tooltip("Hub name displayed to players")]
        [SerializeField] private string hubName = "The Station";

        [Tooltip("Maximum concurrent players in hub")]
        [SerializeField] private int maxPlayers = 32;

        [Header("Portal Settings")]
        [Tooltip("Portal to Thoreau Woods biome")]
        [SerializeField] private Portal thoreauWoodsPortal;

        [Tooltip("Portal to Spinoza Plains biome")]
        [SerializeField] private Portal spinozaPlainsPortal;

        [Tooltip("Portal to Muir Glacier biome")]
        [SerializeField] private Portal muirGlacierPortal;

        [Tooltip("Portal to Creation Realm")]
        [SerializeField] private Portal creationRealmPortal;

        [Header("Environment Settings")]
        [Tooltip("Time of day (0-24)")]
        [SerializeField] private float timeOfDay = 12f;

        [Tooltip("Enable dynamic weather")]
        [SerializeField] private bool enableWeather = true;

        [Tooltip("Archive data visualization frequency (seconds)")]
        [SerializeField] private float archiveUpdateFrequency = 5f;

        // State
        private int currentPlayerCount = 0;
        private float lastArchiveUpdate = 0f;

        [System.Serializable]
        public class Portal
        {
            public string destinationScene;
            public Transform portalTransform;
            public GameObject portalEffect;
            public bool isActive = true;
        }

        private void Start()
        {
            Initialize();
        }

        private void Update()
        {
            UpdateEnvironment();
            UpdateArchiveVisualization();
        }

        /// <summary>
        /// Initialize the Central Hub
        /// </summary>
        private void Initialize()
        {
            Debug.Log($"[CentralHubManager] Initializing {hubName}...");

            // Setup portals
            SetupPortals();

            // Setup environment
            SetupEnvironment();

            // Setup archive integration
            SetupArchiveIntegration();

            Debug.Log($"[CentralHubManager] {hubName} initialized successfully");
        }

        /// <summary>
        /// Setup portal system
        /// </summary>
        private void SetupPortals()
        {
            SetupPortal(thoreauWoodsPortal, "Thoreau Woods");
            SetupPortal(spinozaPlainsPortal, "Spinoza Plains");
            SetupPortal(muirGlacierPortal, "Muir Glacier");
            SetupPortal(creationRealmPortal, "Creation Realm");

            Debug.Log("[CentralHubManager] Portals setup complete");
        }

        /// <summary>
        /// Setup individual portal
        /// </summary>
        private void SetupPortal(Portal portal, string name)
        {
            if (portal == null || portal.portalTransform == null)
            {
                Debug.LogWarning($"[CentralHubManager] {name} portal not configured");
                return;
            }

            // Add portal interaction component
            PortalInteraction portalInteraction = portal.portalTransform.gameObject.GetComponent<PortalInteraction>();
            if (portalInteraction == null)
            {
                portalInteraction = portal.portalTransform.gameObject.AddComponent<PortalInteraction>();
            }

            portalInteraction.destinationScene = portal.destinationScene;
            portalInteraction.portalEffect = portal.portalEffect;
            portalInteraction.SetActive(portal.isActive);

            Debug.Log($"[CentralHubManager] {name} portal configured");
        }

        /// <summary>
        /// Setup environment (lighting, weather, etc.)
        /// </summary>
        private void SetupEnvironment()
        {
            // Set time of day
            UpdateTimeOfDay(timeOfDay);

            // Enable weather system
            if (enableWeather)
            {
                // Weather system implementation would go here
                Debug.Log("[CentralHubManager] Weather system enabled");
            }
        }

        /// <summary>
        /// Setup archive data integration
        /// </summary>
        private void SetupArchiveIntegration()
        {
            // Archive integration would connect to Archive.org API
            Debug.Log("[CentralHubManager] Archive integration setup");
        }

        /// <summary>
        /// Update environment (time, weather, etc.)
        /// </summary>
        private void UpdateEnvironment()
        {
            // Update time of day, weather, etc.
            // Implementation depends on day/night cycle system
        }

        /// <summary>
        /// Update archive data visualization
        /// </summary>
        private void UpdateArchiveVisualization()
        {
            if (Time.time - lastArchiveUpdate < archiveUpdateFrequency)
                return;

            lastArchiveUpdate = Time.time;

            // Update 3D datacube visualization
            // This would fetch and visualize archive data
        }

        /// <summary>
        /// Update time of day
        /// </summary>
        private void UpdateTimeOfDay(float hour)
        {
            timeOfDay = Mathf.Clamp(hour, 0f, 24f);

            // Update directional light rotation
            Light directionalLight = RenderSettings.sun;
            if (directionalLight != null)
            {
                // Rotate sun based on time (simple implementation)
                float rotation = (timeOfDay / 24f) * 360f - 90f;
                directionalLight.transform.rotation = Quaternion.Euler(rotation, 170f, 0f);

                // Adjust light intensity based on time
                float intensity = Mathf.Clamp01(1f - Mathf.Abs((timeOfDay - 12f) / 12f));
                directionalLight.intensity = intensity * 1.5f;
            }
        }

        /// <summary>
        /// Teleport player to destination
        /// </summary>
        public void TeleportToScene(string sceneName)
        {
            if (string.IsNullOrEmpty(sceneName))
            {
                Debug.LogWarning("[CentralHubManager] Invalid scene name");
                return;
            }

            Debug.Log($"[CentralHubManager] Teleporting to {sceneName}...");
            SceneManager.LoadScene(sceneName);
        }

        /// <summary>
        /// Player entered hub
        /// </summary>
        public void OnPlayerEnter()
        {
            currentPlayerCount++;
            Debug.Log($"[CentralHubManager] Player entered. Total: {currentPlayerCount}/{maxPlayers}");
        }

        /// <summary>
        /// Player left hub
        /// </summary>
        public void OnPlayerExit()
        {
            currentPlayerCount = Mathf.Max(0, currentPlayerCount - 1);
            Debug.Log($"[CentralHubManager] Player exited. Total: {currentPlayerCount}/{maxPlayers}");
        }

        /// <summary>
        /// Get current player count
        /// </summary>
        public int GetPlayerCount()
        {
            return currentPlayerCount;
        }

        /// <summary>
        /// Check if hub is full
        /// </summary>
        public bool IsFull()
        {
            return currentPlayerCount >= maxPlayers;
        }

#if UNITY_EDITOR
        private void OnDrawGizmos()
        {
            // Draw portal positions
            DrawPortalGizmo(thoreauWoodsPortal, Color.green);
            DrawPortalGizmo(spinozaPlainsPortal, Color.blue);
            DrawPortalGizmo(muirGlacierPortal, Color.cyan);
            DrawPortalGizmo(creationRealmPortal, Color.yellow);
        }

        private void DrawPortalGizmo(Portal portal, Color color)
        {
            if (portal != null && portal.portalTransform != null)
            {
                Gizmos.color = color;
                Gizmos.DrawWireSphere(portal.portalTransform.position, 1f);
                Gizmos.DrawRay(portal.portalTransform.position, portal.portalTransform.forward * 2f);
            }
        }
#endif
    }

    /// <summary>
    /// Portal interaction component
    /// Handles player interaction with portals
    /// </summary>
    public class PortalInteraction : MonoBehaviour
    {
        public string destinationScene;
        public GameObject portalEffect;
        private bool isActive = true;

        private void OnTriggerEnter(Collider other)
        {
            if (!isActive)
                return;

            // Check if player entered
            if (other.CompareTag("Player"))
            {
                TeleportPlayer();
            }
        }

        private void TeleportPlayer()
        {
            if (string.IsNullOrEmpty(destinationScene))
            {
                Debug.LogWarning("[PortalInteraction] No destination scene set");
                return;
            }

            // Find hub manager
            CentralHubManager hubManager = FindObjectOfType<CentralHubManager>();
            if (hubManager != null)
            {
                hubManager.TeleportToScene(destinationScene);
            }
            else
            {
                // Fallback to direct scene load
                SceneManager.LoadScene(destinationScene);
            }
        }

        public void SetActive(bool active)
        {
            isActive = active;

            if (portalEffect != null)
            {
                portalEffect.SetActive(active);
            }
        }
    }
}
