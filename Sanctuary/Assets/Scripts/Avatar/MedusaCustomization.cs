using UnityEngine;
using Unity.Netcode;

namespace Sanctuary.Avatar
{
    /// <summary>
    /// Handles customization of the Medusa jellyfish avatar
    /// Allows players to modify appearance: colors, tentacle length, transparency, etc.
    /// </summary>
    public class MedusaCustomization : NetworkBehaviour
    {
        [Header("References")]
        [SerializeField] private SkinnedMeshRenderer bellRenderer;
        [SerializeField] private Transform[] tentacles;
        [SerializeField] private Material customMaterial;

        [Header("Customization Options")]
        [SerializeField] private CustomizationPreset currentPreset;

        // Network variables for synchronization
        private NetworkVariable<Color> networkBellColor = new NetworkVariable<Color>(
            new Color(0.1f, 0.3f, 0.5f, 0.8f),
            NetworkVariableReadPermission.Everyone,
            NetworkVariableWritePermission.Owner
        );

        private NetworkVariable<Color> networkGlowColor = new NetworkVariable<Color>(
            Color.cyan,
            NetworkVariableReadPermission.Everyone,
            NetworkVariableWritePermission.Owner
        );

        private NetworkVariable<float> networkTransparency = new NetworkVariable<float>(
            0.7f,
            NetworkVariableReadPermission.Everyone,
            NetworkVariableWritePermission.Owner
        );

        private NetworkVariable<float> networkTentacleLength = new NetworkVariable<float>(
            1.0f,
            NetworkVariableReadPermission.Everyone,
            NetworkVariableWritePermission.Owner
        );

        // Shader property IDs
        private static readonly int ColorProperty = Shader.PropertyToID("_Color");
        private static readonly int EmissionColorProperty = Shader.PropertyToID("_EmissionColor");
        private static readonly int TransparencyProperty = Shader.PropertyToID("_Transparency");
        private static readonly int GlowIntensityProperty = Shader.PropertyToID("_GlowIntensity");

        private MaterialPropertyBlock propertyBlock;

        private void Awake()
        {
            propertyBlock = new MaterialPropertyBlock();

            if (bellRenderer == null)
            {
                bellRenderer = GetComponentInChildren<SkinnedMeshRenderer>();
            }

            // Apply default preset if available
            if (currentPreset != null)
            {
                ApplyPreset(currentPreset);
            }
        }

        public override void OnNetworkSpawn()
        {
            base.OnNetworkSpawn();

            // Subscribe to network variable changes
            networkBellColor.OnValueChanged += OnBellColorChanged;
            networkGlowColor.OnValueChanged += OnGlowColorChanged;
            networkTransparency.OnValueChanged += OnTransparencyChanged;
            networkTentacleLength.OnValueChanged += OnTentacleLengthChanged;

            // Apply current values
            ApplyCustomization();
        }

        public override void OnNetworkDespawn()
        {
            // Unsubscribe
            networkBellColor.OnValueChanged -= OnBellColorChanged;
            networkGlowColor.OnValueChanged -= OnGlowColorChanged;
            networkTransparency.OnValueChanged -= OnTransparencyChanged;
            networkTentacleLength.OnValueChanged -= OnTentacleLengthChanged;

            base.OnNetworkDespawn();
        }

        /// <summary>
        /// Set the bell (body) color
        /// </summary>
        public void SetBellColor(Color color)
        {
            if (IsOwner)
            {
                networkBellColor.Value = color;
            }
        }

        /// <summary>
        /// Set the bioluminescent glow color
        /// </summary>
        public void SetGlowColor(Color color)
        {
            if (IsOwner)
            {
                networkGlowColor.Value = color;
            }
        }

        /// <summary>
        /// Set transparency level (0 = opaque, 1 = fully transparent)
        /// </summary>
        public void SetTransparency(float transparency)
        {
            if (IsOwner)
            {
                networkTransparency.Value = Mathf.Clamp01(transparency);
            }
        }

        /// <summary>
        /// Set tentacle length multiplier
        /// </summary>
        public void SetTentacleLength(float lengthMultiplier)
        {
            if (IsOwner)
            {
                networkTentacleLength.Value = Mathf.Clamp(lengthMultiplier, 0.5f, 2.0f);
            }
        }

        /// <summary>
        /// Apply a customization preset
        /// </summary>
        public void ApplyPreset(CustomizationPreset preset)
        {
            if (preset == null || !IsOwner)
                return;

            SetBellColor(preset.bellColor);
            SetGlowColor(preset.glowColor);
            SetTransparency(preset.transparency);
            SetTentacleLength(preset.tentacleLength);

            Debug.Log($"[MedusaCustomization] Applied preset: {preset.presetName}");
        }

        /// <summary>
        /// Randomize avatar appearance
        /// </summary>
        public void Randomize()
        {
            if (!IsOwner)
                return;

            // Random bell color (blue/purple/teal spectrum)
            Color randomBell = new Color(
                Random.Range(0.1f, 0.5f),
                Random.Range(0.3f, 0.8f),
                Random.Range(0.5f, 1.0f),
                0.8f
            );

            // Random glow color (complementary)
            Color randomGlow = new Color(
                Random.Range(0.0f, 1.0f),
                Random.Range(0.5f, 1.0f),
                Random.Range(0.5f, 1.0f),
                1.0f
            );

            SetBellColor(randomBell);
            SetGlowColor(randomGlow);
            SetTransparency(Random.Range(0.5f, 0.9f));
            SetTentacleLength(Random.Range(0.8f, 1.5f));

            Debug.Log("[MedusaCustomization] Randomized avatar");
        }

        /// <summary>
        /// Apply all customization settings to the avatar
        /// </summary>
        private void ApplyCustomization()
        {
            ApplyColorCustomization();
            ApplyTentacleCustomization();
        }

        /// <summary>
        /// Apply color and transparency settings
        /// </summary>
        private void ApplyColorCustomization()
        {
            if (bellRenderer == null)
                return;

            bellRenderer.GetPropertyBlock(propertyBlock);

            propertyBlock.SetColor(ColorProperty, networkBellColor.Value);
            propertyBlock.SetColor(EmissionColorProperty, networkGlowColor.Value);
            propertyBlock.SetFloat(TransparencyProperty, networkTransparency.Value);

            bellRenderer.SetPropertyBlock(propertyBlock);
        }

        /// <summary>
        /// Apply tentacle length customization
        /// </summary>
        private void ApplyTentacleCustomization()
        {
            if (tentacles == null || tentacles.Length == 0)
                return;

            foreach (Transform tentacle in tentacles)
            {
                if (tentacle != null)
                {
                    Vector3 scale = tentacle.localScale;
                    scale.y = networkTentacleLength.Value;
                    tentacle.localScale = scale;
                }
            }
        }

        // Network variable change callbacks
        private void OnBellColorChanged(Color previousValue, Color newValue)
        {
            ApplyColorCustomization();
        }

        private void OnGlowColorChanged(Color previousValue, Color newValue)
        {
            ApplyColorCustomization();
        }

        private void OnTransparencyChanged(float previousValue, float newValue)
        {
            ApplyColorCustomization();
        }

        private void OnTentacleLengthChanged(float previousValue, float newValue)
        {
            ApplyTentacleCustomization();
        }

        /// <summary>
        /// Get current customization as a preset
        /// </summary>
        public CustomizationPreset GetCurrentCustomization()
        {
            CustomizationPreset preset = ScriptableObject.CreateInstance<CustomizationPreset>();
            preset.presetName = "Custom";
            preset.bellColor = networkBellColor.Value;
            preset.glowColor = networkGlowColor.Value;
            preset.transparency = networkTransparency.Value;
            preset.tentacleLength = networkTentacleLength.Value;
            return preset;
        }

#if UNITY_EDITOR
        // Editor testing
        [ContextMenu("Apply Random")]
        private void TestRandomize()
        {
            Randomize();
        }

        [ContextMenu("Reset to Default")]
        private void TestReset()
        {
            SetBellColor(new Color(0.1f, 0.3f, 0.5f, 0.8f));
            SetGlowColor(Color.cyan);
            SetTransparency(0.7f);
            SetTentacleLength(1.0f);
        }
#endif
    }

    /// <summary>
    /// Scriptable Object for storing customization presets
    /// </summary>
    [CreateAssetMenu(fileName = "MedusaPreset", menuName = "Sanctuary/Medusa Customization Preset")]
    public class CustomizationPreset : ScriptableObject
    {
        public string presetName = "Default";

        [Header("Colors")]
        public Color bellColor = new Color(0.1f, 0.3f, 0.5f, 0.8f);
        public Color glowColor = Color.cyan;

        [Header("Appearance")]
        [Range(0f, 1f)]
        public float transparency = 0.7f;

        [Header("Tentacles")]
        [Range(0.5f, 2.0f)]
        public float tentacleLength = 1.0f;

        [Header("Description")]
        [TextArea(3, 5)]
        public string description = "A beautiful jellyfish avatar";
    }
}
