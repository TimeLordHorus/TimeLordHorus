using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Events;

namespace Sanctuary.Core
{
    /// <summary>
    /// Firebase integration manager for user authentication and data storage
    /// Handles user profiles, creation storage, and social features
    /// </summary>
    public class FirebaseManager : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string firebaseApiKey = "";
        [SerializeField] private string firebaseProjectId = "";
        [SerializeField] private string firebaseAppId = "";
        [SerializeField] private bool enableOfflineMode = true;

        [Header("Events")]
        public UnityEvent<UserProfile> OnUserSignedIn;
        public UnityEvent OnUserSignedOut;
        public UnityEvent<string> OnAuthError;
        public UnityEvent<UserProfile> OnProfileUpdated;

        // Singleton
        private static FirebaseManager instance;
        public static FirebaseManager Instance => instance;

        // State
        private bool isInitialized = false;
        private UserProfile currentUser;
        private Dictionary<string, object> offlineCache = new Dictionary<string, object>();

        // Constants
        private const string USERS_COLLECTION = "users";
        private const string CREATIONS_COLLECTION = "creations";
        private const string COLLECTIONS_COLLECTION = "collections";

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
        }

        private async void Start()
        {
            await InitializeFirebase();
        }

        /// <summary>
        /// Initialize Firebase SDK
        /// </summary>
        private async Task InitializeFirebase()
        {
            try
            {
                Debug.Log("[Firebase] Initializing Firebase...");

                // In production, this would initialize Firebase SDK
                // For now, we'll simulate initialization
                await Task.Delay(500);

                isInitialized = true;
                Debug.Log("[Firebase] Firebase initialized successfully");
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Initialization failed: {e.Message}");
                OnAuthError?.Invoke($"Firebase initialization failed: {e.Message}");
            }
        }

        /// <summary>
        /// Sign in with email and password
        /// </summary>
        public async Task<bool> SignInWithEmail(string email, string password)
        {
            if (!isInitialized)
            {
                Debug.LogError("[Firebase] Firebase not initialized");
                return false;
            }

            try
            {
                Debug.Log($"[Firebase] Signing in user: {email}");

                // In production, this would call Firebase Auth
                // For now, simulate authentication
                await Task.Delay(1000);

                // Create user profile
                currentUser = new UserProfile
                {
                    userId = GenerateUserId(email),
                    email = email,
                    displayName = email.Split('@')[0],
                    createdAt = DateTime.UtcNow.ToString("o"),
                    lastLogin = DateTime.UtcNow.ToString("o"),
                    totalCreations = 0,
                    totalMeditationMinutes = 0,
                    level = 1,
                    xp = 0
                };

                // Fetch or create user profile from Firestore
                await FetchUserProfile(currentUser.userId);

                OnUserSignedIn?.Invoke(currentUser);
                Debug.Log($"[Firebase] User signed in: {currentUser.userId}");

                return true;
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Sign in failed: {e.Message}");
                OnAuthError?.Invoke($"Sign in failed: {e.Message}");
                return false;
            }
        }

        /// <summary>
        /// Sign in anonymously
        /// </summary>
        public async Task<bool> SignInAnonymously()
        {
            if (!isInitialized)
            {
                Debug.LogError("[Firebase] Firebase not initialized");
                return false;
            }

            try
            {
                Debug.Log("[Firebase] Signing in anonymously...");

                await Task.Delay(500);

                string anonymousId = $"anon_{Guid.NewGuid().ToString().Substring(0, 8)}";

                currentUser = new UserProfile
                {
                    userId = anonymousId,
                    displayName = $"Guest_{anonymousId.Substring(5)}",
                    isAnonymous = true,
                    createdAt = DateTime.UtcNow.ToString("o"),
                    lastLogin = DateTime.UtcNow.ToString("o"),
                    totalCreations = 0,
                    totalMeditationMinutes = 0,
                    level = 1,
                    xp = 0
                };

                OnUserSignedIn?.Invoke(currentUser);
                Debug.Log($"[Firebase] Anonymous user signed in: {currentUser.userId}");

                return true;
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Anonymous sign in failed: {e.Message}");
                OnAuthError?.Invoke($"Anonymous sign in failed: {e.Message}");
                return false;
            }
        }

        /// <summary>
        /// Sign out current user
        /// </summary>
        public void SignOut()
        {
            if (currentUser != null)
            {
                Debug.Log($"[Firebase] Signing out user: {currentUser.userId}");
                currentUser = null;
                OnUserSignedOut?.Invoke();
            }
        }

        /// <summary>
        /// Fetch user profile from Firestore
        /// </summary>
        private async Task FetchUserProfile(string userId)
        {
            try
            {
                Debug.Log($"[Firebase] Fetching user profile: {userId}");

                // In production, this would query Firestore
                // For now, check offline cache or create new profile
                if (offlineCache.ContainsKey($"user_{userId}"))
                {
                    currentUser = offlineCache[$"user_{userId}"] as UserProfile;
                    Debug.Log($"[Firebase] Loaded user from cache");
                }
                else
                {
                    // Create new profile in Firestore
                    await SaveUserProfile(currentUser);
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Failed to fetch user profile: {e.Message}");
            }
        }

        /// <summary>
        /// Save user profile to Firestore
        /// </summary>
        public async Task SaveUserProfile(UserProfile profile)
        {
            if (!isInitialized)
            {
                Debug.LogError("[Firebase] Firebase not initialized");
                return;
            }

            try
            {
                Debug.Log($"[Firebase] Saving user profile: {profile.userId}");

                // In production, this would save to Firestore
                // For now, save to offline cache
                offlineCache[$"user_{profile.userId}"] = profile;

                await Task.Delay(200);

                OnProfileUpdated?.Invoke(profile);
                Debug.Log("[Firebase] User profile saved");
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Failed to save user profile: {e.Message}");
            }
        }

        /// <summary>
        /// Save a creation to user's collection
        /// </summary>
        public async Task<bool> SaveCreation(Creation creation)
        {
            if (currentUser == null)
            {
                Debug.LogError("[Firebase] No user signed in");
                return false;
            }

            try
            {
                Debug.Log($"[Firebase] Saving creation: {creation.generationId}");

                creation.userId = currentUser.userId;
                creation.createdAt = DateTime.UtcNow.ToString("o");

                // In production, this would save to Firestore
                offlineCache[$"creation_{creation.generationId}"] = creation;

                // Update user stats
                currentUser.totalCreations++;
                await SaveUserProfile(currentUser);

                await Task.Delay(200);

                Debug.Log($"[Firebase] Creation saved: {creation.generationId}");
                return true;
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Failed to save creation: {e.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get all creations for current user
        /// </summary>
        public async Task<List<Creation>> GetUserCreations()
        {
            if (currentUser == null)
            {
                Debug.LogError("[Firebase] No user signed in");
                return new List<Creation>();
            }

            try
            {
                Debug.Log($"[Firebase] Fetching creations for user: {currentUser.userId}");

                List<Creation> creations = new List<Creation>();

                // In production, this would query Firestore
                // For now, get from offline cache
                foreach (var key in offlineCache.Keys)
                {
                    if (key.StartsWith("creation_"))
                    {
                        Creation creation = offlineCache[key] as Creation;
                        if (creation != null && creation.userId == currentUser.userId)
                        {
                            creations.Add(creation);
                        }
                    }
                }

                await Task.Delay(200);

                Debug.Log($"[Firebase] Found {creations.Count} creations");
                return creations;
            }
            catch (Exception e)
            {
                Debug.LogError($"[Firebase] Failed to get user creations: {e.Message}");
                return new List<Creation>();
            }
        }

        /// <summary>
        /// Update user XP and level
        /// </summary>
        public async Task AddXP(int xpAmount, string reason)
        {
            if (currentUser == null)
            {
                Debug.LogWarning("[Firebase] No user signed in");
                return;
            }

            int oldLevel = currentUser.level;
            currentUser.xp += xpAmount;

            // Level up calculation (100 XP per level)
            int newLevel = 1 + (currentUser.xp / 100);

            if (newLevel > oldLevel)
            {
                currentUser.level = newLevel;
                Debug.Log($"[Firebase] User leveled up! {oldLevel} → {newLevel}");
            }

            Debug.Log($"[Firebase] Added {xpAmount} XP ({reason}). Total: {currentUser.xp} XP, Level: {currentUser.level}");

            await SaveUserProfile(currentUser);
        }

        /// <summary>
        /// Track meditation session
        /// </summary>
        public async Task TrackMeditation(int minutes)
        {
            if (currentUser == null)
            {
                Debug.LogWarning("[Firebase] No user signed in");
                return;
            }

            currentUser.totalMeditationMinutes += minutes;
            await AddXP(minutes * 2, "meditation");

            Debug.Log($"[Firebase] Tracked {minutes} minutes of meditation");
        }

        /// <summary>
        /// Get current user profile
        /// </summary>
        public UserProfile GetCurrentUser()
        {
            return currentUser;
        }

        /// <summary>
        /// Check if user is signed in
        /// </summary>
        public bool IsSignedIn()
        {
            return currentUser != null;
        }

        /// <summary>
        /// Generate user ID from email
        /// </summary>
        private string GenerateUserId(string email)
        {
            // In production, Firebase Auth would provide this
            return $"user_{email.GetHashCode():X8}";
        }

#if UNITY_EDITOR
        [ContextMenu("Test Sign In")]
        private void TestSignIn()
        {
            _ = SignInWithEmail("test@sanctuary.com", "password123");
        }

        [ContextMenu("Test Anonymous Sign In")]
        private void TestAnonymousSignIn()
        {
            _ = SignInAnonymously();
        }

        [ContextMenu("Test Add XP")]
        private void TestAddXP()
        {
            _ = AddXP(50, "test");
        }
#endif
    }

    /// <summary>
    /// User profile data model
    /// </summary>
    [Serializable]
    public class UserProfile
    {
        public string userId;
        public string email;
        public string displayName;
        public bool isAnonymous = false;
        public string createdAt;
        public string lastLogin;

        // Stats
        public int totalCreations;
        public int totalMeditationMinutes;
        public int level;
        public int xp;

        // Customization
        public string avatarPreset = "default";
        public Dictionary<string, bool> unlockedTitles = new Dictionary<string, bool>();
        public List<string> favoriteCreations = new List<string>();

        // Social
        public List<string> friends = new List<string>();
        public bool isProfilePublic = true;
    }

    /// <summary>
    /// Creation data model for Firestore
    /// </summary>
    [Serializable]
    public class Creation
    {
        public string generationId;
        public string userId;
        public string prompt;
        public string modelUrl;
        public string thumbnailUrl;
        public string createdAt;
        public int polycount;
        public bool isPublic = false;
        public int likes = 0;
        public List<string> tags = new List<string>();
    }
}
