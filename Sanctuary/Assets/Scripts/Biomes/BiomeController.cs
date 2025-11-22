using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Sanctuary.Biomes
{
    /// <summary>
    /// Base class for all Protected Biome controllers.
    /// Handles player entry/exit, environmental setup, and educational content triggers.
    /// </summary>
    public abstract class BiomeController : MonoBehaviour
    {
        [Header("Biome Info")]
        [SerializeField] protected string biomeName = "Unknown Biome";
        [SerializeField] [TextArea] protected string biomeDescription;
        [SerializeField] protected Sprite biomeIcon;

        [Header("Environment")]
        [SerializeField] protected AudioClip ambienceLoop;
        [SerializeField] protected float ambienceFadeTime = 2f;
        [SerializeField] protected Color fogColor = Color.white;
        [SerializeField] protected float fogDensity = 0.01f;

        [Header("Entry/Exit")]
        [SerializeField] protected Transform playerSpawnPoint;
        [SerializeField] protected GameObject exitPortal;
        [SerializeField] protected string hubSceneName = "CentralHub";

        [Header("Content Nodes")]
        [SerializeField] protected EducationalNode[] educationalNodes;

        protected AudioSource ambienceSource;
        protected bool playerInBiome = false;

        protected virtual void Awake()
        {
            SetupAudioSource();
            SetupEnvironment();
        }

        protected virtual void Start()
        {
            OnPlayerEnter();
        }

        /// <summary>
        /// Setup the audio source for ambience
        /// </summary>
        private void SetupAudioSource()
        {
            ambienceSource = gameObject.AddComponent<AudioSource>();
            ambienceSource.loop = true;
            ambienceSource.playOnAwake = false;
            ambienceSource.spatialBlend = 0f; // 2D ambience
            ambienceSource.volume = 0f;

            if (ambienceLoop != null)
            {
                ambienceSource.clip = ambienceLoop;
            }
        }

        /// <summary>
        /// Configure environmental settings (fog, lighting, etc.)
        /// </summary>
        protected virtual void SetupEnvironment()
        {
            RenderSettings.fog = true;
            RenderSettings.fogColor = fogColor;
            RenderSettings.fogDensity = fogDensity;

            Debug.Log($"[Biome] Environment configured for {biomeName}");
        }

        /// <summary>
        /// Called when a player enters the biome
        /// </summary>
        protected virtual void OnPlayerEnter()
        {
            playerInBiome = true;

            // Spawn player at designated point
            if (playerSpawnPoint != null)
            {
                Transform playerTransform = Camera.main?.transform.parent;
                if (playerTransform != null)
                {
                    playerTransform.position = playerSpawnPoint.position;
                    playerTransform.rotation = playerSpawnPoint.rotation;
                }
            }

            // Fade in ambience
            if (ambienceSource != null && ambienceLoop != null)
            {
                StartCoroutine(FadeInAmbience());
            }

            // Activate educational nodes
            ActivateEducationalNodes();

            Debug.Log($"[Biome] Player entered {biomeName}");
        }

        /// <summary>
        /// Called when a player exits the biome
        /// </summary>
        protected virtual void OnPlayerExit()
        {
            playerInBiome = false;

            // Fade out ambience
            if (ambienceSource != null)
            {
                StartCoroutine(FadeOutAmbience());
            }

            Debug.Log($"[Biome] Player exited {biomeName}");
        }

        /// <summary>
        /// Fade in ambience audio
        /// </summary>
        private IEnumerator FadeInAmbience()
        {
            ambienceSource.Play();
            float elapsed = 0f;

            while (elapsed < ambienceFadeTime)
            {
                elapsed += Time.deltaTime;
                ambienceSource.volume = Mathf.Lerp(0f, 1f, elapsed / ambienceFadeTime);
                yield return null;
            }

            ambienceSource.volume = 1f;
        }

        /// <summary>
        /// Fade out ambience audio
        /// </summary>
        private IEnumerator FadeOutAmbience()
        {
            float startVolume = ambienceSource.volume;
            float elapsed = 0f;

            while (elapsed < ambienceFadeTime)
            {
                elapsed += Time.deltaTime;
                ambienceSource.volume = Mathf.Lerp(startVolume, 0f, elapsed / ambienceFadeTime);
                yield return null;
            }

            ambienceSource.volume = 0f;
            ambienceSource.Stop();
        }

        /// <summary>
        /// Activate all educational content nodes in the biome
        /// </summary>
        protected virtual void ActivateEducationalNodes()
        {
            if (educationalNodes == null || educationalNodes.Length == 0)
            {
                Debug.LogWarning($"[Biome] No educational nodes configured for {biomeName}");
                return;
            }

            foreach (EducationalNode node in educationalNodes)
            {
                if (node != null)
                {
                    node.Activate();
                }
            }

            Debug.Log($"[Biome] Activated {educationalNodes.Length} educational nodes");
        }

        /// <summary>
        /// Return to the Central Hub
        /// </summary>
        public void ReturnToHub()
        {
            OnPlayerExit();
            StartCoroutine(LoadHubScene());
        }

        /// <summary>
        /// Load the Central Hub scene
        /// </summary>
        private IEnumerator LoadHubScene()
        {
            // Fade out or show loading screen here
            yield return new WaitForSeconds(1f);

            SceneManager.LoadScene(hubSceneName);
        }

        /// <summary>
        /// Get biome information
        /// </summary>
        public BiomeInfo GetBiomeInfo()
        {
            return new BiomeInfo
            {
                name = biomeName,
                description = biomeDescription,
                icon = biomeIcon
            };
        }

        protected virtual void OnDrawGizmos()
        {
            // Visualize spawn point
            if (playerSpawnPoint != null)
            {
                Gizmos.color = Color.green;
                Gizmos.DrawWireSphere(playerSpawnPoint.position, 0.5f);
                Gizmos.DrawLine(playerSpawnPoint.position, playerSpawnPoint.position + playerSpawnPoint.forward * 2f);
            }

            // Visualize educational nodes
            if (educationalNodes != null)
            {
                Gizmos.color = Color.cyan;
                foreach (EducationalNode node in educationalNodes)
                {
                    if (node != null && node.transform != null)
                    {
                        Gizmos.DrawWireCube(node.transform.position, Vector3.one * 0.5f);
                    }
                }
            }
        }
    }

    /// <summary>
    /// Data structure for biome information
    /// </summary>
    [System.Serializable]
    public struct BiomeInfo
    {
        public string name;
        public string description;
        public Sprite icon;
    }
}
