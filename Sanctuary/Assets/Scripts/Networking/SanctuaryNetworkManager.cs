using Unity.Netcode;
using UnityEngine;

namespace Sanctuary.Networking
{
    /// <summary>
    /// Sanctuary Network Manager
    /// Handles multiplayer networking using Unity Netcode for GameObjects
    /// Alternative to Photon Fusion for the beta phase
    /// </summary>
    public class SanctuaryNetworkManager : MonoBehaviour
    {
        [Header("Network Settings")]
        [Tooltip("Maximum number of players per server")]
        [SerializeField] private int maxPlayers = 32;

        [Tooltip("Server tick rate")]
        [SerializeField] private int tickRate = 60;

        [Tooltip("Enable voice chat")]
        [SerializeField] private bool enableVoiceChat = false;

        [Header("Connection Settings")]
        [Tooltip("Connection timeout in seconds")]
        [SerializeField] private float connectionTimeout = 10f;

        [Tooltip("Auto-connect on start")]
        [SerializeField] private bool autoConnect = false;

        [Tooltip("Connection type")]
        [SerializeField] private ConnectionType connectionType = ConnectionType.Host;

        [Header("Spawn Settings")]
        [Tooltip("Player prefab to spawn")]
        [SerializeField] private GameObject playerPrefab;

        [Tooltip("Spawn points")]
        [SerializeField] private Transform[] spawnPoints;

        private NetworkManager networkManager;
        private int nextSpawnPointIndex = 0;

        public enum ConnectionType
        {
            Host,
            Client,
            Server
        }

        private void Awake()
        {
            // Get or create NetworkManager
            networkManager = GetComponent<NetworkManager>();
            if (networkManager == null)
            {
                networkManager = gameObject.AddComponent<NetworkManager>();
            }

            // Configure NetworkManager
            ConfigureNetworkManager();

            // Register callbacks
            RegisterCallbacks();
        }

        private void Start()
        {
            if (autoConnect)
            {
                Connect();
            }
        }

        /// <summary>
        /// Configure the Unity NetworkManager
        /// </summary>
        private void ConfigureNetworkManager()
        {
            // Set network prefabs
            if (playerPrefab != null && networkManager.NetworkConfig != null)
            {
                // Note: In production, register prefabs through NetworkConfig asset
                Debug.Log($"[SanctuaryNetworkManager] Player prefab: {playerPrefab.name}");
            }

            Debug.Log("[SanctuaryNetworkManager] Network manager configured");
        }

        /// <summary>
        /// Register network callbacks
        /// </summary>
        private void RegisterCallbacks()
        {
            if (networkManager != null)
            {
                networkManager.OnClientConnectedCallback += OnClientConnected;
                networkManager.OnClientDisconnectCallback += OnClientDisconnected;
                networkManager.OnServerStarted += OnServerStarted;
            }
        }

        /// <summary>
        /// Connect to network based on connection type
        /// </summary>
        public void Connect()
        {
            if (networkManager == null)
            {
                Debug.LogError("[SanctuaryNetworkManager] NetworkManager not found!");
                return;
            }

            switch (connectionType)
            {
                case ConnectionType.Host:
                    StartHost();
                    break;
                case ConnectionType.Client:
                    StartClient();
                    break;
                case ConnectionType.Server:
                    StartServer();
                    break;
            }
        }

        /// <summary>
        /// Start as host (server + client)
        /// </summary>
        public void StartHost()
        {
            Debug.Log("[SanctuaryNetworkManager] Starting as Host...");
            networkManager.StartHost();
        }

        /// <summary>
        /// Start as client
        /// </summary>
        public void StartClient()
        {
            Debug.Log("[SanctuaryNetworkManager] Starting as Client...");
            networkManager.StartClient();
        }

        /// <summary>
        /// Start as dedicated server
        /// </summary>
        public void StartServer()
        {
            Debug.Log("[SanctuaryNetworkManager] Starting as Server...");
            networkManager.StartServer();
        }

        /// <summary>
        /// Disconnect from network
        /// </summary>
        public void Disconnect()
        {
            Debug.Log("[SanctuaryNetworkManager] Disconnecting...");
            networkManager.Shutdown();
        }

        /// <summary>
        /// Called when a client connects
        /// </summary>
        private void OnClientConnected(ulong clientId)
        {
            Debug.Log($"[SanctuaryNetworkManager] Client {clientId} connected");

            // Spawn player for this client
            if (networkManager.IsServer)
            {
                SpawnPlayer(clientId);
            }
        }

        /// <summary>
        /// Called when a client disconnects
        /// </summary>
        private void OnClientDisconnected(ulong clientId)
        {
            Debug.Log($"[SanctuaryNetworkManager] Client {clientId} disconnected");
        }

        /// <summary>
        /// Called when server starts
        /// </summary>
        private void OnServerStarted()
        {
            Debug.Log("[SanctuaryNetworkManager] Server started successfully");
        }

        /// <summary>
        /// Spawn player at spawn point
        /// </summary>
        private void SpawnPlayer(ulong clientId)
        {
            if (playerPrefab == null)
            {
                Debug.LogWarning("[SanctuaryNetworkManager] No player prefab assigned!");
                return;
            }

            // Get spawn position
            Vector3 spawnPosition = GetSpawnPosition();
            Quaternion spawnRotation = GetSpawnRotation();

            // Spawn player
            GameObject playerObj = Instantiate(playerPrefab, spawnPosition, spawnRotation);
            NetworkObject networkObject = playerObj.GetComponent<NetworkObject>();

            if (networkObject != null)
            {
                networkObject.SpawnAsPlayerObject(clientId);
                Debug.Log($"[SanctuaryNetworkManager] Spawned player for client {clientId}");
            }
            else
            {
                Debug.LogError("[SanctuaryNetworkManager] Player prefab missing NetworkObject component!");
                Destroy(playerObj);
            }
        }

        /// <summary>
        /// Get next spawn position
        /// </summary>
        private Vector3 GetSpawnPosition()
        {
            if (spawnPoints == null || spawnPoints.Length == 0)
            {
                // Default spawn at origin with slight randomization
                return new Vector3(
                    Random.Range(-2f, 2f),
                    2f,
                    Random.Range(-2f, 2f)
                );
            }

            Vector3 position = spawnPoints[nextSpawnPointIndex].position;
            nextSpawnPointIndex = (nextSpawnPointIndex + 1) % spawnPoints.length;
            return position;
        }

        /// <summary>
        /// Get spawn rotation
        /// </summary>
        private Quaternion GetSpawnRotation()
        {
            if (spawnPoints == null || spawnPoints.Length == 0)
            {
                return Quaternion.identity;
            }

            return spawnPoints[nextSpawnPointIndex].rotation;
        }

        /// <summary>
        /// Get current connection status
        /// </summary>
        public bool IsConnected()
        {
            return networkManager != null && networkManager.IsListening;
        }

        /// <summary>
        /// Get number of connected clients
        /// </summary>
        public int GetConnectedClients()
        {
            if (networkManager == null || !networkManager.IsServer)
                return 0;

            return (int)networkManager.ConnectedClients.Count;
        }

        private void OnDestroy()
        {
            // Unregister callbacks
            if (networkManager != null)
            {
                networkManager.OnClientConnectedCallback -= OnClientConnected;
                networkManager.OnClientDisconnectCallback -= OnClientDisconnected;
                networkManager.OnServerStarted -= OnServerStarted;
            }
        }

#if UNITY_EDITOR
        private void OnGUI()
        {
            // Debug UI for testing
            if (!Application.isPlaying)
                return;

            GUILayout.BeginArea(new Rect(10, 10, 200, 200));

            if (!IsConnected())
            {
                if (GUILayout.Button("Start Host"))
                    StartHost();
                if (GUILayout.Button("Start Client"))
                    StartClient();
                if (GUILayout.Button("Start Server"))
                    StartServer();
            }
            else
            {
                GUILayout.Label($"Connected: {GetConnectedClients()} clients");
                if (GUILayout.Button("Disconnect"))
                    Disconnect();
            }

            GUILayout.EndArea();
        }
#endif
    }
}
