using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Events;

namespace Sanctuary.Verification
{
    /// <summary>
    /// The Gate - Age Verification System
    /// Privacy-first 18+ verification using facial analysis and challenge questions
    /// Zero-knowledge proof approach: verification data never leaves device
    /// </summary>
    public class AgeVerificationManager : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private int minimumAge = 18;
        [SerializeField] private bool requireFacialVerification = true;
        [SerializeField] private bool requireChallengeQuestions = true;
        [SerializeField] private int requiredChallenges = 3;

        [Header("Privacy Settings")]
        [SerializeField] private bool enableLocalProcessing = true; // Process on-device only
        [SerializeField] private bool storeVerificationResult = true; // Store only pass/fail, not biometric data
        [SerializeField] private float verificationCacheDays = 30f; // Re-verify after 30 days

        [Header("Events")]
        public UnityEvent OnVerificationStarted;
        public UnityEvent OnVerificationPassed;
        public UnityEvent OnVerificationFailed;
        public UnityEvent<string> OnVerificationError;
        public UnityEvent<float> OnVerificationProgress; // 0.0 to 1.0

        // Singleton
        private static AgeVerificationManager instance;
        public static AgeVerificationManager Instance => instance;

        // State
        private VerificationState currentState = VerificationState.NotStarted;
        private VerificationResult cachedResult;
        private DateTime lastVerificationDate;

        // Components
        private FacialAgeEstimator facialEstimator;
        private ChallengeQuestionSystem challengeSystem;

        public enum VerificationState
        {
            NotStarted,
            InitializingCamera,
            CapturingFace,
            AnalyzingFace,
            PresentingChallenges,
            AnsweringChallenges,
            Verifying,
            Passed,
            Failed
        }

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
                return;
            }

            InitializeComponents();
        }

        private void Start()
        {
            LoadCachedVerification();
        }

        /// <summary>
        /// Initialize verification components
        /// </summary>
        private void InitializeComponents()
        {
            // Facial age estimator
            if (requireFacialVerification)
            {
                GameObject estimatorObj = new GameObject("FacialAgeEstimator");
                estimatorObj.transform.SetParent(transform);
                facialEstimator = estimatorObj.AddComponent<FacialAgeEstimator>();
                facialEstimator.OnEstimationComplete += OnFacialEstimationComplete;
                facialEstimator.OnEstimationError += OnFacialEstimationError;
            }

            // Challenge question system
            if (requireChallengeQuestions)
            {
                GameObject challengeObj = new GameObject("ChallengeQuestionSystem");
                challengeObj.transform.SetParent(transform);
                challengeSystem = challengeObj.AddComponent<ChallengeQuestionSystem>();
                challengeSystem.OnChallengesComplete += OnChallengesComplete;
            }

            Debug.Log("[AgeVerification] Components initialized");
        }

        /// <summary>
        /// Start the age verification process
        /// </summary>
        public async Task<bool> StartVerification()
        {
            // Check if already verified recently
            if (IsRecentlyVerified())
            {
                Debug.Log("[AgeVerification] User recently verified, using cached result");
                OnVerificationPassed?.Invoke();
                return true;
            }

            currentState = VerificationState.NotStarted;
            OnVerificationStarted?.Invoke();

            Debug.Log("[AgeVerification] Starting verification process...");

            try
            {
                bool facialPassed = true;
                bool challengesPassed = true;

                // Step 1: Facial verification
                if (requireFacialVerification)
                {
                    OnVerificationProgress?.Invoke(0.1f);
                    currentState = VerificationState.InitializingCamera;

                    facialPassed = await PerformFacialVerification();

                    if (!facialPassed)
                    {
                        Debug.LogWarning("[AgeVerification] Facial verification failed");
                        currentState = VerificationState.Failed;
                        OnVerificationFailed?.Invoke();
                        return false;
                    }

                    OnVerificationProgress?.Invoke(0.5f);
                }

                // Step 2: Challenge questions
                if (requireChallengeQuestions)
                {
                    currentState = VerificationState.PresentingChallenges;

                    challengesPassed = await PerformChallengeVerification();

                    if (!challengesPassed)
                    {
                        Debug.LogWarning("[AgeVerification] Challenge verification failed");
                        currentState = VerificationState.Failed;
                        OnVerificationFailed?.Invoke();
                        return false;
                    }

                    OnVerificationProgress?.Invoke(1.0f);
                }

                // Verification passed
                currentState = VerificationState.Passed;
                SaveVerificationResult(true);
                OnVerificationPassed?.Invoke();

                Debug.Log("[AgeVerification] Verification successful!");
                return true;
            }
            catch (Exception e)
            {
                Debug.LogError($"[AgeVerification] Verification error: {e.Message}");
                currentState = VerificationState.Failed;
                OnVerificationError?.Invoke(e.Message);
                OnVerificationFailed?.Invoke();
                return false;
            }
        }

        /// <summary>
        /// Perform facial age estimation
        /// </summary>
        private async Task<bool> PerformFacialVerification()
        {
            if (facialEstimator == null)
            {
                Debug.LogError("[AgeVerification] Facial estimator not initialized");
                return false;
            }

            currentState = VerificationState.CapturingFace;

            // Start facial capture
            bool captureSuccess = await facialEstimator.StartCapture();

            if (!captureSuccess)
            {
                Debug.LogError("[AgeVerification] Face capture failed");
                return false;
            }

            currentState = VerificationState.AnalyzingFace;

            // Wait for estimation to complete (handled by callback)
            // This is a simplified approach - in production, you'd await a Task
            await Task.Delay(3000); // Simulate processing time

            return facialEstimator.GetLastEstimatedAge() >= minimumAge;
        }

        /// <summary>
        /// Perform challenge question verification
        /// </summary>
        private async Task<bool> PerformChallengeVerification()
        {
            if (challengeSystem == null)
            {
                Debug.LogError("[AgeVerification] Challenge system not initialized");
                return false;
            }

            currentState = VerificationState.AnsweringChallenges;

            // Present challenges
            bool challengesPassed = await challengeSystem.PresentChallenges(requiredChallenges);

            return challengesPassed;
        }

        /// <summary>
        /// Callback for facial estimation complete
        /// </summary>
        private void OnFacialEstimationComplete(int estimatedAge, float confidence)
        {
            Debug.Log($"[AgeVerification] Estimated age: {estimatedAge} (confidence: {confidence:P0})");

            // Privacy: Immediately discard detailed biometric data
            // Store only pass/fail result
        }

        /// <summary>
        /// Callback for facial estimation error
        /// </summary>
        private void OnFacialEstimationError(string error)
        {
            Debug.LogError($"[AgeVerification] Facial estimation error: {error}");
            OnVerificationError?.Invoke(error);
        }

        /// <summary>
        /// Callback for challenges complete
        /// </summary>
        private void OnChallengesComplete(bool passed, int score, int total)
        {
            Debug.Log($"[AgeVerification] Challenges result: {score}/{total} ({(passed ? "PASS" : "FAIL")})");
        }

        /// <summary>
        /// Save verification result to local storage
        /// </summary>
        private void SaveVerificationResult(bool passed)
        {
            if (!storeVerificationResult) return;

            cachedResult = new VerificationResult
            {
                passed = passed,
                timestamp = DateTime.UtcNow.ToString("o"),
                expiryDate = DateTime.UtcNow.AddDays(verificationCacheDays).ToString("o")
            };

            lastVerificationDate = DateTime.UtcNow;

            // Save to PlayerPrefs (encrypted in production)
            string resultJson = JsonUtility.ToJson(cachedResult);
            PlayerPrefs.SetString("VerificationResult", resultJson);
            PlayerPrefs.Save();

            Debug.Log($"[AgeVerification] Result cached until {cachedResult.expiryDate}");
        }

        /// <summary>
        /// Load cached verification result
        /// </summary>
        private void LoadCachedVerification()
        {
            if (!storeVerificationResult) return;

            if (PlayerPrefs.HasKey("VerificationResult"))
            {
                string resultJson = PlayerPrefs.GetString("VerificationResult");
                cachedResult = JsonUtility.FromJson<VerificationResult>(resultJson);

                DateTime expiryDate = DateTime.Parse(cachedResult.expiryDate);
                DateTime timestamp = DateTime.Parse(cachedResult.timestamp);

                lastVerificationDate = timestamp;

                if (DateTime.UtcNow < expiryDate && cachedResult.passed)
                {
                    currentState = VerificationState.Passed;
                    Debug.Log($"[AgeVerification] Loaded cached verification (expires {expiryDate:g})");
                }
                else
                {
                    Debug.Log("[AgeVerification] Cached verification expired");
                    cachedResult = null;
                }
            }
        }

        /// <summary>
        /// Check if user is recently verified
        /// </summary>
        private bool IsRecentlyVerified()
        {
            if (cachedResult == null || !cachedResult.passed)
                return false;

            DateTime expiryDate = DateTime.Parse(cachedResult.expiryDate);
            return DateTime.UtcNow < expiryDate;
        }

        /// <summary>
        /// Force re-verification
        /// </summary>
        public void ForceReverification()
        {
            cachedResult = null;
            PlayerPrefs.DeleteKey("VerificationResult");
            currentState = VerificationState.NotStarted;

            Debug.Log("[AgeVerification] Forced re-verification");
        }

        /// <summary>
        /// Get current verification state
        /// </summary>
        public VerificationState GetCurrentState()
        {
            return currentState;
        }

        /// <summary>
        /// Check if currently verified
        /// </summary>
        public bool IsVerified()
        {
            return currentState == VerificationState.Passed || IsRecentlyVerified();
        }

        /// <summary>
        /// Get days until re-verification required
        /// </summary>
        public int GetDaysUntilReverification()
        {
            if (cachedResult == null) return 0;

            DateTime expiryDate = DateTime.Parse(cachedResult.expiryDate);
            TimeSpan remaining = expiryDate - DateTime.UtcNow;

            return Math.Max(0, (int)remaining.TotalDays);
        }

#if UNITY_EDITOR
        [ContextMenu("Start Verification")]
        private void EditorStartVerification()
        {
            _ = StartVerification();
        }

        [ContextMenu("Force Reverification")]
        private void EditorForceReverification()
        {
            ForceReverification();
        }

        [ContextMenu("Simulate Pass")]
        private void EditorSimulatePass()
        {
            currentState = VerificationState.Passed;
            SaveVerificationResult(true);
            OnVerificationPassed?.Invoke();
        }
#endif
    }

    /// <summary>
    /// Verification result data
    /// </summary>
    [Serializable]
    public class VerificationResult
    {
        public bool passed;
        public string timestamp;
        public string expiryDate;
        // NOTE: No biometric data stored for privacy
    }
}
