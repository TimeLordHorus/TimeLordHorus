using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections.Generic;
using Sanctuary.Verification;

namespace Sanctuary.UI
{
    /// <summary>
    /// User interface for The Gate age verification system
    /// Presents camera preview and challenge questions in VR-friendly format
    /// </summary>
    public class AgeVerificationUI : MonoBehaviour
    {
        [Header("Panel References")]
        [SerializeField] private GameObject welcomePanel;
        [SerializeField] private GameObject cameraPanel;
        [SerializeField] private GameObject challengePanel;
        [SerializeField] private GameObject resultPanel;

        [Header("Welcome Panel")]
        [SerializeField] private TextMeshProUGUI welcomeText;
        [SerializeField] private TextMeshProUGUI privacyNoticeText;
        [SerializeField] private Button startButton;
        [SerializeField] private Toggle privacyAgreementToggle;

        [Header("Camera Panel")]
        [SerializeField] private RawImage cameraPreview;
        [SerializeField] private TextMeshProUGUI cameraInstructionsText;
        [SerializeField] private Slider captureProgressBar;
        [SerializeField] private TextMeshProUGUI captureProgressText;

        [Header("Challenge Panel")]
        [SerializeField] private TextMeshProUGUI questionText;
        [SerializeField] private TextMeshProUGUI questionNumberText;
        [SerializeField] private Button[] answerButtons;
        [SerializeField] private Slider timeoutProgressBar;

        [Header("Result Panel")]
        [SerializeField] private TextMeshProUGUI resultTitleText;
        [SerializeField] private TextMeshProUGUI resultMessageText;
        [SerializeField] private Button continueButton;
        [SerializeField] private Button retryButton;

        [Header("Settings")]
        [SerializeField] private float timeoutDuration = 30f;
        [SerializeField] private Color correctColor = Color.green;
        [SerializeField] private Color incorrectColor = Color.red;

        // References
        private AgeVerificationManager verificationManager;
        private ChallengeQuestionSystem challengeSystem;
        private FacialAgeEstimator facialEstimator;

        // State
        private float questionStartTime;
        private bool isAnsweringQuestion = false;

        private void Start()
        {
            verificationManager = AgeVerificationManager.Instance;

            if (verificationManager == null)
            {
                Debug.LogError("[VerificationUI] AgeVerificationManager not found!");
                return;
            }

            // Subscribe to events
            verificationManager.OnVerificationStarted.AddListener(OnVerificationStarted);
            verificationManager.OnVerificationPassed.AddListener(OnVerificationPassed);
            verificationManager.OnVerificationFailed.AddListener(OnVerificationFailed);
            verificationManager.OnVerificationProgress.AddListener(OnVerificationProgress);

            // Find challenge system
            challengeSystem = FindObjectOfType<ChallengeQuestionSystem>();
            if (challengeSystem != null)
            {
                challengeSystem.OnQuestionPresented += OnQuestionPresented;
                challengeSystem.OnQuestionAnswered += OnQuestionAnswered;
            }

            // Find facial estimator
            facialEstimator = FindObjectOfType<FacialAgeEstimator>();

            // Setup buttons
            if (startButton != null)
                startButton.onClick.AddListener(OnStartButtonClicked);

            if (continueButton != null)
                continueButton.onClick.AddListener(OnContinueButtonClicked);

            if (retryButton != null)
                retryButton.onClick.AddListener(OnRetryButtonClicked);

            // Setup answer buttons
            for (int i = 0; i < answerButtons.Length; i++)
            {
                int index = i; // Capture for closure
                if (answerButtons[i] != null)
                {
                    answerButtons[i].onClick.AddListener(() => OnAnswerButtonClicked(index));
                }
            }

            // Setup privacy toggle
            if (privacyAgreementToggle != null)
            {
                privacyAgreementToggle.onValueChanged.AddListener(OnPrivacyToggleChanged);
            }

            // Setup privacy notice
            if (privacyNoticeText != null)
            {
                privacyNoticeText.text = GetPrivacyNotice();
            }

            // Check if already verified
            if (verificationManager.IsVerified())
            {
                ShowWelcomePanel();
                UpdateWelcomeText("You are already verified!");
                if (startButton != null)
                    startButton.GetComponentInChildren<TextMeshProUGUI>().text = "Continue to Sanctuary";
            }
            else
            {
                ShowWelcomePanel();
            }
        }

        private void Update()
        {
            // Update camera preview
            if (cameraPanel != null && cameraPanel.activeSelf && facialEstimator != null)
            {
                var webcamTexture = facialEstimator.GetWebcamTexture();
                if (webcamTexture != null && cameraPreview != null)
                {
                    cameraPreview.texture = webcamTexture;
                }
            }

            // Update question timeout
            if (isAnsweringQuestion && timeoutProgressBar != null)
            {
                float elapsed = Time.time - questionStartTime;
                float progress = 1f - (elapsed / timeoutDuration);
                timeoutProgressBar.value = Mathf.Clamp01(progress);

                if (progress <= 0f)
                {
                    isAnsweringQuestion = false;
                }
            }
        }

        private void OnDestroy()
        {
            if (verificationManager != null)
            {
                verificationManager.OnVerificationStarted.RemoveListener(OnVerificationStarted);
                verificationManager.OnVerificationPassed.RemoveListener(OnVerificationPassed);
                verificationManager.OnVerificationFailed.RemoveListener(OnVerificationFailed);
                verificationManager.OnVerificationProgress.RemoveListener(OnVerificationProgress);
            }

            if (challengeSystem != null)
            {
                challengeSystem.OnQuestionPresented -= OnQuestionPresented;
                challengeSystem.OnQuestionAnswered -= OnQuestionAnswered;
            }
        }

        // ========== Button Handlers ==========

        private void OnStartButtonClicked()
        {
            if (verificationManager.IsVerified())
            {
                // Already verified, continue to main scene
                OnContinueButtonClicked();
                return;
            }

            if (privacyAgreementToggle != null && !privacyAgreementToggle.isOn)
            {
                Debug.LogWarning("[VerificationUI] Privacy agreement not accepted");
                // Show warning
                return;
            }

            Debug.Log("[VerificationUI] Starting verification");
            _ = verificationManager.StartVerification();
        }

        private void OnContinueButtonClicked()
        {
            Debug.Log("[VerificationUI] Continuing to Sanctuary");
            // TODO: Load main scene
            gameObject.SetActive(false);
        }

        private void OnRetryButtonClicked()
        {
            Debug.Log("[VerificationUI] Retrying verification");
            verificationManager.ForceReverification();
            ShowWelcomePanel();
        }

        private void OnAnswerButtonClicked(int answerIndex)
        {
            if (!isAnsweringQuestion) return;

            Debug.Log($"[VerificationUI] Answer selected: {answerIndex}");

            isAnsweringQuestion = false;

            // Submit answer to challenge system
            if (challengeSystem != null)
            {
                challengeSystem.SubmitAnswer(answerIndex);
            }
        }

        private void OnPrivacyToggleChanged(bool isOn)
        {
            if (startButton != null)
            {
                startButton.interactable = isOn;
            }
        }

        // ========== Event Handlers ==========

        private void OnVerificationStarted()
        {
            Debug.Log("[VerificationUI] Verification started");
            ShowCameraPanel();
            UpdateCameraInstructions("Please look at the camera and hold still...");
        }

        private void OnVerificationPassed()
        {
            Debug.Log("[VerificationUI] Verification passed");
            ShowResultPanel(true);
        }

        private void OnVerificationFailed()
        {
            Debug.Log("[VerificationUI] Verification failed");
            ShowResultPanel(false);
        }

        private void OnVerificationProgress(float progress)
        {
            if (captureProgressBar != null)
            {
                captureProgressBar.value = progress;
            }

            if (captureProgressText != null)
            {
                captureProgressText.text = $"{Mathf.RoundToInt(progress * 100)}%";
            }

            // Update instructions based on progress
            if (progress < 0.5f)
            {
                UpdateCameraInstructions("Analyzing facial features...");
            }
            else if (progress < 1.0f)
            {
                UpdateCameraInstructions("Preparing challenge questions...");
            }
        }

        private void OnQuestionPresented(ChallengeQuestion question, int questionNumber)
        {
            Debug.Log($"[VerificationUI] Presenting question {questionNumber}");

            ShowChallengePanel();

            // Update question text
            if (questionText != null)
            {
                questionText.text = question.questionText;
            }

            if (questionNumberText != null)
            {
                questionNumberText.text = $"Question {questionNumber}";
            }

            // Update answer buttons
            for (int i = 0; i < answerButtons.Length && i < question.answers.Count; i++)
            {
                if (answerButtons[i] != null)
                {
                    answerButtons[i].gameObject.SetActive(true);
                    var buttonText = answerButtons[i].GetComponentInChildren<TextMeshProUGUI>();
                    if (buttonText != null)
                    {
                        buttonText.text = question.answers[i];
                    }

                    // Reset button color
                    var colors = answerButtons[i].colors;
                    colors.normalColor = Color.white;
                    answerButtons[i].colors = colors;
                }
            }

            // Hide unused buttons
            for (int i = question.answers.Count; i < answerButtons.Length; i++)
            {
                if (answerButtons[i] != null)
                {
                    answerButtons[i].gameObject.SetActive(false);
                }
            }

            isAnsweringQuestion = true;
            questionStartTime = Time.time;

            if (timeoutProgressBar != null)
            {
                timeoutProgressBar.value = 1f;
            }
        }

        private void OnQuestionAnswered(bool correct)
        {
            Debug.Log($"[VerificationUI] Question answered: {(correct ? "CORRECT" : "INCORRECT")}");

            // Visual feedback (flash green/red)
            // This would be implemented with animation/coroutine
        }

        // ========== Panel Management ==========

        private void ShowWelcomePanel()
        {
            HideAllPanels();
            if (welcomePanel != null)
                welcomePanel.SetActive(true);
        }

        private void ShowCameraPanel()
        {
            HideAllPanels();
            if (cameraPanel != null)
                cameraPanel.SetActive(true);
        }

        private void ShowChallengePanel()
        {
            HideAllPanels();
            if (challengePanel != null)
                challengePanel.SetActive(true);
        }

        private void ShowResultPanel(bool passed)
        {
            HideAllPanels();
            if (resultPanel != null)
                resultPanel.SetActive(true);

            if (resultTitleText != null)
            {
                resultTitleText.text = passed ? "Verification Successful!" : "Verification Failed";
                resultTitleText.color = passed ? correctColor : incorrectColor;
            }

            if (resultMessageText != null)
            {
                if (passed)
                {
                    resultMessageText.text = "Welcome to Sanctuary! You may now enter the metaverse.";
                }
                else
                {
                    resultMessageText.text = "We were unable to verify your age. Please ensure:\n" +
                                            "• Good lighting for facial capture\n" +
                                            "• You answer questions carefully\n" +
                                            "• You meet the minimum age requirement (18+)";
                }
            }

            if (continueButton != null)
                continueButton.gameObject.SetActive(passed);

            if (retryButton != null)
                retryButton.gameObject.SetActive(!passed);
        }

        private void HideAllPanels()
        {
            if (welcomePanel != null) welcomePanel.SetActive(false);
            if (cameraPanel != null) cameraPanel.SetActive(false);
            if (challengePanel != null) challengePanel.SetActive(false);
            if (resultPanel != null) resultPanel.SetActive(false);
        }

        // ========== Helper Methods ==========

        private void UpdateWelcomeText(string message)
        {
            if (welcomeText != null)
            {
                welcomeText.text = message;
            }
        }

        private void UpdateCameraInstructions(string instructions)
        {
            if (cameraInstructionsText != null)
            {
                cameraInstructionsText.text = instructions;
            }
        }

        private string GetPrivacyNotice()
        {
            return "Privacy Notice:\n\n" +
                   "• Facial analysis is performed entirely on your device\n" +
                   "• No biometric data is transmitted or stored\n" +
                   "• Only verification result (pass/fail) is saved locally\n" +
                   "• You may be re-verified periodically (every 30 days)\n" +
                   "• You must be 18+ to enter Sanctuary\n\n" +
                   "By proceeding, you agree to these terms.";
        }

#if UNITY_EDITOR
        [ContextMenu("Show Welcome")]
        private void EditorShowWelcome()
        {
            ShowWelcomePanel();
        }

        [ContextMenu("Show Camera")]
        private void EditorShowCamera()
        {
            ShowCameraPanel();
        }

        [ContextMenu("Show Challenge")]
        private void EditorShowChallenge()
        {
            ShowChallengePanel();
        }

        [ContextMenu("Show Result (Pass)")]
        private void EditorShowResultPass()
        {
            ShowResultPanel(true);
        }

        [ContextMenu("Show Result (Fail)")]
        private void EditorShowResultFail()
        {
            ShowResultPanel(false);
        }
#endif
    }
}
