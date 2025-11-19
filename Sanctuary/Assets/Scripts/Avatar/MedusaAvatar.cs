using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

namespace Sanctuary.Avatar
{
    /// <summary>
    /// Main controller for the Medusa Jellyfish avatar.
    /// Handles physics-based floating locomotion, bioluminescent shader reactions,
    /// and tentacle dynamics.
    /// </summary>
    public class MedusaAvatar : MonoBehaviour
    {
        [Header("Avatar Components")]
        [SerializeField] private SkinnedMeshRenderer bellMeshRenderer;
        [SerializeField] private Transform[] tentacles;
        [SerializeField] private ParticleSystem bioluminescentParticles;

        [Header("Movement Settings")]
        [SerializeField] private float floatSpeed = 2f;
        [SerializeField] private float floatAmplitude = 0.5f;
        [SerializeField] private float rotationSpeed = 1f;

        [Header("Audio Reactivity")]
        [SerializeField] private AudioSource voiceInput;
        [SerializeField] private float glowMinIntensity = 0.2f;
        [SerializeField] private float glowMaxIntensity = 2f;
        [SerializeField] private float audioSensitivity = 5f;

        [Header("Shader Properties")]
        [SerializeField] private Material bioluminescentMaterial;
        private MaterialPropertyBlock propertyBlock;
        private static readonly int EmissionColorProperty = Shader.PropertyToID("_EmissionColor");
        private static readonly int GlowIntensityProperty = Shader.PropertyToID("_GlowIntensity");

        [Header("Tentacle Physics")]
        [SerializeField] private float tentacleGravity = -2f;
        [SerializeField] private float tentacleDamping = 0.9f;
        [SerializeField] private int verletIterations = 3;

        // Internal state
        private Vector3[] tentacleVelocities;
        private float currentGlowIntensity;
        private float floatTimer;

        private void Awake()
        {
            InitializeComponents();
            InitializeTentacles();
        }

        private void InitializeComponents()
        {
            propertyBlock = new MaterialPropertyBlock();

            if (bellMeshRenderer == null)
            {
                bellMeshRenderer = GetComponentInChildren<SkinnedMeshRenderer>();
            }

            if (voiceInput == null)
            {
                voiceInput = GetComponent<AudioSource>();
            }

            currentGlowIntensity = glowMinIntensity;
        }

        private void InitializeTentacles()
        {
            if (tentacles == null || tentacles.Length == 0)
            {
                Debug.LogWarning("No tentacles assigned to MedusaAvatar");
                return;
            }

            tentacleVelocities = new Vector3[tentacles.Length];
            for (int i = 0; i < tentacleVelocities.Length; i++)
            {
                tentacleVelocities[i] = Vector3.zero;
            }
        }

        private void Update()
        {
            UpdateFloatingMotion();
            UpdateAudioReactivity();
            UpdateBioluminescentShader();
        }

        private void FixedUpdate()
        {
            UpdateTentaclePhysics();
        }

        /// <summary>
        /// Handles the floating locomotion using sine wave motion
        /// </summary>
        private void UpdateFloatingMotion()
        {
            floatTimer += Time.deltaTime * floatSpeed;

            // Gentle vertical floating motion
            float verticalOffset = Mathf.Sin(floatTimer) * floatAmplitude;
            Vector3 targetPosition = transform.position;
            targetPosition.y += verticalOffset * Time.deltaTime;

            // Subtle rotation sway
            float rotationOffset = Mathf.Sin(floatTimer * 0.5f) * 15f;
            Quaternion targetRotation = Quaternion.Euler(0, rotationOffset, 0);

            transform.position = targetPosition;
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                targetRotation,
                Time.deltaTime * rotationSpeed
            );
        }

        /// <summary>
        /// Analyzes voice input and adjusts glow intensity
        /// </summary>
        private void UpdateAudioReactivity()
        {
            if (voiceInput == null || !voiceInput.isPlaying)
            {
                // Fade back to minimum when not speaking
                currentGlowIntensity = Mathf.Lerp(
                    currentGlowIntensity,
                    glowMinIntensity,
                    Time.deltaTime * 2f
                );
                return;
            }

            // Get audio volume
            float[] samples = new float[256];
            voiceInput.GetOutputData(samples, 0);

            float sum = 0f;
            foreach (float sample in samples)
            {
                sum += Mathf.Abs(sample);
            }
            float averageVolume = sum / samples.Length;

            // Map volume to glow intensity
            float targetIntensity = Mathf.Lerp(
                glowMinIntensity,
                glowMaxIntensity,
                averageVolume * audioSensitivity
            );

            currentGlowIntensity = Mathf.Lerp(
                currentGlowIntensity,
                targetIntensity,
                Time.deltaTime * 10f
            );
        }

        /// <summary>
        /// Updates the bioluminescent shader with current glow intensity
        /// </summary>
        private void UpdateBioluminescentShader()
        {
            if (bellMeshRenderer == null || bioluminescentMaterial == null)
                return;

            bellMeshRenderer.GetPropertyBlock(propertyBlock);
            propertyBlock.SetFloat(GlowIntensityProperty, currentGlowIntensity);

            Color emissionColor = Color.cyan * currentGlowIntensity;
            propertyBlock.SetColor(EmissionColorProperty, emissionColor);

            bellMeshRenderer.SetPropertyBlock(propertyBlock);
        }

        /// <summary>
        /// Simulates tentacle physics using Verlet integration
        /// </summary>
        private void UpdateTentaclePhysics()
        {
            if (tentacles == null || tentacles.Length == 0)
                return;

            Vector3 movementVelocity = GetComponent<Rigidbody>()?.velocity ?? Vector3.zero;

            for (int i = 0; i < tentacles.Length; i++)
            {
                if (tentacles[i] == null)
                    continue;

                // Apply gravity and movement drag
                Vector3 force = Vector3.up * tentacleGravity;
                force -= movementVelocity * 0.5f;

                // Update velocity
                tentacleVelocities[i] += force * Time.fixedDeltaTime;
                tentacleVelocities[i] *= tentacleDamping;

                // Apply position offset
                Vector3 offset = tentacleVelocities[i] * Time.fixedDeltaTime;
                tentacles[i].localPosition += offset;

                // Constraint: keep tentacles within reasonable distance
                float maxDistance = 2f;
                if (tentacles[i].localPosition.magnitude > maxDistance)
                {
                    tentacles[i].localPosition = tentacles[i].localPosition.normalized * maxDistance;
                    tentacleVelocities[i] *= 0.5f; // Dampen on constraint
                }
            }
        }

        /// <summary>
        /// Public method to set glow intensity (e.g., from network sync)
        /// </summary>
        public void SetGlowIntensity(float intensity)
        {
            currentGlowIntensity = Mathf.Clamp(intensity, glowMinIntensity, glowMaxIntensity);
        }

        /// <summary>
        /// Get current glow intensity (for network sync)
        /// </summary>
        public float GetGlowIntensity()
        {
            return currentGlowIntensity;
        }

        private void OnDrawGizmosSelected()
        {
            // Visualize tentacle attachment points
            if (tentacles != null)
            {
                Gizmos.color = Color.cyan;
                foreach (Transform tentacle in tentacles)
                {
                    if (tentacle != null)
                    {
                        Gizmos.DrawWireSphere(tentacle.position, 0.1f);
                        Gizmos.DrawLine(transform.position, tentacle.position);
                    }
                }
            }
        }
    }
}
