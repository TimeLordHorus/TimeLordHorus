using System;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Events;
using Sanctuary.AI;

namespace Sanctuary.Core
{
    /// <summary>
    /// The Loom - Creation Management System
    /// Orchestrates the complete workflow: Voice/Text Input → AI Generation → 3D Model Spawn
    /// </summary>
    public class CreationManager : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private TextTo3DClient textTo3DClient;
        [SerializeField] private RuntimeModelImporter modelImporter;

        [Header("User Settings")]
        [SerializeField] private string userId = "user_default";
        [SerializeField] private string defaultQuality = "medium";
        [SerializeField] private string defaultStyle = "realistic";

        [Header("Spawn Settings")]
        [SerializeField] private bool spawnInFrontOfPlayer = true;
        [SerializeField] private float spawnDistance = 2.5f;

        [Header("Events")]
        public UnityEvent<string> OnGenerationStarted;
        public UnityEvent<GameObject> OnModelSpawned;
        public UnityEvent<string> OnGenerationFailed;

        // State
        private bool isGenerating = false;
        private GameObject lastSpawnedModel;

        private static CreationManager instance;
        public static CreationManager Instance => instance;

        private void Awake()
        {
            if (instance == null)
            {
                instance = this;
            }
            else
            {
                Destroy(gameObject);
                return;
            }

            // Auto-find references if not set
            if (textTo3DClient == null)
            {
                textTo3DClient = FindObjectOfType<TextTo3DClient>();
                if (textTo3DClient == null)
                {
                    GameObject clientObj = new GameObject("TextTo3DClient");
                    clientObj.transform.SetParent(transform);
                    textTo3DClient = clientObj.AddComponent<TextTo3DClient>();
                }
            }

            if (modelImporter == null)
            {
                modelImporter = FindObjectOfType<RuntimeModelImporter>();
                if (modelImporter == null)
                {
                    GameObject importerObj = new GameObject("RuntimeModelImporter");
                    importerObj.transform.SetParent(transform);
                    modelImporter = importerObj.AddComponent<RuntimeModelImporter>();
                }
            }
        }

        /// <summary>
        /// Create a 3D model from a text prompt
        /// Complete workflow: Generate → Download → Spawn
        /// </summary>
        public async Task<GameObject> CreateFromText(
            string prompt,
            string quality = null,
            string style = null
        )
        {
            if (isGenerating)
            {
                Debug.LogWarning("[CreationManager] Generation already in progress");
                return null;
            }

            if (string.IsNullOrEmpty(prompt))
            {
                Debug.LogError("[CreationManager] Prompt cannot be empty");
                OnGenerationFailed?.Invoke("Prompt cannot be empty");
                return null;
            }

            isGenerating = true;

            try
            {
                Debug.Log($"[CreationManager] Starting creation: '{prompt}'");
                OnGenerationStarted?.Invoke(prompt);

                // Step 1: Send generation request to backend
                ModelGenerationResponse response = await textTo3DClient.GenerateModel(
                    prompt,
                    userId,
                    quality ?? defaultQuality,
                    style ?? defaultStyle
                );

                if (response.status != "success")
                {
                    throw new Exception($"Generation failed with status: {response.status}");
                }

                Debug.Log($"[CreationManager] Model generated: {response.generation_id}");
                Debug.Log($"[CreationManager] Model URL: {response.model_url}");

                // Step 2: Calculate spawn position
                Vector3 spawnPosition = CalculateSpawnPosition();

                // Step 3: Import and spawn the model
                GameObject spawnedModel = await modelImporter.ImportAndSpawnModel(
                    response.model_url,
                    spawnPosition
                );

                if (spawnedModel != null)
                {
                    // Store reference
                    lastSpawnedModel = spawnedModel;

                    // Tag with metadata
                    CreationMetadata metadata = spawnedModel.AddComponent<CreationMetadata>();
                    metadata.generationId = response.generation_id;
                    metadata.prompt = prompt;
                    metadata.createdAt = response.created_at;
                    metadata.polycount = response.estimated_polycount;

                    Debug.Log($"[CreationManager] Model spawned successfully at {spawnPosition}");
                    OnModelSpawned?.Invoke(spawnedModel);

                    return spawnedModel;
                }
                else
                {
                    throw new Exception("Model import failed");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[CreationManager] Creation failed: {e.Message}");
                OnGenerationFailed?.Invoke(e.Message);
                return null;
            }
            finally
            {
                isGenerating = false;
            }
        }

        /// <summary>
        /// Create from voice input (uses Whisper transcription first)
        /// </summary>
        public async Task<GameObject> CreateFromVoice(AudioClip audioClip)
        {
            // TODO: Implement voice-to-text transcription
            // 1. Convert AudioClip to WAV/MP3
            // 2. Send to Whisper API via backend
            // 3. Get transcription
            // 4. Call CreateFromText with transcription

            Debug.LogWarning("[CreationManager] Voice input not yet implemented");
            return await CreateFromText("Placeholder: Voice input coming soon");
        }

        /// <summary>
        /// Calculate where to spawn the model
        /// </summary>
        private Vector3 CalculateSpawnPosition()
        {
            if (spawnInFrontOfPlayer && Camera.main != null)
            {
                Transform cameraTransform = Camera.main.transform;
                Vector3 forward = cameraTransform.forward;
                forward.y = 0; // Keep on horizontal plane
                forward.Normalize();

                return cameraTransform.position + (forward * spawnDistance);
            }

            // Default spawn position
            return new Vector3(0, 1.5f, 2f);
        }

        /// <summary>
        /// Delete the last spawned model
        /// </summary>
        public void DeleteLastCreation()
        {
            if (lastSpawnedModel != null)
            {
                modelImporter.DeleteModel(lastSpawnedModel);
                lastSpawnedModel = null;
                Debug.Log("[CreationManager] Last creation deleted");
            }
        }

        /// <summary>
        /// Save the last created model to collection
        /// </summary>
        public void SaveLastCreation()
        {
            if (lastSpawnedModel != null)
            {
                CreationMetadata metadata = lastSpawnedModel.GetComponent<CreationMetadata>();
                if (metadata != null)
                {
                    modelImporter.SaveModelToCollection(lastSpawnedModel, metadata.generationId);
                    Debug.Log($"[CreationManager] Creation saved: {metadata.generationId}");
                }
            }
        }

        /// <summary>
        /// Check if currently generating
        /// </summary>
        public bool IsGenerating()
        {
            return isGenerating;
        }

        /// <summary>
        /// Get the last spawned model
        /// </summary>
        public GameObject GetLastCreation()
        {
            return lastSpawnedModel;
        }

        /// <summary>
        /// Set user ID for generation requests
        /// </summary>
        public void SetUserId(string newUserId)
        {
            userId = newUserId;
        }

#if UNITY_EDITOR
        // Test creation from editor
        [ContextMenu("Test Create Cube")]
        private void TestCreateCube()
        {
            _ = CreateFromText("a simple cube", "low", "realistic");
        }

        [ContextMenu("Test Create Sphere")]
        private void TestCreateSphere()
        {
            _ = CreateFromText("a smooth sphere", "low", "realistic");
        }

        [ContextMenu("Delete Last")]
        private void TestDelete()
        {
            DeleteLastCreation();
        }
#endif
    }

    /// <summary>
    /// Metadata component attached to created models
    /// </summary>
    public class CreationMetadata : MonoBehaviour
    {
        public string generationId;
        public string prompt;
        public string createdAt;
        public int polycount;

        public void ShowInfo()
        {
            Debug.Log($"[Creation] ID: {generationId}");
            Debug.Log($"[Creation] Prompt: {prompt}");
            Debug.Log($"[Creation] Created: {createdAt}");
            Debug.Log($"[Creation] Polycount: {polycount}");
        }
    }
}
