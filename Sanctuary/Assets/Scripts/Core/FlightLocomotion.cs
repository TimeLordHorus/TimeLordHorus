using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.InputSystem;

namespace Sanctuary.Core
{
    /// <summary>
    /// Flight locomotion system for jellyfish-style movement in VR
    /// Provides smooth, physics-based flight with head-directed movement
    /// </summary>
    public class FlightLocomotion : MonoBehaviour
    {
        [Header("Flight Settings")]
        [Tooltip("Base flight speed in meters per second")]
        [SerializeField] private float flightSpeed = 3.0f;

        [Tooltip("Maximum flight speed")]
        [SerializeField] private float maxSpeed = 8.0f;

        [Tooltip("Acceleration rate")]
        [SerializeField] private float acceleration = 2.0f;

        [Tooltip("Deceleration rate when not moving")]
        [SerializeField] private float deceleration = 5.0f;

        [Tooltip("Vertical flight speed multiplier")]
        [SerializeField] private float verticalSpeedMultiplier = 0.75f;

        [Header("Input Settings")]
        [Tooltip("Use head direction for movement (jellyfish style)")]
        [SerializeField] private bool headDirectedMovement = true;

        [Tooltip("Enable boost on trigger hold")]
        [SerializeField] private bool enableBoost = true;

        [Tooltip("Boost multiplier")]
        [SerializeField] private float boostMultiplier = 2.0f;

        [Header("Physics Settings")]
        [Tooltip("Enable inertia dampening")]
        [SerializeField] private bool useInertia = true;

        [Tooltip("Inertia strength (0-1)")]
        [SerializeField] private float inertiaStrength = 0.85f;

        [Tooltip("Enable gravity when idle")]
        [SerializeField] private bool applyIdleGravity = false;

        [Tooltip("Idle gravity strength")]
        [SerializeField] private float idleGravity = -2.0f;

        [Header("References")]
        [SerializeField] private Transform xrOrigin;
        [SerializeField] private Transform cameraTransform;
        [SerializeField] private CharacterController characterController;

        [Header("Input Actions")]
        [SerializeField] private InputActionProperty moveAction;
        [SerializeField] private InputActionProperty boostAction;
        [SerializeField] private InputActionProperty upAction;
        [SerializeField] private InputActionProperty downAction;

        // Private state
        private Vector3 currentVelocity = Vector3.zero;
        private bool isBoosting = false;
        private float currentSpeed = 0f;

        private void Awake()
        {
            // Auto-find references if not set
            if (xrOrigin == null)
                xrOrigin = transform;

            if (cameraTransform == null)
                cameraTransform = Camera.main.transform;

            if (characterController == null)
            {
                characterController = GetComponent<CharacterController>();
                if (characterController == null)
                {
                    characterController = gameObject.AddComponent<CharacterController>();
                    characterController.height = 1.8f;
                    characterController.radius = 0.4f;
                    characterController.center = new Vector3(0, 0.9f, 0);
                }
            }
        }

        private void OnEnable()
        {
            moveAction.action?.Enable();
            boostAction.action?.Enable();
            upAction.action?.Enable();
            downAction.action?.Enable();
        }

        private void OnDisable()
        {
            moveAction.action?.Disable();
            boostAction.action?.Disable();
            upAction.action?.Disable();
            downAction.action?.Disable();
        }

        private void Update()
        {
            HandleFlightMovement();
        }

        /// <summary>
        /// Handle flight movement logic
        /// </summary>
        private void HandleFlightMovement()
        {
            // Get input
            Vector2 moveInput = moveAction.action?.ReadValue<Vector2>() ?? Vector2.zero;
            float upInput = upAction.action?.ReadValue<float>() ?? 0f;
            float downInput = downAction.action?.ReadValue<float>() ?? 0f;
            isBoosting = enableBoost && (boostAction.action?.ReadValue<float>() > 0.5f);

            // Calculate movement direction
            Vector3 moveDirection = Vector3.zero;

            if (moveInput.sqrMagnitude > 0.01f)
            {
                // Get forward/right relative to camera or origin
                Transform referenceTransform = headDirectedMovement ? cameraTransform : xrOrigin;

                Vector3 forward = referenceTransform.forward;
                Vector3 right = referenceTransform.right;

                // Project onto horizontal plane for standard movement
                if (!headDirectedMovement)
                {
                    forward.y = 0;
                    right.y = 0;
                    forward.Normalize();
                    right.Normalize();
                }

                moveDirection = (forward * moveInput.y + right * moveInput.x).normalized;
            }

            // Add vertical movement
            float verticalInput = upInput - downInput;
            if (Mathf.Abs(verticalInput) > 0.01f)
            {
                moveDirection += Vector3.up * verticalInput * verticalSpeedMultiplier;
                moveDirection.Normalize();
            }

            // Calculate target speed
            float targetSpeed = 0f;
            if (moveDirection.sqrMagnitude > 0.01f)
            {
                targetSpeed = flightSpeed;
                if (isBoosting)
                    targetSpeed *= boostMultiplier;
            }

            // Smooth acceleration/deceleration
            if (targetSpeed > currentSpeed)
            {
                currentSpeed = Mathf.Lerp(currentSpeed, targetSpeed, acceleration * Time.deltaTime);
            }
            else
            {
                currentSpeed = Mathf.Lerp(currentSpeed, targetSpeed, deceleration * Time.deltaTime);
            }

            // Clamp speed
            currentSpeed = Mathf.Min(currentSpeed, maxSpeed);

            // Calculate velocity
            Vector3 targetVelocity = moveDirection * currentSpeed;

            // Apply inertia
            if (useInertia && currentVelocity.sqrMagnitude > 0.01f)
            {
                currentVelocity = Vector3.Lerp(targetVelocity, currentVelocity, inertiaStrength * Time.deltaTime);
            }
            else
            {
                currentVelocity = targetVelocity;
            }

            // Apply idle gravity
            if (applyIdleGravity && moveDirection.sqrMagnitude < 0.01f)
            {
                currentVelocity += Vector3.up * idleGravity * Time.deltaTime;
            }

            // Move character controller
            if (characterController != null && characterController.enabled)
            {
                characterController.Move(currentVelocity * Time.deltaTime);
            }
            else
            {
                // Fallback to transform movement
                xrOrigin.position += currentVelocity * Time.deltaTime;
            }
        }

        /// <summary>
        /// Get current flight velocity (useful for animation/effects)
        /// </summary>
        public Vector3 GetVelocity()
        {
            return currentVelocity;
        }

        /// <summary>
        /// Get current speed magnitude
        /// </summary>
        public float GetSpeed()
        {
            return currentSpeed;
        }

        /// <summary>
        /// Check if currently boosting
        /// </summary>
        public bool IsBoosting()
        {
            return isBoosting;
        }

        /// <summary>
        /// Set flight speed programmatically
        /// </summary>
        public void SetFlightSpeed(float speed)
        {
            flightSpeed = Mathf.Max(0, speed);
        }

        /// <summary>
        /// Stop all movement instantly
        /// </summary>
        public void StopMovement()
        {
            currentVelocity = Vector3.zero;
            currentSpeed = 0f;
        }

#if UNITY_EDITOR
        private void OnDrawGizmos()
        {
            if (Application.isPlaying && currentVelocity.sqrMagnitude > 0.01f)
            {
                Gizmos.color = isBoosting ? Color.cyan : Color.green;
                Gizmos.DrawRay(xrOrigin != null ? xrOrigin.position : transform.position, currentVelocity);
            }
        }
#endif
    }
}
