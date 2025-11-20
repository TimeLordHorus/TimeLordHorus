using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.InputSystem;

namespace Sanctuary.Core
{
    /// <summary>
    /// Sets up complete XR Rig with controllers, flight locomotion, and teleportation
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    public class XRRigSetup : MonoBehaviour
    {
        [Header("Prefab References")]
        [Tooltip("Left controller prefab (set automatically if using XR Interaction Toolkit)")]
        public GameObject leftControllerPrefab;

        [Tooltip("Right controller prefab")]
        public GameObject rightControllerPrefab;

        [Header("Setup Options")]
        [Tooltip("Automatically create camera offset")]
        public bool createCameraOffset = true;

        [Tooltip("Setup teleportation system")]
        public bool setupTeleportation = true;

        [Tooltip("Setup flight locomotion")]
        public bool setupFlightLocomotion = true;

        [Tooltip("Setup hand tracking")]
        public bool setupHandTracking = false;

        [Header("Height Settings")]
        [Tooltip("Camera height offset from origin")]
        public float cameraHeight = 1.6f;

        // Internal references
        private GameObject cameraOffsetObject;
        private Camera xrCamera;
        private FlightLocomotion flightSystem;

        private void Awake()
        {
            SetupXRRig();
        }

        /// <summary>
        /// Setup complete XR Rig
        /// </summary>
        private void SetupXRRig()
        {
            Debug.Log("[XRRigSetup] Setting up XR Rig...");

            // Setup camera offset
            if (createCameraOffset)
            {
                SetupCameraOffset();
            }

            // Setup controllers
            SetupControllers();

            // Setup locomotion systems
            if (setupFlightLocomotion)
            {
                SetupFlight();
            }

            if (setupTeleportation)
            {
                SetupTeleportationSystem();
            }

            // Setup interaction manager
            SetupInteractionManager();

            Debug.Log("[XRRigSetup] XR Rig setup complete!");
        }

        /// <summary>
        /// Create camera offset object
        /// </summary>
        private void SetupCameraOffset()
        {
            // Find or create camera offset
            Transform existingOffset = transform.Find("Camera Offset");
            if (existingOffset != null)
            {
                cameraOffsetObject = existingOffset.gameObject;
            }
            else
            {
                cameraOffsetObject = new GameObject("Camera Offset");
                cameraOffsetObject.transform.SetParent(transform);
                cameraOffsetObject.transform.localPosition = new Vector3(0, cameraHeight, 0);
                cameraOffsetObject.transform.localRotation = Quaternion.identity;
            }

            // Find or create main camera
            xrCamera = Camera.main;
            if (xrCamera == null)
            {
                GameObject cameraObj = new GameObject("Main Camera");
                cameraObj.transform.SetParent(cameraOffsetObject.transform);
                cameraObj.transform.localPosition = Vector3.zero;
                cameraObj.transform.localRotation = Quaternion.identity;
                cameraObj.tag = "MainCamera";

                xrCamera = cameraObj.AddComponent<Camera>();
                xrCamera.nearClipPlane = 0.01f;
                xrCamera.farClipPlane = 1000f;

                cameraObj.AddComponent<AudioListener>();
            }
            else if (xrCamera.transform.parent != cameraOffsetObject.transform)
            {
                xrCamera.transform.SetParent(cameraOffsetObject.transform);
                xrCamera.transform.localPosition = Vector3.zero;
                xrCamera.transform.localRotation = Quaternion.identity;
            }

            Debug.Log("[XRRigSetup] Camera offset created");
        }

        /// <summary>
        /// Setup XR controllers
        /// </summary>
        private void SetupControllers()
        {
            if (cameraOffsetObject == null)
            {
                Debug.LogWarning("[XRRigSetup] Camera offset not found, creating it first");
                SetupCameraOffset();
            }

            // Setup left controller
            if (leftControllerPrefab != null)
            {
                Transform existingLeft = cameraOffsetObject.transform.Find("LeftHand Controller");
                if (existingLeft == null)
                {
                    GameObject leftController = Instantiate(leftControllerPrefab, cameraOffsetObject.transform);
                    leftController.name = "LeftHand Controller";
                }
            }

            // Setup right controller
            if (rightControllerPrefab != null)
            {
                Transform existingRight = cameraOffsetObject.transform.Find("RightHand Controller");
                if (existingRight == null)
                {
                    GameObject rightController = Instantiate(rightControllerPrefab, cameraOffsetObject.transform);
                    rightController.name = "RightHand Controller";
                }
            }

            Debug.Log("[XRRigSetup] Controllers setup complete");
        }

        /// <summary>
        /// Setup flight locomotion system
        /// </summary>
        private void SetupFlight()
        {
            flightSystem = GetComponent<FlightLocomotion>();
            if (flightSystem == null)
            {
                flightSystem = gameObject.AddComponent<FlightLocomotion>();
                Debug.Log("[XRRigSetup] Flight locomotion added");
            }
        }

        /// <summary>
        /// Setup teleportation system
        /// </summary>
        private void SetupTeleportationSystem()
        {
            // Add teleportation provider
            TeleportationProvider teleportProvider = GetComponent<TeleportationProvider>();
            if (teleportProvider == null)
            {
                teleportProvider = gameObject.AddComponent<TeleportationProvider>();
            }

            Debug.Log("[XRRigSetup] Teleportation system setup complete");
        }

        /// <summary>
        /// Setup XR Interaction Manager
        /// </summary>
        private void SetupInteractionManager()
        {
            XRInteractionManager manager = FindObjectOfType<XRInteractionManager>();
            if (manager == null)
            {
                GameObject managerObj = new GameObject("XR Interaction Manager");
                manager = managerObj.AddComponent<XRInteractionManager>();
                Debug.Log("[XRRigSetup] XR Interaction Manager created");
            }
        }

        /// <summary>
        /// Get the flight locomotion system
        /// </summary>
        public FlightLocomotion GetFlightSystem()
        {
            return flightSystem;
        }

        /// <summary>
        /// Get the main XR camera
        /// </summary>
        public Camera GetXRCamera()
        {
            return xrCamera;
        }

        /// <summary>
        /// Get camera offset transform
        /// </summary>
        public Transform GetCameraOffset()
        {
            return cameraOffsetObject != null ? cameraOffsetObject.transform : null;
        }
    }
}
