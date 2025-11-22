using UnityEngine;
using System.Collections.Generic;

namespace Sanctuary.Performance
{
    /// <summary>
    /// Component attached to individual objects to manage their LOD state
    /// Automatically adjusts mesh quality, material complexity, and component activity
    /// </summary>
    [RequireComponent(typeof(MeshRenderer))]
    public class LODObject : MonoBehaviour
    {
        [Header("LOD Meshes")]
        [SerializeField] private Mesh ultraDetailMesh;
        [SerializeField] private Mesh highDetailMesh;
        [SerializeField] private Mesh mediumDetailMesh;
        [SerializeField] private Mesh lowDetailMesh;

        [Header("LOD Materials")]
        [SerializeField] private Material ultraDetailMaterial;
        [SerializeField] private Material highDetailMaterial;
        [SerializeField] private Material mediumDetailMaterial;
        [SerializeField] private Material lowDetailMaterial;

        [Header("Component Management")]
        [SerializeField] private bool disableComponentsAtLowLOD = true;
        [SerializeField] private Behaviour[] componentsToDisable; // ParticleSystems, Lights, etc.

        [Header("Shadow Settings")]
        [SerializeField] private bool adjustShadows = true;
        [SerializeField] private UnityEngine.Rendering.ShadowCastingMode ultraShadowMode = UnityEngine.Rendering.ShadowCastingMode.On;
        [SerializeField] private UnityEngine.Rendering.ShadowCastingMode highShadowMode = UnityEngine.Rendering.ShadowCastingMode.On;
        [SerializeField] private UnityEngine.Rendering.ShadowCastingMode mediumShadowMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        [SerializeField] private UnityEngine.Rendering.ShadowCastingMode lowShadowMode = UnityEngine.Rendering.ShadowCastingMode.Off;

        [Header("Auto-Configuration")]
        [SerializeField] private bool autoRegisterWithLODSystem = true;
        [SerializeField] private bool autoGenerateLODs = false;
        [SerializeField] private float[] lodReductionFactors = { 1.0f, 0.7f, 0.4f, 0.2f }; // Ultra, High, Med, Low

        // Components
        private MeshFilter meshFilter;
        private MeshRenderer meshRenderer;
        private LODSystem lodSystem;

        // State
        private LODLevel currentLevel = LODLevel.Ultra;
        private float currentDistance = 0f;
        private bool isInitialized = false;

        private void Awake()
        {
            // Get components
            meshFilter = GetComponent<MeshFilter>();
            meshRenderer = GetComponent<MeshRenderer>();

            if (meshFilter == null || meshRenderer == null)
            {
                Debug.LogError($"[LODObject] Missing MeshFilter or MeshRenderer on {gameObject.name}");
                return;
            }

            // Auto-generate LOD meshes if enabled
            if (autoGenerateLODs && ultraDetailMesh == null)
            {
                ultraDetailMesh = meshFilter.sharedMesh;
                GenerateLODMeshes();
            }

            // Set default meshes if not assigned
            if (ultraDetailMesh == null && meshFilter.sharedMesh != null)
            {
                ultraDetailMesh = meshFilter.sharedMesh;
            }

            // Copy materials if not assigned
            if (ultraDetailMaterial == null && meshRenderer.sharedMaterial != null)
            {
                ultraDetailMaterial = meshRenderer.sharedMaterial;
            }

            isInitialized = true;
        }

        private void Start()
        {
            // Register with LOD system
            if (autoRegisterWithLODSystem)
            {
                lodSystem = LODSystem.Instance;

                if (lodSystem != null)
                {
                    lodSystem.RegisterObject(this);
                }
                else
                {
                    Debug.LogWarning($"[LODObject] LODSystem not found for {gameObject.name}");
                }
            }
        }

        private void OnDestroy()
        {
            // Unregister from LOD system
            if (lodSystem != null)
            {
                lodSystem.UnregisterObject(this);
            }
        }

        /// <summary>
        /// Set the LOD level for this object
        /// </summary>
        public void SetLODLevel(LODLevel level, float distance)
        {
            if (!isInitialized) return;

            // Update state
            LODLevel previousLevel = currentLevel;
            currentLevel = level;
            currentDistance = distance;

            // Only update if level changed
            if (previousLevel == level) return;

            // Apply LOD changes
            ApplyLOD(level);
        }

        /// <summary>
        /// Apply LOD changes to object
        /// </summary>
        private void ApplyLOD(LODLevel level)
        {
            switch (level)
            {
                case LODLevel.Ultra:
                    ApplyUltraDetail();
                    break;

                case LODLevel.High:
                    ApplyHighDetail();
                    break;

                case LODLevel.Medium:
                    ApplyMediumDetail();
                    break;

                case LODLevel.Low:
                    ApplyLowDetail();
                    break;

                case LODLevel.Culled:
                    ApplyCulled();
                    break;
            }
        }

        private void ApplyUltraDetail()
        {
            if (ultraDetailMesh != null && meshFilter != null)
                meshFilter.sharedMesh = ultraDetailMesh;

            if (ultraDetailMaterial != null && meshRenderer != null)
                meshRenderer.sharedMaterial = ultraDetailMaterial;

            if (adjustShadows && meshRenderer != null)
                meshRenderer.shadowCastingMode = ultraShadowMode;

            EnableComponents(true);
            meshRenderer.enabled = true;
        }

        private void ApplyHighDetail()
        {
            Mesh mesh = highDetailMesh != null ? highDetailMesh : ultraDetailMesh;
            if (mesh != null && meshFilter != null)
                meshFilter.sharedMesh = mesh;

            Material mat = highDetailMaterial != null ? highDetailMaterial : ultraDetailMaterial;
            if (mat != null && meshRenderer != null)
                meshRenderer.sharedMaterial = mat;

            if (adjustShadows && meshRenderer != null)
                meshRenderer.shadowCastingMode = highShadowMode;

            EnableComponents(true);
            meshRenderer.enabled = true;
        }

        private void ApplyMediumDetail()
        {
            Mesh mesh = mediumDetailMesh != null ? mediumDetailMesh : (highDetailMesh != null ? highDetailMesh : ultraDetailMesh);
            if (mesh != null && meshFilter != null)
                meshFilter.sharedMesh = mesh;

            Material mat = mediumDetailMaterial != null ? mediumDetailMaterial : (highDetailMaterial != null ? highDetailMaterial : ultraDetailMaterial);
            if (mat != null && meshRenderer != null)
                meshRenderer.sharedMaterial = mat;

            if (adjustShadows && meshRenderer != null)
                meshRenderer.shadowCastingMode = mediumShadowMode;

            EnableComponents(true);
            meshRenderer.enabled = true;
        }

        private void ApplyLowDetail()
        {
            Mesh mesh = lowDetailMesh != null ? lowDetailMesh : mediumDetailMesh;
            if (mesh == null) mesh = ultraDetailMesh;

            if (mesh != null && meshFilter != null)
                meshFilter.sharedMesh = mesh;

            Material mat = lowDetailMaterial != null ? lowDetailMaterial : mediumDetailMaterial;
            if (mat == null) mat = ultraDetailMaterial;

            if (mat != null && meshRenderer != null)
                meshRenderer.sharedMaterial = mat;

            if (adjustShadows && meshRenderer != null)
                meshRenderer.shadowCastingMode = lowShadowMode;

            EnableComponents(false);
            meshRenderer.enabled = true;
        }

        private void ApplyCulled()
        {
            meshRenderer.enabled = false;
            EnableComponents(false);
        }

        /// <summary>
        /// Enable/disable additional components based on LOD
        /// </summary>
        private void EnableComponents(bool enable)
        {
            if (!disableComponentsAtLowLOD || componentsToDisable == null)
                return;

            foreach (var component in componentsToDisable)
            {
                if (component != null)
                {
                    component.enabled = enable;
                }
            }
        }

        /// <summary>
        /// Auto-generate LOD meshes by decimating the original mesh
        /// NOTE: This is a simplified version - in production, use Unity's LOD Group or external tools
        /// </summary>
        private void GenerateLODMeshes()
        {
            if (ultraDetailMesh == null)
            {
                Debug.LogWarning($"[LODObject] No ultra detail mesh to generate LODs from: {gameObject.name}");
                return;
            }

            // For now, just reuse the same mesh at different LOD levels
            // In production, you'd use mesh decimation algorithms or pre-generated LODs
            highDetailMesh = ultraDetailMesh;
            mediumDetailMesh = ultraDetailMesh;
            lowDetailMesh = ultraDetailMesh;

            Debug.Log($"[LODObject] Auto-generated LOD meshes for {gameObject.name}");

            // TODO: Implement actual mesh decimation
            // This would involve:
            // 1. Vertex decimation (edge collapse)
            // 2. Triangle reduction
            // 3. Preserving UV coordinates
            // 4. Maintaining mesh normals
        }

        /// <summary>
        /// Get current LOD level
        /// </summary>
        public LODLevel GetCurrentLevel()
        {
            return currentLevel;
        }

        /// <summary>
        /// Get current distance from viewer
        /// </summary>
        public float GetCurrentDistance()
        {
            return currentDistance;
        }

        /// <summary>
        /// Manually set specific LOD meshes
        /// </summary>
        public void SetLODMeshes(Mesh ultra, Mesh high, Mesh medium, Mesh low)
        {
            ultraDetailMesh = ultra;
            highDetailMesh = high;
            mediumDetailMesh = medium;
            lowDetailMesh = low;
        }

        /// <summary>
        /// Manually set specific LOD materials
        /// </summary>
        public void SetLODMaterials(Material ultra, Material high, Material medium, Material low)
        {
            ultraDetailMaterial = ultra;
            highDetailMaterial = high;
            mediumDetailMaterial = medium;
            lowDetailMaterial = low;
        }

#if UNITY_EDITOR
        private void OnDrawGizmos()
        {
            // Draw LOD level indicator
            Color levelColor = GetLODLevelColor();
            Gizmos.color = levelColor;
            Gizmos.DrawWireSphere(transform.position, 0.5f);

            // Draw distance text
            if (UnityEditor.Selection.activeGameObject == gameObject)
            {
                UnityEditor.Handles.Label(transform.position + Vector3.up,
                    $"LOD: {currentLevel}\nDist: {currentDistance:F1}m");
            }
        }

        private Color GetLODLevelColor()
        {
            switch (currentLevel)
            {
                case LODLevel.Ultra:
                    return Color.green;
                case LODLevel.High:
                    return Color.yellow;
                case LODLevel.Medium:
                    return new Color(1f, 0.5f, 0f); // Orange
                case LODLevel.Low:
                    return Color.red;
                case LODLevel.Culled:
                    return Color.gray;
                default:
                    return Color.white;
            }
        }

        [ContextMenu("Force Ultra Detail")]
        private void EditorForceUltra()
        {
            SetLODLevel(LODLevel.Ultra, 0f);
        }

        [ContextMenu("Force High Detail")]
        private void EditorForceHigh()
        {
            SetLODLevel(LODLevel.High, 10f);
        }

        [ContextMenu("Force Medium Detail")]
        private void EditorForceMedium()
        {
            SetLODLevel(LODLevel.Medium, 20f);
        }

        [ContextMenu("Force Low Detail")]
        private void EditorForceLow()
        {
            SetLODLevel(LODLevel.Low, 40f);
        }

        [ContextMenu("Force Culled")]
        private void EditorForceCulled()
        {
            SetLODLevel(LODLevel.Culled, 60f);
        }
#endif
    }
}
