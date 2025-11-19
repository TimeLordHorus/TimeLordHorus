using UnityEngine;

namespace Sanctuary.Biomes
{
    /// <summary>
    /// Represents an interactive educational content point within a Protected Biome.
    /// Triggers audio, text, or visual content when the player approaches.
    /// </summary>
    public class EducationalNode : MonoBehaviour
    {
        [Header("Node Settings")]
        [SerializeField] private string nodeName = "Educational Node";
        [SerializeField] [TextArea(3, 10)] private string contentText;
        [SerializeField] private NodeType nodeType = NodeType.ProximityTrigger;

        [Header("Audio Content")]
        [SerializeField] private AudioClip[] audioClips;
        [SerializeField] private bool playRandomClip = false;
        [SerializeField] private float audioVolume = 1f;

        [Header("Visual Content")]
        [SerializeField] private GameObject visualPrefab;
        [SerializeField] private Sprite contentImage;

        [Header("Trigger Settings")]
        [SerializeField] private float triggerRadius = 3f;
        [SerializeField] private bool triggerOnce = true;
        [SerializeField] private float cooldownTime = 5f;

        [Header("UI Display")]
        [SerializeField] private Canvas textCanvas;
        [SerializeField] private TMPro.TextMeshProUGUI textDisplay;

        private AudioSource audioSource;
        private bool hasTriggered = false;
        private float lastTriggerTime = 0f;
        private GameObject spawnedVisual;
        private Transform playerTransform;

        public enum NodeType
        {
            ProximityTrigger,
            InteractionTrigger,
            AlwaysActive
        }

        private void Awake()
        {
            SetupAudioSource();
            SetupTextDisplay();
            FindPlayer();
        }

        private void SetupAudioSource()
        {
            audioSource = gameObject.AddComponent<AudioSource>();
            audioSource.playOnAwake = false;
            audioSource.spatialBlend = 1f; // 3D audio
            audioSource.volume = audioVolume;
            audioSource.minDistance = 1f;
            audioSource.maxDistance = triggerRadius * 2f;
        }

        private void SetupTextDisplay()
        {
            if (textCanvas != null)
            {
                textCanvas.gameObject.SetActive(false);
            }

            if (textDisplay != null && !string.IsNullOrEmpty(contentText))
            {
                textDisplay.text = contentText;
            }
        }

        private void FindPlayer()
        {
            // Find the player's camera (typically the XR Rig camera)
            Camera mainCam = Camera.main;
            if (mainCam != null)
            {
                playerTransform = mainCam.transform;
            }
        }

        private void Update()
        {
            if (nodeType == NodeType.ProximityTrigger && playerTransform != null)
            {
                CheckProximity();
            }
        }

        private void CheckProximity()
        {
            float distance = Vector3.Distance(transform.position, playerTransform.position);

            if (distance <= triggerRadius)
            {
                if (!hasTriggered || (!triggerOnce && Time.time - lastTriggerTime > cooldownTime))
                {
                    TriggerNode();
                }
            }
        }

        /// <summary>
        /// Activate this educational node
        /// </summary>
        public void Activate()
        {
            gameObject.SetActive(true);

            if (nodeType == NodeType.AlwaysActive)
            {
                TriggerNode();
            }

            Debug.Log($"[EducationalNode] {nodeName} activated");
        }

        /// <summary>
        /// Trigger the node's content
        /// </summary>
        public void TriggerNode()
        {
            hasTriggered = true;
            lastTriggerTime = Time.time;

            // Play audio content
            if (audioClips != null && audioClips.Length > 0)
            {
                PlayAudioContent();
            }

            // Display text content
            if (!string.IsNullOrEmpty(contentText))
            {
                DisplayTextContent();
            }

            // Spawn visual content
            if (visualPrefab != null && spawnedVisual == null)
            {
                SpawnVisualContent();
            }

            Debug.Log($"[EducationalNode] {nodeName} triggered");
        }

        private void PlayAudioContent()
        {
            AudioClip clipToPlay;

            if (playRandomClip)
            {
                clipToPlay = audioClips[Random.Range(0, audioClips.Length)];
            }
            else
            {
                clipToPlay = audioClips[0];
            }

            if (clipToPlay != null)
            {
                audioSource.clip = clipToPlay;
                audioSource.Play();
                Debug.Log($"[EducationalNode] Playing audio: {clipToPlay.name}");
            }
        }

        private void DisplayTextContent()
        {
            if (textCanvas != null)
            {
                textCanvas.gameObject.SetActive(true);

                // Make canvas face the player
                if (playerTransform != null)
                {
                    Vector3 directionToPlayer = playerTransform.position - textCanvas.transform.position;
                    directionToPlayer.y = 0; // Keep canvas upright
                    textCanvas.transform.rotation = Quaternion.LookRotation(directionToPlayer);
                }

                // Auto-hide after audio finishes or after 10 seconds
                float hideDelay = audioSource.clip != null ? audioSource.clip.length : 10f;
                Invoke(nameof(HideTextDisplay), hideDelay);
            }
        }

        private void HideTextDisplay()
        {
            if (textCanvas != null)
            {
                textCanvas.gameObject.SetActive(false);
            }
        }

        private void SpawnVisualContent()
        {
            spawnedVisual = Instantiate(visualPrefab, transform.position, Quaternion.identity);
            spawnedVisual.transform.SetParent(transform);
            Debug.Log($"[EducationalNode] Spawned visual content: {visualPrefab.name}");
        }

        /// <summary>
        /// Deactivate this node
        /// </summary>
        public void Deactivate()
        {
            if (audioSource != null && audioSource.isPlaying)
            {
                audioSource.Stop();
            }

            if (textCanvas != null)
            {
                textCanvas.gameObject.SetActive(false);
            }

            if (spawnedVisual != null)
            {
                Destroy(spawnedVisual);
            }

            gameObject.SetActive(false);
        }

        /// <summary>
        /// Reset the node so it can be triggered again
        /// </summary>
        public void Reset()
        {
            hasTriggered = false;
            lastTriggerTime = 0f;

            if (spawnedVisual != null)
            {
                Destroy(spawnedVisual);
                spawnedVisual = null;
            }
        }

        private void OnDrawGizmosSelected()
        {
            // Visualize trigger radius
            Gizmos.color = new Color(0, 1, 1, 0.3f);
            Gizmos.DrawWireSphere(transform.position, triggerRadius);

            // Draw node icon
            Gizmos.color = Color.cyan;
            Gizmos.DrawCube(transform.position, Vector3.one * 0.3f);
        }
    }
}
