using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

namespace Sanctuary.Core
{
    /// <summary>
    /// Client for accessing Archive.org content through Sanctuary backend
    /// Provides access to public domain books, audio, and educational content
    /// </summary>
    public class ArchiveClient : MonoBehaviour
    {
        [Header("API Configuration")]
        [SerializeField] private string apiBaseUrl = "http://localhost:5000/api/v1";
        [SerializeField] private string apiKey = "your_api_key_here";

        [Header("Cache Settings")]
        [SerializeField] private bool enableCache = true;
        [SerializeField] private float cacheExpirationMinutes = 60f;

        private static ArchiveClient instance;
        public static ArchiveClient Instance => instance;

        // Cache
        private Dictionary<string, CachedData> cache = new Dictionary<string, CachedData>();

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
        /// Search for books on Archive.org
        /// </summary>
        public async Task<ArchiveSearchResponse> SearchBooks(string query, int limit = 20, int page = 1)
        {
            if (string.IsNullOrEmpty(query))
            {
                throw new ArgumentException("Query cannot be empty");
            }

            // Check cache
            string cacheKey = $"search_books_{query}_{limit}_{page}";
            if (enableCache && TryGetFromCache(cacheKey, out ArchiveSearchResponse cachedResult))
            {
                Debug.Log($"[ArchiveClient] Returning cached results for: {query}");
                return cachedResult;
            }

            string url = $"{apiBaseUrl}/archive/search/books?query={UnityWebRequest.EscapeURL(query)}&limit={limit}&page={page}";

            Debug.Log($"[ArchiveClient] Searching books: {query}");

            try
            {
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
                        ArchiveSearchResponse response = JsonUtility.FromJson<ArchiveSearchResponse>(responseText);

                        // Cache result
                        if (enableCache)
                        {
                            AddToCache(cacheKey, response);
                        }

                        Debug.Log($"[ArchiveClient] Found {response.results.Length} books");
                        return response;
                    }
                    else
                    {
                        string errorMessage = $"API Error: {webRequest.error}";
                        Debug.LogError($"[ArchiveClient] {errorMessage}");
                        throw new Exception(errorMessage);
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[ArchiveClient] Exception: {e.Message}");
                throw;
            }
        }

        /// <summary>
        /// Search for audio content on Archive.org
        /// </summary>
        public async Task<ArchiveSearchResponse> SearchAudio(string query, int limit = 20, int page = 1)
        {
            string url = $"{apiBaseUrl}/archive/search/audio?query={UnityWebRequest.EscapeURL(query)}&limit={limit}&page={page}";

            Debug.Log($"[ArchiveClient] Searching audio: {query}");

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
                    return JsonUtility.FromJson<ArchiveSearchResponse>(responseText);
                }
                else
                {
                    throw new Exception($"Audio search failed: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Get detailed metadata for a specific item
        /// </summary>
        public async Task<ArchiveItemMetadata> GetItemMetadata(string identifier)
        {
            if (string.IsNullOrEmpty(identifier))
            {
                throw new ArgumentException("Identifier cannot be empty");
            }

            // Check cache
            string cacheKey = $"metadata_{identifier}";
            if (enableCache && TryGetFromCache(cacheKey, out ArchiveItemMetadata cachedMetadata))
            {
                Debug.Log($"[ArchiveClient] Returning cached metadata for: {identifier}");
                return cachedMetadata;
            }

            string url = $"{apiBaseUrl}/archive/item/{identifier}";

            Debug.Log($"[ArchiveClient] Fetching metadata: {identifier}");

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
                    ArchiveItemMetadata metadata = JsonUtility.FromJson<ArchiveItemMetadata>(responseText);

                    // Cache result
                    if (enableCache)
                    {
                        AddToCache(cacheKey, metadata);
                    }

                    Debug.Log($"[ArchiveClient] Retrieved metadata for: {identifier}");
                    return metadata;
                }
                else
                {
                    throw new Exception($"Metadata fetch failed: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Get Walden collection (Thoreau)
        /// </summary>
        public async Task<ArchiveSearchResponse> GetWaldenCollection()
        {
            string url = $"{apiBaseUrl}/archive/collections/walden";

            Debug.Log("[ArchiveClient] Fetching Walden collection");

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
                    return JsonUtility.FromJson<ArchiveSearchResponse>(responseText);
                }
                else
                {
                    throw new Exception($"Walden collection fetch failed: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Get Spinoza collection (Ethics)
        /// </summary>
        public async Task<ArchiveSearchResponse> GetSpinozaCollection()
        {
            string url = $"{apiBaseUrl}/archive/collections/spinoza";

            Debug.Log("[ArchiveClient] Fetching Spinoza collection");

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
                    return JsonUtility.FromJson<ArchiveSearchResponse>(responseText);
                }
                else
                {
                    throw new Exception($"Spinoza collection fetch failed: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Get Muir collection (Nature & Glaciers)
        /// </summary>
        public async Task<ArchiveSearchResponse> GetMuirCollection()
        {
            string url = $"{apiBaseUrl}/archive/collections/muir";

            Debug.Log("[ArchiveClient] Fetching Muir collection");

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
                    return JsonUtility.FromJson<ArchiveSearchResponse>(responseText);
                }
                else
                {
                    throw new Exception($"Muir collection fetch failed: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Get text content preview for an item
        /// </summary>
        public async Task<string> GetTextPreview(string identifier, int maxChars = 5000)
        {
            string url = $"{apiBaseUrl}/archive/text/{identifier}?max_chars={maxChars}";

            Debug.Log($"[ArchiveClient] Fetching text preview: {identifier}");

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
                    return webRequest.downloadHandler.text;
                }
                else
                {
                    throw new Exception($"Text preview fetch failed: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Clear the cache
        /// </summary>
        public void ClearCache()
        {
            cache.Clear();
            Debug.Log("[ArchiveClient] Cache cleared");
        }

        // ========== Cache Management ==========

        private bool TryGetFromCache<T>(string key, out T value)
        {
            if (cache.ContainsKey(key))
            {
                CachedData cachedData = cache[key];

                // Check if expired
                if ((DateTime.Now - cachedData.timestamp).TotalMinutes < cacheExpirationMinutes)
                {
                    value = (T)cachedData.data;
                    return true;
                }
                else
                {
                    // Remove expired entry
                    cache.Remove(key);
                }
            }

            value = default(T);
            return false;
        }

        private void AddToCache<T>(string key, T data)
        {
            cache[key] = new CachedData
            {
                data = data,
                timestamp = DateTime.Now
            };
        }

        private class CachedData
        {
            public object data;
            public DateTime timestamp;
        }

#if UNITY_EDITOR
        [ContextMenu("Test Search Walden")]
        private void TestSearchWalden()
        {
            _ = SearchBooks("Walden Thoreau", 5);
        }

        [ContextMenu("Test Get Walden Collection")]
        private void TestWaldenCollection()
        {
            _ = GetWaldenCollection();
        }

        [ContextMenu("Clear Cache")]
        private void EditorClearCache()
        {
            ClearCache();
        }
#endif
    }

    #region Data Models

    [Serializable]
    public class ArchiveSearchResponse
    {
        public string status;
        public ArchiveItem[] results;
        public int total_count;
        public int page;
        public int pages_total;
        public string query;
    }

    [Serializable]
    public class ArchiveItem
    {
        public string identifier;
        public string title;
        public string creator;
        public string description;
        public string date;
        public int downloads;
        public long size;
    }

    [Serializable]
    public class ArchiveItemMetadata
    {
        public string identifier;
        public string title;
        public string creator;
        public string description;
        public string date;
        public string language;
        public string[] subject;
        public string mediatype;
        public string[] collection;
        public ArchiveFile[] files;
    }

    [Serializable]
    public class ArchiveFile
    {
        public string name;
        public string format;
        public long size;
        public string url;
    }

    #endregion
}
