using Unity.Netcode;
using UnityEngine;
using Sanctuary.Core;

namespace Sanctuary.Networking
{
    /// <summary>
    /// Networked player component for multiplayer VR
    /// Syncs position, rotation, and avatar state across network
    /// </summary>
    [RequireComponent(typeof(NetworkObject))]
    public class NetworkedPlayer : NetworkBehaviour
    {
        [Header("Synchronization Settings")]
        [Tooltip("Position interpolation speed")]
        [SerializeField] private float positionLerpSpeed = 15f;

        [Tooltip("Rotation interpolation speed")]
        [SerializeField] private float rotationLerpSpeed = 10f;

        [Tooltip("Send rate (updates per second)")]
        [SerializeField] private float sendRate = 20f;

        [Header("Avatar References")]
        [Tooltip("Head transform to sync")]
        [SerializeField] private Transform headTransform;

        [Tooltip("Left hand transform")]
        [SerializeField] private Transform leftHandTransform;

        [Tooltip("Right hand transform")]
        [SerializeField] private Transform rightHandTransform;

        [Header("Local Player References")]
        [Tooltip("Local XR rig (disabled for remote players)")]
        [SerializeField] private GameObject localXRRig;

        [Tooltip("Remote avatar representation")]
        [SerializeField] private GameObject remoteAvatar;

        // Network variables
        private NetworkVariable<Vector3> networkPosition = new NetworkVariable<Vector3>();
        private NetworkVariable<Quaternion> networkRotation = new NetworkVariable<Quaternion>();
        private NetworkVariable<Vector3> networkHeadPosition = new NetworkVariable<Vector3>();
        private NetworkVariable<Quaternion> networkHeadRotation = new NetworkVariable<Quaternion>();

        // State
        private float lastSendTime = 0f;
        private FlightLocomotion flightSystem;

        public override void OnNetworkSpawn()
        {
            base.OnNetworkSpawn();

            if (IsOwner)
            {
                // This is the local player
                SetupLocalPlayer();
            }
            else
            {
                // This is a remote player
                SetupRemotePlayer();
            }

            Debug.Log($"[NetworkedPlayer] Spawned - Owner: {IsOwner}, ClientId: {OwnerClientId}");
        }

        /// <summary>
        /// Setup local player (this client's player)
        /// </summary>
        private void SetupLocalPlayer()
        {
            // Enable local XR rig
            if (localXRRig != null)
            {
                localXRRig.SetActive(true);
            }

            // Disable remote avatar
            if (remoteAvatar != null)
            {
                remoteAvatar.SetActive(false);
            }

            // Get flight system
            flightSystem = GetComponent<FlightLocomotion>();

            // Find camera if not assigned
            if (headTransform == null)
            {
                Camera mainCam = Camera.main;
                if (mainCam != null)
                {
                    headTransform = mainCam.transform;
                }
            }

            Debug.Log("[NetworkedPlayer] Local player setup complete");
        }

        /// <summary>
        /// Setup remote player (other clients' players)
        /// </summary>
        private void SetupRemotePlayer()
        {
            // Disable local XR rig
            if (localXRRig != null)
            {
                localXRRig.SetActive(false);
            }

            // Enable remote avatar
            if (remoteAvatar != null)
            {
                remoteAvatar.SetActive(true);
            }

            // Disable local-only components
            FlightLocomotion flight = GetComponent<FlightLocomotion>();
            if (flight != null)
            {
                flight.enabled = false;
            }

            CharacterController charController = GetComponent<CharacterController>();
            if (charController != null)
            {
                charController.enabled = false;
            }

            Debug.Log("[NetworkedPlayer] Remote player setup complete");
        }

        private void Update()
        {
            if (IsOwner)
            {
                // Send updates to server
                SendUpdatesToServer();
            }
            else
            {
                // Interpolate remote player position
                InterpolateRemotePlayer();
            }
        }

        /// <summary>
        /// Send position and rotation updates to server
        /// </summary>
        private void SendUpdatesToServer()
        {
            if (Time.time - lastSendTime < 1f / sendRate)
                return;

            lastSendTime = Time.time;

            // Update network variables (server authoritative)
            UpdatePositionServerRpc(transform.position, transform.rotation);

            // Update head position if available
            if (headTransform != null)
            {
                UpdateHeadServerRpc(headTransform.localPosition, headTransform.localRotation);
            }
        }

        /// <summary>
        /// Interpolate remote player to network position
        /// </summary>
        private void InterpolateRemotePlayer()
        {
            // Interpolate body
            transform.position = Vector3.Lerp(
                transform.position,
                networkPosition.Value,
                positionLerpSpeed * Time.deltaTime
            );

            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                networkRotation.Value,
                rotationLerpSpeed * Time.deltaTime
            );

            // Interpolate head
            if (headTransform != null)
            {
                headTransform.localPosition = Vector3.Lerp(
                    headTransform.localPosition,
                    networkHeadPosition.Value,
                    positionLerpSpeed * Time.deltaTime
                );

                headTransform.localRotation = Quaternion.Slerp(
                    headTransform.localRotation,
                    networkHeadRotation.Value,
                    rotationLerpSpeed * Time.deltaTime
                );
            }
        }

        /// <summary>
        /// Update position on server
        /// </summary>
        [ServerRpc]
        private void UpdatePositionServerRpc(Vector3 position, Quaternion rotation)
        {
            networkPosition.Value = position;
            networkRotation.Value = rotation;
        }

        /// <summary>
        /// Update head transform on server
        /// </summary>
        [ServerRpc]
        private void UpdateHeadServerRpc(Vector3 localPosition, Quaternion localRotation)
        {
            networkHeadPosition.Value = localPosition;
            networkHeadRotation.Value = localRotation;
        }

        /// <summary>
        /// Check if this is the local player
        /// </summary>
        public bool IsLocalPlayer()
        {
            return IsOwner;
        }

        /// <summary>
        /// Get the flight system (local player only)
        /// </summary>
        public FlightLocomotion GetFlightSystem()
        {
            return flightSystem;
        }
    }
}
