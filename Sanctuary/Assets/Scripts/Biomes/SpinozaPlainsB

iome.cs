using UnityEngine;
using System.Collections;

namespace Sanctuary.Biomes
{
    /// <summary>
    /// Spinoza Plains - Geometric Fractal Biome
    /// Educational biome inspired by Baruch Spinoza's Ethics and geometric philosophy
    /// Features procedural fractal landscapes and philosophical demonstrations
    /// </summary>
    public class SpinozaPlainsBiome : BiomeController
    {
        [Header("Spinoza Plains Specific")]
        [SerializeField] private Transform plainsCenter;
        [SerializeField] private float plainsRadius = 50f;

        [Header("Geometric Environment")]
        [SerializeField] private Material fractalMaterial;
        [SerializeField] private GameObject[] geometricStructures;
        [SerializeField] private float structureRotationSpeed = 5f;

        [Header("Philosophical Content")]
        [SerializeField] private EthicsProposition[] ethicsPropositions;
        [SerializeField] private GameObject geometricDemonstrationPrefab;

        [Header("Visual Effects")]
        [SerializeField] private Color primaryColor = new Color(0.8f, 0.4f, 0.2f);
        [SerializeField] private Color secondaryColor = new Color(0.2f, 0.6f, 0.8f);
        [SerializeField] private float colorTransitionSpeed = 0.5f;

        [Header("Procedural Generation")]
        [SerializeField] private bool enableProceduralGeneration = true;
        [SerializeField] private int fractalIterations = 5;
        [SerializeField] private float fractalScale = 1.0f;

        private float geometryAnimationTime = 0f;

        protected override void Awake()
        {
            // Set biome info
            biomeName = "The Spinoza Geometric Plains";
            biomeDescription = "A realm of pure geometric form inspired by Baruch Spinoza's Ethics. " +
                               "Experience philosophical propositions through interactive geometric demonstrations.";

            // Set environmental defaults
            fogColor = new Color(0.9f, 0.85f, 0.75f);
            fogDensity = 0.008f;

            base.Awake();

            SetupGeometricEnvironment();
        }

        /// <summary>
        /// Configure geometric environment
        /// </summary>
        private void SetupGeometricEnvironment()
        {
            // Setup lighting for geometric clarity
            Light directionalLight = RenderSettings.sun;
            if (directionalLight != null)
            {
                directionalLight.color = new Color(1f, 0.95f, 0.9f);
                directionalLight.intensity = 1.5f;
                directionalLight.transform.rotation = Quaternion.Euler(60f, -45f, 0f);
                directionalLight.shadows = LightShadows.Soft;
            }

            // Setup ambient light for geometric definition
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.4f, 0.4f, 0.45f);

            // Setup skybox color
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;

            Debug.Log("[SpinozaPlains] Geometric environment configured");
        }

        protected override void Start()
        {
            base.Start();

            // Generate procedural fractal structures
            if (enableProceduralGeneration)
            {
                StartCoroutine(GenerateFractalStructures());
            }

            // Setup Ethics propositions
            SetupEthicsPropositions();

            // Animate geometric structures
            StartCoroutine(AnimateGeometricStructures());
        }

        private void Update()
        {
            geometryAnimationTime += Time.deltaTime;

            // Animated fog color transition
            AnimateFogColors();

            // Rotate geometric structures
            RotateGeometricStructures();
        }

        /// <summary>
        /// Setup Ethics proposition educational nodes
        /// </summary>
        private void SetupEthicsPropositions()
        {
            if (ethicsPropositions == null || ethicsPropositions.Length == 0)
            {
                Debug.LogWarning("[SpinozaPlains] No Ethics propositions configured");
                return;
            }

            foreach (EthicsProposition proposition in ethicsPropositions)
            {
                if (proposition != null && proposition.propositionNode != null)
                {
                    proposition.propositionNode.Activate();

                    // Spawn geometric demonstration
                    if (geometricDemonstrationPrefab != null)
                    {
                        Vector3 spawnPos = proposition.propositionNode.transform.position + Vector3.up * 2f;
                        GameObject demo = Instantiate(geometricDemonstrationPrefab, spawnPos, Quaternion.identity);
                        demo.transform.SetParent(proposition.propositionNode.transform);

                        // Apply proposition-specific material/colors
                        Renderer renderer = demo.GetComponent<Renderer>();
                        if (renderer != null && proposition.demonstrationColor != Color.clear)
                        {
                            renderer.material.color = proposition.demonstrationColor;
                        }
                    }
                }
            }

            Debug.Log($"[SpinozaPlains] Configured {ethicsPropositions.Length} Ethics propositions");
        }

        /// <summary>
        /// Generate procedural fractal structures
        /// </summary>
        private IEnumerator GenerateFractalStructures()
        {
            Debug.Log("[SpinozaPlains] Generating fractal structures...");

            // Generate in a grid pattern
            int gridSize = 5;
            float spacing = 10f;

            for (int x = -gridSize; x <= gridSize; x++)
            {
                for (int z = -gridSize; z <= gridSize; z++)
                {
                    Vector3 position = new Vector3(x * spacing, 0, z * spacing);

                    // Skip center area (reserved for main structures)
                    if (position.magnitude < 15f)
                        continue;

                    // Create fractal structure
                    CreateFractalStructure(position);

                    // Yield to prevent frame drops
                    if (x % 2 == 0 && z % 2 == 0)
                        yield return null;
                }
            }

            Debug.Log("[SpinozaPlains] Fractal generation complete");
        }

        /// <summary>
        /// Create a single fractal structure
        /// </summary>
        private void CreateFractalStructure(Vector3 position)
        {
            GameObject structure = new GameObject($"FractalStructure_{position.x}_{position.z}");
            structure.transform.position = position;
            structure.transform.SetParent(transform);

            // Add basic geometric shapes in fractal pattern
            CreateFractalIteration(structure.transform, fractalIterations, fractalScale);
        }

        /// <summary>
        /// Recursive fractal iteration
        /// </summary>
        private void CreateFractalIteration(Transform parent, int iterations, float scale)
        {
            if (iterations <= 0)
                return;

            // Create central cube
            GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cube.transform.SetParent(parent);
            cube.transform.localPosition = Vector3.zero;
            cube.transform.localScale = Vector3.one * scale;

            // Apply fractal material
            if (fractalMaterial != null)
            {
                cube.GetComponent<Renderer>().material = fractalMaterial;
            }

            // Create child iterations at corners
            float childScale = scale * 0.4f;
            Vector3[] offsets = {
                new Vector3(1, 1, 1),
                new Vector3(-1, 1, 1),
                new Vector3(1, 1, -1),
                new Vector3(-1, 1, -1)
            };

            foreach (Vector3 offset in offsets)
            {
                GameObject child = new GameObject("FractalChild");
                child.transform.SetParent(parent);
                child.transform.localPosition = offset.normalized * scale;

                CreateFractalIteration(child.transform, iterations - 1, childScale);
            }
        }

        /// <summary>
        /// Animate fog colors in a cycle
        /// </summary>
        private void AnimateFogColors()
        {
            float t = Mathf.PingPong(geometryAnimationTime * colorTransitionSpeed, 1f);
            Color animatedFogColor = Color.Lerp(primaryColor, secondaryColor, t);
            RenderSettings.fogColor = animatedFogColor;
        }

        /// <summary>
        /// Rotate geometric structures for visual interest
        /// </summary>
        private void RotateGeometricStructures()
        {
            if (geometricStructures == null)
                return;

            foreach (GameObject structure in geometricStructures)
            {
                if (structure != null)
                {
                    structure.transform.Rotate(Vector3.up, structureRotationSpeed * Time.deltaTime);
                    structure.transform.Rotate(Vector3.right, structureRotationSpeed * 0.5f * Time.deltaTime);
                }
            }
        }

        /// <summary>
        /// Animate geometric structures with scale pulsing
        /// </summary>
        private IEnumerator AnimateGeometricStructures()
        {
            while (true)
            {
                if (geometricStructures != null)
                {
                    foreach (GameObject structure in geometricStructures)
                    {
                        if (structure != null)
                        {
                            float pulse = Mathf.Sin(geometryAnimationTime * 2f) * 0.1f + 1f;
                            structure.transform.localScale = Vector3.one * pulse;
                        }
                    }
                }

                yield return new WaitForSeconds(0.1f);
            }
        }

        /// <summary>
        /// Trigger a specific Ethics proposition
        /// </summary>
        public void TriggerEthicsProposition(int propositionIndex)
        {
            if (ethicsPropositions == null || propositionIndex < 0 || propositionIndex >= ethicsPropositions.Length)
            {
                Debug.LogWarning($"[SpinozaPlains] Invalid proposition index: {propositionIndex}");
                return;
            }

            EthicsProposition proposition = ethicsPropositions[propositionIndex];
            if (proposition != null && proposition.propositionNode != null)
            {
                proposition.propositionNode.TriggerNode();
                Debug.Log($"[SpinozaPlains] Triggered proposition: {proposition.propositionTitle}");
            }
        }

        /// <summary>
        /// Get distance to plains center
        /// </summary>
        public float GetDistanceToCenter(Vector3 position)
        {
            if (plainsCenter == null)
                return float.MaxValue;

            return Vector3.Distance(position, plainsCenter.position);
        }

        protected override void OnDrawGizmos()
        {
            base.OnDrawGizmos();

            // Draw plains area
            if (plainsCenter != null)
            {
                Gizmos.color = new Color(0.8f, 0.4f, 0.2f, 0.3f);
                Gizmos.DrawWireSphere(plainsCenter.position, plainsRadius);

                // Draw geometric grid
                Gizmos.color = new Color(0.2f, 0.6f, 0.8f, 0.2f);
                int gridSize = 5;
                float spacing = 10f;

                for (int x = -gridSize; x <= gridSize; x++)
                {
                    Vector3 start = new Vector3(x * spacing, 0, -gridSize * spacing);
                    Vector3 end = new Vector3(x * spacing, 0, gridSize * spacing);
                    Gizmos.DrawLine(start, end);
                }

                for (int z = -gridSize; z <= gridSize; z++)
                {
                    Vector3 start = new Vector3(-gridSize * spacing, 0, z * spacing);
                    Vector3 end = new Vector3(gridSize * spacing, 0, z * spacing);
                    Gizmos.DrawLine(start, end);
                }
            }

            // Draw Ethics proposition nodes
            if (ethicsPropositions != null)
            {
                Gizmos.color = Color.yellow;
                foreach (EthicsProposition proposition in ethicsPropositions)
                {
                    if (proposition != null && proposition.propositionNode != null)
                    {
                        Vector3 pos = proposition.propositionNode.transform.position;
                        Gizmos.DrawWireCube(pos, Vector3.one);
                        Gizmos.DrawLine(pos, pos + Vector3.up * 2f);
                    }
                }
            }
        }
    }

    /// <summary>
    /// Data structure for Ethics proposition content
    /// </summary>
    [System.Serializable]
    public class EthicsProposition
    {
        public string propositionTitle;
        public int partNumber; // Part of Ethics (I-V)
        public int propositionNumber;

        [TextArea(3, 10)]
        public string propositionText;

        [TextArea(2, 5)]
        public string demonstration;

        public EducationalNode propositionNode;
        public AudioClip audioReading;
        public Color demonstrationColor = Color.white;
    }
}
