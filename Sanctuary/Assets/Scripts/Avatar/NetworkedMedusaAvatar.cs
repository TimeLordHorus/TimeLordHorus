using Unity.Netcode;
using UnityEngine;

namespace Sanctuary.Avatar
{
    /// <summary>
    /// Networked version of MedusaAvatar for multiplayer synchronization
    /// Syncs glow intensity, voice activity, and movement state
    /// </summary>
    [RequireComponent(typeof(NetworkObject))]
    [RequireComponent(typeof(MedusaAvatar))]
    public class NetworkedMedusaAvatar : NetworkBehaviour
    {
        [Header("References")]
        private MedusaAvatar medusaAvatar;
        private MedusaCustomization customization;

        [Header("Sync Settings")]
        [SerializeField] private float syncInterval = 0.1f; // 10Hz sync rate
        private float lastSyncTime = 0f;

        // Network variables
        private NetworkVariable<float> networkGlowIntensity = new NetworkVariable<float>(
            0.2f,
            NetworkVariableReadPermission.Everyone,
            NetworkVariableWritePermission.Owner
        );

        private NetworkVariable<bool> networkIsSpeaking = new NetworkVariable<bool>(
            false,
            NetworkVariableReadPermission.Everyone,
            NetworkVariableWritePermission.Owner
        );

        private void Awake()
        {
            medusaAvatar = GetComponent<MedusaAvatar>();
            customization = GetComponent<MedusaCustomization>();
        }

        public override void OnNetworkSpawn()
        {
            base.OnNetworkSpawn();

            // Subscribe to network variable changes
            networkGlowIntensity.OnValueChanged += OnGlowIntensityChanged;
            networkIsSpeaking.OnValueChanged += OnSpeakingStateChanged;

            // Apply initial values
            if (!IsOwner)
            {
                medusaAvatar.SetGlowIntensity(networkGlowIntensity.Value);
            }

            Debug.Log($"[NetworkedMedusa] Spawned - Owner: {IsOwner}, ClientId: {OwnerClientId}");
        }

        public override void OnNetworkDespawn()
        {
            // Unsubscribe
            networkGlowIntensity.OnValueChanged -= OnGlowIntensityChanged;
            networkIsSpeaking.OnValueChanged -= OnSpeakingStateChanged;

            base.OnNetworkDespawn();
        }

        private void Update()
        {
            if (!IsSpawned)
                return;

            if (IsOwner)
            {
                // Send updates to server at regular intervals
                if (Time.time - lastSyncTime >= syncInterval)
                {
                    SyncState();
                    lastSyncTime = Time.time;
                }
            }
        }

        /// <summary>
        /// Sync local state to network
        /// </summary>
        private void SyncState()
        {
            if (!IsOwner)
                return;

            // Update glow intensity
            float currentGlow = medusaAvatar.GetGlowIntensity();
            if (Mathf.Abs(currentGlow - networkGlowIntensity.Value) > 0.01f)
            {
                networkGlowIntensity.Value = currentGlow;
            }

            // Update speaking state (you'd check microphone input here)
            // This is a placeholder - actual implementation would check audio input
            bool speaking = currentGlow > 0.5f;
            if (speaking != networkIsSpeaking.Value)
            {
                networkIsSpeaking.Value = speaking;
            }
        }

        /// <summary>
        /// Handle glow intensity changes from network
        /// </summary>
        private void OnGlowIntensityChanged(float previousValue, float newValue)
        {
            if (!IsOwner)
            {
                medusaAvatar.SetGlowIntensity(newValue);
            }
        }

        /// <summary>
        /// Handle speaking state changes from network
        /// </summary>
        private void OnSpeakingStateChanged(bool previousValue, bool newValue)
        {
            if (!IsOwner)
            {
                // Could trigger visual/audio indicators for remote players
                Debug.Log($"[NetworkedMedusa] Player {OwnerClientId} is {(newValue ? "speaking" : "silent")}");
            }
        }

        /// <summary>
        /// Set voice activity (call this from voice detection system)
        /// </summary>
        public void SetVoiceActive(bool active, float intensity)
        {
            if (!IsOwner)
                return;

            networkIsSpeaking.Value = active;

            if (active)
            {
                medusaAvatar.SetGlowIntensity(intensity);
            }
        }

        /// <summary>
        /// Get current speaking state
        /// </summary>
        public bool IsSpeaking()
        {
            return networkIsSpeaking.Value;
        }

        /// <summary>
        /// Server RPC to broadcast emote/gesture
        /// </summary>
        [ServerRpc]
        public void PlayEmoteServerRpc(EmoteType emote)
        {
            // Broadcast to all clients
            PlayEmoteClientRpc(emote);
        }

        /// <summary>
        /// Client RPC to play emote on all clients
        /// </summary>
        [ClientRpc]
        private void PlayEmoteClientRpc(EmoteType emote)
        {
            PlayEmoteLocal(emote);
        }

        /// <summary>
        /// Play emote locally
        /// </summary>
        private void PlayEmoteLocal(EmoteType emote)
        {
            switch (emote)
            {
                case EmoteType.Wave:
                    Debug.Log($"[NetworkedMedusa] Playing Wave emote for {OwnerClientId}");
                    // Animate tentacles waving
                    break;

                case EmoteType.Glow:
                    Debug.Log($"[NetworkedMedusa] Playing Glow emote for {OwnerClientId}");
                    // Temporary glow boost
                    medusaAvatar.SetGlowIntensity(2.0f);
                    break;

                case EmoteType.Pulse:
                    Debug.Log($"[NetworkedMedusa] Playing Pulse emote for {OwnerClientId}");
                    // Pulsing effect
                    break;

                case EmoteType.Dance:
                    Debug.Log($"[NetworkedMedusa] Playing Dance emote for {OwnerClientId}");
                    // Rotating animation
                    break;
            }
        }

        /// <summary>
        /// Emote types for jellyfish avatar
        /// </summary>
        public enum EmoteType
        {
            Wave,
            Glow,
            Pulse,
            Dance
        }
    }
}
