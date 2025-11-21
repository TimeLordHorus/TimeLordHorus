using UnityEngine;
using UnityEngine.UI;
using TMPro;
using Sanctuary.Core;
using System.Collections.Generic;

namespace Sanctuary.UI
{
    /// <summary>
    /// User profile UI manager
    /// Displays user stats, creations gallery, and profile settings
    /// </summary>
    public class UserProfileUI : MonoBehaviour
    {
        [Header("Profile Display")]
        [SerializeField] private TextMeshProUGUI displayNameText;
        [SerializeField] private TextMeshProUGUI levelText;
        [SerializeField] private TextMeshProUGUI xpText;
        [SerializeField] private Slider xpProgressBar;
        [SerializeField] private Image avatarPreview;

        [Header("Stats Display")]
        [SerializeField] private TextMeshProUGUI totalCreationsText;
        [SerializeField] private TextMeshProUGUI meditationMinutesText;
        [SerializeField] private TextMeshProUGUI accountAgeText;

        [Header("Creations Gallery")]
        [SerializeField] private Transform creationsContainer;
        [SerializeField] private GameObject creationCardPrefab;
        [SerializeField] private int maxDisplayedCreations = 12;

        [Header("Authentication")]
        [SerializeField] private GameObject loginPanel;
        [SerializeField] private GameObject profilePanel;
        [SerializeField] private TMP_InputField emailInput;
        [SerializeField] private TMP_InputField passwordInput;
        [SerializeField] private Button signInButton;
        [SerializeField] private Button signInAnonymouslyButton;
        [SerializeField] private Button signOutButton;

        [Header("Settings")]
        [SerializeField] private Toggle publicProfileToggle;
        [SerializeField] private TMP_InputField displayNameInput;
        [SerializeField] private Button saveSettingsButton;

        private FirebaseManager firebaseManager;
        private UserProfile currentUserProfile;

        private void Start()
        {
            firebaseManager = FirebaseManager.Instance;

            if (firebaseManager == null)
            {
                Debug.LogError("[UserProfileUI] FirebaseManager not found!");
                return;
            }

            // Subscribe to Firebase events
            firebaseManager.OnUserSignedIn.AddListener(OnUserSignedIn);
            firebaseManager.OnUserSignedOut.AddListener(OnUserSignedOut);
            firebaseManager.OnProfileUpdated.AddListener(OnProfileUpdated);

            // Setup UI buttons
            if (signInButton != null)
                signInButton.onClick.AddListener(OnSignInClicked);

            if (signInAnonymouslyButton != null)
                signInAnonymouslyButton.onClick.AddListener(OnSignInAnonymouslyClicked);

            if (signOutButton != null)
                signOutButton.onClick.AddListener(OnSignOutClicked);

            if (saveSettingsButton != null)
                saveSettingsButton.onClick.AddListener(OnSaveSettingsClicked);

            // Check if already signed in
            if (firebaseManager.IsSignedIn())
            {
                OnUserSignedIn(firebaseManager.GetCurrentUser());
            }
            else
            {
                ShowLoginPanel();
            }
        }

        private void OnDestroy()
        {
            if (firebaseManager != null)
            {
                firebaseManager.OnUserSignedIn.RemoveListener(OnUserSignedIn);
                firebaseManager.OnUserSignedOut.RemoveListener(OnUserSignedOut);
                firebaseManager.OnProfileUpdated.RemoveListener(OnProfileUpdated);
            }
        }

        /// <summary>
        /// Handle user sign in event
        /// </summary>
        private void OnUserSignedIn(UserProfile profile)
        {
            currentUserProfile = profile;
            ShowProfilePanel();
            UpdateProfileDisplay();
            LoadCreationsGallery();

            Debug.Log($"[UserProfileUI] User signed in: {profile.displayName}");
        }

        /// <summary>
        /// Handle user sign out event
        /// </summary>
        private void OnUserSignedOut()
        {
            currentUserProfile = null;
            ShowLoginPanel();
            ClearCreationsGallery();

            Debug.Log("[UserProfileUI] User signed out");
        }

        /// <summary>
        /// Handle profile update event
        /// </summary>
        private void OnProfileUpdated(UserProfile profile)
        {
            currentUserProfile = profile;
            UpdateProfileDisplay();

            Debug.Log("[UserProfileUI] Profile updated");
        }

        /// <summary>
        /// Update profile display with current user data
        /// </summary>
        private void UpdateProfileDisplay()
        {
            if (currentUserProfile == null) return;

            // Display name
            if (displayNameText != null)
            {
                displayNameText.text = currentUserProfile.displayName;
                if (currentUserProfile.isAnonymous)
                {
                    displayNameText.text += " (Guest)";
                }
            }

            // Level and XP
            if (levelText != null)
            {
                levelText.text = $"Level {currentUserProfile.level}";
            }

            if (xpText != null)
            {
                int currentLevelXP = currentUserProfile.xp % 100;
                xpText.text = $"{currentLevelXP} / 100 XP";
            }

            if (xpProgressBar != null)
            {
                int currentLevelXP = currentUserProfile.xp % 100;
                xpProgressBar.value = currentLevelXP / 100f;
            }

            // Stats
            if (totalCreationsText != null)
            {
                totalCreationsText.text = $"{currentUserProfile.totalCreations} Creations";
            }

            if (meditationMinutesText != null)
            {
                int hours = currentUserProfile.totalMeditationMinutes / 60;
                int minutes = currentUserProfile.totalMeditationMinutes % 60;
                meditationMinutesText.text = $"{hours}h {minutes}m Meditation";
            }

            if (accountAgeText != null)
            {
                System.DateTime createdDate = System.DateTime.Parse(currentUserProfile.createdAt);
                System.TimeSpan age = System.DateTime.UtcNow - createdDate;
                accountAgeText.text = $"Member for {age.Days} days";
            }

            // Settings
            if (publicProfileToggle != null)
            {
                publicProfileToggle.isOn = currentUserProfile.isProfilePublic;
            }

            if (displayNameInput != null)
            {
                displayNameInput.text = currentUserProfile.displayName;
            }
        }

        /// <summary>
        /// Load user's creations into gallery
        /// </summary>
        private async void LoadCreationsGallery()
        {
            if (firebaseManager == null || currentUserProfile == null) return;

            ClearCreationsGallery();

            List<Creation> creations = await firebaseManager.GetUserCreations();

            Debug.Log($"[UserProfileUI] Loading {creations.Count} creations");

            int count = 0;
            foreach (Creation creation in creations)
            {
                if (count >= maxDisplayedCreations) break;

                CreateCreationCard(creation);
                count++;
            }
        }

        /// <summary>
        /// Create a creation card in the gallery
        /// </summary>
        private void CreateCreationCard(Creation creation)
        {
            if (creationCardPrefab == null || creationsContainer == null) return;

            GameObject card = Instantiate(creationCardPrefab, creationsContainer);

            // Update card UI (assuming card has these components)
            TextMeshProUGUI promptText = card.transform.Find("PromptText")?.GetComponent<TextMeshProUGUI>();
            if (promptText != null)
            {
                promptText.text = creation.prompt;
            }

            TextMeshProUGUI dateText = card.transform.Find("DateText")?.GetComponent<TextMeshProUGUI>();
            if (dateText != null)
            {
                System.DateTime createdDate = System.DateTime.Parse(creation.createdAt);
                dateText.text = createdDate.ToString("MMM dd, yyyy");
            }

            TextMeshProUGUI polycountText = card.transform.Find("PolycountText")?.GetComponent<TextMeshProUGUI>();
            if (polycountText != null)
            {
                polycountText.text = $"{creation.polycount:N0} tris";
            }

            // Add click handler to view creation
            Button cardButton = card.GetComponent<Button>();
            if (cardButton != null)
            {
                cardButton.onClick.AddListener(() => OnCreationCardClicked(creation));
            }
        }

        /// <summary>
        /// Clear all creation cards from gallery
        /// </summary>
        private void ClearCreationsGallery()
        {
            if (creationsContainer == null) return;

            foreach (Transform child in creationsContainer)
            {
                Destroy(child.gameObject);
            }
        }

        /// <summary>
        /// Handle creation card click
        /// </summary>
        private void OnCreationCardClicked(Creation creation)
        {
            Debug.Log($"[UserProfileUI] Clicked creation: {creation.generationId}");

            // TODO: Open creation detail view or spawn model in scene
        }

        /// <summary>
        /// Show login panel
        /// </summary>
        private void ShowLoginPanel()
        {
            if (loginPanel != null) loginPanel.SetActive(true);
            if (profilePanel != null) profilePanel.SetActive(false);
        }

        /// <summary>
        /// Show profile panel
        /// </summary>
        private void ShowProfilePanel()
        {
            if (loginPanel != null) loginPanel.SetActive(false);
            if (profilePanel != null) profilePanel.SetActive(true);
        }

        /// <summary>
        /// Handle sign in button click
        /// </summary>
        private async void OnSignInClicked()
        {
            if (firebaseManager == null) return;

            string email = emailInput != null ? emailInput.text : "";
            string password = passwordInput != null ? passwordInput.text : "";

            if (string.IsNullOrEmpty(email) || string.IsNullOrEmpty(password))
            {
                Debug.LogWarning("[UserProfileUI] Email or password is empty");
                return;
            }

            Debug.Log($"[UserProfileUI] Signing in: {email}");

            bool success = await firebaseManager.SignInWithEmail(email, password);

            if (!success)
            {
                Debug.LogError("[UserProfileUI] Sign in failed");
                // TODO: Show error message to user
            }
        }

        /// <summary>
        /// Handle anonymous sign in button click
        /// </summary>
        private async void OnSignInAnonymouslyClicked()
        {
            if (firebaseManager == null) return;

            Debug.Log("[UserProfileUI] Signing in anonymously");

            bool success = await firebaseManager.SignInAnonymously();

            if (!success)
            {
                Debug.LogError("[UserProfileUI] Anonymous sign in failed");
                // TODO: Show error message to user
            }
        }

        /// <summary>
        /// Handle sign out button click
        /// </summary>
        private void OnSignOutClicked()
        {
            if (firebaseManager == null) return;

            Debug.Log("[UserProfileUI] Signing out");
            firebaseManager.SignOut();
        }

        /// <summary>
        /// Handle save settings button click
        /// </summary>
        private async void OnSaveSettingsClicked()
        {
            if (firebaseManager == null || currentUserProfile == null) return;

            Debug.Log("[UserProfileUI] Saving settings");

            // Update display name
            if (displayNameInput != null && !string.IsNullOrEmpty(displayNameInput.text))
            {
                currentUserProfile.displayName = displayNameInput.text;
            }

            // Update public profile setting
            if (publicProfileToggle != null)
            {
                currentUserProfile.isProfilePublic = publicProfileToggle.isOn;
            }

            await firebaseManager.SaveUserProfile(currentUserProfile);

            Debug.Log("[UserProfileUI] Settings saved");
            // TODO: Show success message
        }

        /// <summary>
        /// Manually refresh profile display
        /// </summary>
        public void RefreshProfile()
        {
            if (firebaseManager != null && firebaseManager.IsSignedIn())
            {
                currentUserProfile = firebaseManager.GetCurrentUser();
                UpdateProfileDisplay();
                LoadCreationsGallery();
            }
        }

#if UNITY_EDITOR
        [ContextMenu("Refresh Profile")]
        private void EditorRefreshProfile()
        {
            RefreshProfile();
        }
#endif
    }
}
