using System;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

namespace Sanctuary.AI
{
    /// <summary>
    /// Client for communicating with the Flask AI backend to generate 3D models
    /// from text prompts.
    /// </summary>
    public class TextTo3DClient : MonoBehaviour
    {
        [Header("API Configuration")]
        [SerializeField] private string apiBaseUrl = "http://localhost:5000/api/v1";
        [SerializeField] private string apiKey = "your_api_key_here";

        [Header("Generation Settings")]
        [SerializeField] private string defaultQuality = "medium";
        [SerializeField] private string defaultStyle = "realistic";

        private static TextTo3DClient instance;
        public static TextTo3DClient Instance => instance;

        private void Awake()
        {
            if (instance == null)
            {
                instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }

        /// <summary>
        /// Generate a 3D model from a text prompt
        /// </summary>
        public async Task<ModelGenerationResponse> GenerateModel(
            string prompt,
            string userId,
            string quality = null,
            string style = null
        )
        {
            if (string.IsNullOrEmpty(prompt))
            {
                throw new ArgumentException("Prompt cannot be empty");
            }

            var request = new ModelGenerationRequest
            {
                prompt = prompt,
                user_id = userId,
                quality = quality ?? defaultQuality,
                style = style ?? defaultStyle
            };

            string url = $"{apiBaseUrl}/generate/model";
            string jsonPayload = JsonUtility.ToJson(request);

            Debug.Log($"[TextTo3D] Sending generation request: {prompt}");

            try
            {
                using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
                {
                    byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonPayload);
                    webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
                    webRequest.downloadHandler = new DownloadHandlerBuffer();

                    webRequest.SetRequestHeader("Content-Type", "application/json");
                    webRequest.SetRequestHeader("Authorization", $"Bearer {apiKey}");

                    var operation = webRequest.SendWebRequest();

                    while (!operation.isDone)
                    {
                        await Task.Yield();
                    }

                    if (webRequest.result == UnityWebRequest.Result.Success)
                    {
                        string responseText = webRequest.downloadHandler.text;
                        ModelGenerationResponse response = JsonUtility.FromJson<ModelGenerationResponse>(responseText);

                        Debug.Log($"[TextTo3D] Model generated successfully: {response.model_url}");
                        return response;
                    }
                    else
                    {
                        string errorMessage = $"API Error: {webRequest.error}\n{webRequest.downloadHandler.text}";
                        Debug.LogError($"[TextTo3D] {errorMessage}");
                        throw new Exception(errorMessage);
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[TextTo3D] Exception: {e.Message}");
                throw;
            }
        }

        /// <summary>
        /// Check the status of a model generation request
        /// </summary>
        public async Task<GenerationStatusResponse> CheckGenerationStatus(string generationId)
        {
            string url = $"{apiBaseUrl}/generate/status/{generationId}";

            using (UnityWebRequest webRequest = UnityWebRequest.Get(url))
            {
                webRequest.SetRequestHeader("Authorization", $"Bearer {apiKey}");

                var operation = webRequest.SendWebRequest();

                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                if (webRequest.result == UnityWebRequest.Result.Success)
                {
                    string responseText = webRequest.downloadHandler.text;
                    return JsonUtility.FromJson<GenerationStatusResponse>(responseText);
                }
                else
                {
                    throw new Exception($"Status check failed: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Get all creations for a user
        /// </summary>
        public async Task<UserCreationsResponse> GetUserCreations(
            string userId,
            int page = 1,
            int limit = 20
        )
        {
            string url = $"{apiBaseUrl}/users/{userId}/creations?page={page}&limit={limit}";

            using (UnityWebRequest webRequest = UnityWebRequest.Get(url))
            {
                webRequest.SetRequestHeader("Authorization", $"Bearer {apiKey}");

                var operation = webRequest.SendWebRequest();

                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                if (webRequest.result == UnityWebRequest.Result.Success)
                {
                    string responseText = webRequest.downloadHandler.text;
                    return JsonUtility.FromJson<UserCreationsResponse>(responseText);
                }
                else
                {
                    throw new Exception($"Failed to get user creations: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Moderate content before sending to generation
        /// </summary>
        public async Task<ModerationResponse> ModerateContent(string prompt, string userId)
        {
            var request = new ModerationRequest
            {
                content_type = "text",
                content = prompt,
                user_id = userId
            };

            string url = $"{apiBaseUrl}/moderate/content";
            string jsonPayload = JsonUtility.ToJson(request);

            using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonPayload);
                webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
                webRequest.downloadHandler = new DownloadHandlerBuffer();

                webRequest.SetRequestHeader("Content-Type", "application/json");
                webRequest.SetRequestHeader("Authorization", $"Bearer {apiKey}");

                var operation = webRequest.SendWebRequest();

                while (!operation.isDone)
                {
                    await Task.Yield();
                }

                if (webRequest.result == UnityWebRequest.Result.Success)
                {
                    string responseText = webRequest.downloadHandler.text;
                    return JsonUtility.FromJson<ModerationResponse>(responseText);
                }
                else
                {
                    throw new Exception($"Moderation failed: {webRequest.error}");
                }
            }
        }
    }

    #region Data Models

    [Serializable]
    public class ModelGenerationRequest
    {
        public string prompt;
        public string user_id;
        public string quality;
        public string style;
    }

    [Serializable]
    public class ModelGenerationResponse
    {
        public string status;
        public string model_url;
        public string thumbnail_url;
        public string generation_id;
        public int estimated_polycount;
        public string created_at;
    }

    [Serializable]
    public class GenerationStatusResponse
    {
        public string status; // "processing", "completed", "failed"
        public int progress;
        public string model_url;
        public string error_message;
        public int estimated_completion_seconds;
    }

    [Serializable]
    public class UserCreationsResponse
    {
        public string status;
        public Creation[] creations;
        public int total_count;
        public int page;
        public int pages_total;
    }

    [Serializable]
    public class Creation
    {
        public string generation_id;
        public string prompt;
        public string model_url;
        public string thumbnail_url;
        public string created_at;
        public int polycount;
    }

    [Serializable]
    public class ModerationRequest
    {
        public string content_type;
        public string content;
        public string user_id;
    }

    [Serializable]
    public class ModerationResponse
    {
        public string status;
        public bool is_safe;
        public string[] flags;
        public float confidence;
    }

    #endregion
}
