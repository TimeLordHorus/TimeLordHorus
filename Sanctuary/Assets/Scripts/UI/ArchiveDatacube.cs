using UnityEngine;
using TMPro;
using System.Collections;
using Sanctuary.Core;

namespace Sanctuary.UI
{
    /// <summary>
    /// 3D Datacube visualization for Archive.org content
    /// Displays books and texts as interactive holographic cubes in VR space
    /// </summary>
    public class ArchiveDatacube : MonoBehaviour
    {
        [Header("Cube Configuration")]
        [SerializeField] private Vector3 cubeSize = new Vector3(0.5f, 0.5f, 0.5f);
        [SerializeField] private Material datacubeMaterial;
        [SerializeField] private Color primaryColor = new Color(0.2f, 0.6f, 1.0f, 0.7f);
        [SerializeField] private Color secondaryColor = new Color(0.8f, 0.4f, 1.0f, 0.7f);

        [Header("Text Display")]
        [SerializeField] private GameObject textPanelPrefab;
        [SerializeField] private float textPanelDistance = 1.0f;
        [SerializeField] private int textPreviewLength = 500;

        [Header("Animation")]
        [SerializeField] private float rotationSpeed = 20f;
        [SerializeField] private float pulseSpeed = 1.0f;
        [SerializeField] private float pulseAmplitude = 0.1f;
        [SerializeField] private bool enableParticles = true;

        [Header("Audio")]
        [SerializeField] private AudioSource audioSource;
        [SerializeField] private AudioClip hoverSound;
        [SerializeField] private AudioClip selectSound;

        // State
        private ArchiveItem itemData;
        private GameObject cubeObject;
        private GameObject textPanel;
        private ParticleSystem particles;
        private bool isExpanded = false;
        private bool isHovered = false;
        private float animationTime = 0f;

        // Components
        private MeshRenderer cubeRenderer;
        private TextMeshProUGUI titleText;
        private TextMeshProUGUI authorText;
        private TextMeshProUGUI descriptionText;
        private TextMeshProUGUI previewText;

        private void Start()
        {
            CreateDatacube();
            SetupInteraction();
            StartCoroutine(AnimateDatacube());
        }

        /// <summary>
        /// Initialize datacube with Archive.org item data
        /// </summary>
        public void Initialize(ArchiveItem item)
        {
            itemData = item;

            if (titleText != null && item != null)
            {
                titleText.text = item.title;

                if (authorText != null)
                    authorText.text = item.creator;

                if (descriptionText != null)
                    descriptionText.text = item.description;

                Debug.Log($"[Datacube] Initialized with: {item.title}");
            }
        }

        /// <summary>
        /// Create the physical datacube object
        /// </summary>
        private void CreateDatacube()
        {
            // Create cube mesh
            cubeObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cubeObject.name = "Datacube";
            cubeObject.transform.SetParent(transform);
            cubeObject.transform.localPosition = Vector3.zero;
            cubeObject.transform.localScale = cubeSize;

            // Apply material
            cubeRenderer = cubeObject.GetComponent<MeshRenderer>();
            if (datacubeMaterial != null)
            {
                cubeRenderer.material = datacubeMaterial;
            }

            cubeRenderer.material.color = primaryColor;

            // Make it transparent
            SetTransparency(0.7f);

            // Add particle system
            if (enableParticles)
            {
                CreateParticles();
            }

            Debug.Log("[Datacube] Physical cube created");
        }

        /// <summary>
        /// Create particle effects around the cube
        /// </summary>
        private void CreateParticles()
        {
            GameObject particleObj = new GameObject("Particles");
            particleObj.transform.SetParent(transform);
            particleObj.transform.localPosition = Vector3.zero;

            particles = particleObj.AddComponent<ParticleSystem>();

            var main = particles.main;
            main.startSize = 0.02f;
            main.startSpeed = 0.1f;
            main.startLifetime = 2.0f;
            main.maxParticles = 50;
            main.simulationSpace = ParticleSystemSimulationSpace.World;

            var emission = particles.emission;
            emission.rateOverTime = 10f;

            var shape = particles.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = cubeSize;

            var colorOverLifetime = particles.colorOverLifetime;
            colorOverLifetime.enabled = true;

            Gradient gradient = new Gradient();
            gradient.SetKeys(
                new GradientColorKey[] {
                    new GradientColorKey(primaryColor, 0.0f),
                    new GradientColorKey(secondaryColor, 1.0f)
                },
                new GradientAlphaKey[] {
                    new GradientAlphaKey(1.0f, 0.0f),
                    new GradientAlphaKey(0.0f, 1.0f)
                }
            );

            colorOverLifetime.color = gradient;
        }

        /// <summary>
        /// Setup VR interaction
        /// </summary>
        private void SetupInteraction()
        {
            // Add collider for interaction
            if (cubeObject.GetComponent<Collider>() == null)
            {
                cubeObject.AddComponent<BoxCollider>();
            }

            // Add rigidbody for XR interaction
            Rigidbody rb = cubeObject.AddComponent<Rigidbody>();
            rb.useGravity = false;
            rb.isKinematic = true;

            // Add XR grab interactable (if XR Interaction Toolkit is available)
            #if UNITY_XR_INTERACTION_TOOLKIT
            var grabInteractable = cubeObject.AddComponent<UnityEngine.XR.Interaction.Toolkit.XRGrabInteractable>();
            grabInteractable.selectEntered.AddListener(OnSelect);
            grabInteractable.hoverEntered.AddListener(OnHoverEnter);
            grabInteractable.hoverExited.AddListener(OnHoverExit);
            #endif
        }

        /// <summary>
        /// Animate datacube rotation and pulsing
        /// </summary>
        private IEnumerator AnimateDatacube()
        {
            while (true)
            {
                animationTime += Time.deltaTime;

                // Rotate cube
                cubeObject.transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime);
                cubeObject.transform.Rotate(Vector3.right, rotationSpeed * 0.3f * Time.deltaTime);

                // Pulse effect
                float pulse = Mathf.Sin(animationTime * pulseSpeed) * pulseAmplitude;
                cubeObject.transform.localScale = cubeSize * (1f + pulse);

                // Color oscillation
                if (isHovered)
                {
                    float t = Mathf.PingPong(animationTime * 2f, 1f);
                    cubeRenderer.material.color = Color.Lerp(primaryColor, secondaryColor, t);
                }
                else
                {
                    cubeRenderer.material.color = primaryColor;
                }

                yield return null;
            }
        }

        /// <summary>
        /// Handle hover enter event
        /// </summary>
        private void OnHoverEnter(object args)
        {
            isHovered = true;

            if (audioSource != null && hoverSound != null)
            {
                audioSource.PlayOneShot(hoverSound, 0.3f);
            }

            // Show title preview
            ShowTitlePreview();

            Debug.Log($"[Datacube] Hovered: {itemData?.title}");
        }

        /// <summary>
        /// Handle hover exit event
        /// </summary>
        private void OnHoverExit(object args)
        {
            isHovered = false;
            HideTitlePreview();
        }

        /// <summary>
        /// Handle select/grab event
        /// </summary>
        private void OnSelect(object args)
        {
            if (audioSource != null && selectSound != null)
            {
                audioSource.PlayOneShot(selectSound, 0.5f);
            }

            if (!isExpanded)
            {
                ExpandDatacube();
            }
            else
            {
                CollapseDatacube();
            }

            Debug.Log($"[Datacube] Selected: {itemData?.title}");
        }

        /// <summary>
        /// Expand datacube to show full content
        /// </summary>
        private async void ExpandDatacube()
        {
            isExpanded = true;

            // Animate cube expansion
            StartCoroutine(AnimateExpansion());

            // Create text panel
            if (textPanelPrefab != null)
            {
                Vector3 panelPosition = transform.position + Camera.main.transform.forward * textPanelDistance;
                textPanel = Instantiate(textPanelPrefab, panelPosition, Quaternion.identity);
                textPanel.transform.SetParent(transform);

                // Face the camera
                textPanel.transform.LookAt(Camera.main.transform);
                textPanel.transform.Rotate(0, 180, 0);

                // Setup text content
                titleText = textPanel.transform.Find("TitleText")?.GetComponent<TextMeshProUGUI>();
                authorText = textPanel.transform.Find("AuthorText")?.GetComponent<TextMeshProUGUI>();
                descriptionText = textPanel.transform.Find("DescriptionText")?.GetComponent<TextMeshProUGUI>();
                previewText = textPanel.transform.Find("PreviewText")?.GetComponent<TextMeshProUGUI>();

                if (titleText != null) titleText.text = itemData?.title ?? "Unknown Title";
                if (authorText != null) authorText.text = itemData?.creator ?? "Unknown Author";
                if (descriptionText != null) descriptionText.text = itemData?.description ?? "";

                // Load text preview
                if (previewText != null && itemData != null)
                {
                    previewText.text = "Loading preview...";

                    ArchiveClient archiveClient = ArchiveClient.Instance;
                    if (archiveClient != null)
                    {
                        string preview = await archiveClient.GetTextPreview(itemData.identifier, textPreviewLength);
                        previewText.text = preview ?? "Preview not available";
                    }
                }
            }

            Debug.Log("[Datacube] Expanded");
        }

        /// <summary>
        /// Collapse datacube back to compact form
        /// </summary>
        private void CollapseDatacube()
        {
            isExpanded = false;

            // Animate cube collapse
            StartCoroutine(AnimateCollapse());

            // Destroy text panel
            if (textPanel != null)
            {
                Destroy(textPanel);
                textPanel = null;
            }

            Debug.Log("[Datacube] Collapsed");
        }

        /// <summary>
        /// Animate expansion
        /// </summary>
        private IEnumerator AnimateExpansion()
        {
            Vector3 startScale = cubeSize;
            Vector3 endScale = cubeSize * 1.5f;
            float duration = 0.3f;
            float elapsed = 0f;

            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                cubeSize = Vector3.Lerp(startScale, endScale, t);
                yield return null;
            }
        }

        /// <summary>
        /// Animate collapse
        /// </summary>
        private IEnumerator AnimateCollapse()
        {
            Vector3 startScale = cubeSize;
            Vector3 endScale = new Vector3(0.5f, 0.5f, 0.5f);
            float duration = 0.3f;
            float elapsed = 0f;

            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / duration;
                cubeSize = Vector3.Lerp(startScale, endScale, t);
                yield return null;
            }
        }

        /// <summary>
        /// Show title preview on hover
        /// </summary>
        private void ShowTitlePreview()
        {
            // TODO: Create floating title text above cube
        }

        /// <summary>
        /// Hide title preview
        /// </summary>
        private void HideTitlePreview()
        {
            // TODO: Hide floating title text
        }

        /// <summary>
        /// Set cube transparency
        /// </summary>
        private void SetTransparency(float alpha)
        {
            if (cubeRenderer != null)
            {
                Color color = cubeRenderer.material.color;
                color.a = alpha;
                cubeRenderer.material.color = color;
            }
        }

        /// <summary>
        /// Get the Archive item data
        /// </summary>
        public ArchiveItem GetItemData()
        {
            return itemData;
        }

        private void OnDestroy()
        {
            if (textPanel != null)
            {
                Destroy(textPanel);
            }
        }

#if UNITY_EDITOR
        private void OnDrawGizmos()
        {
            // Draw cube bounds
            Gizmos.color = new Color(0.2f, 0.6f, 1.0f, 0.5f);
            Gizmos.DrawWireCube(transform.position, cubeSize);

            // Draw text panel position
            if (isExpanded && Camera.main != null)
            {
                Vector3 panelPosition = transform.position + Camera.main.transform.forward * textPanelDistance;
                Gizmos.color = Color.yellow;
                Gizmos.DrawWireCube(panelPosition, new Vector3(0.5f, 0.7f, 0.1f));
                Gizmos.DrawLine(transform.position, panelPosition);
            }
        }
#endif
    }
}
