"""
Firebase Admin SDK service for user authentication and Firestore database access
Handles user profiles, creation storage, and social features for Sanctuary VR
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Firebase Admin SDK (optional - graceful degradation if not configured)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("[Firebase] firebase-admin not installed - Firebase features disabled")


class FirebaseService:
    """Service for Firebase authentication and Firestore database operations"""

    def __init__(self):
        self.app = None
        self.db = None
        self.bucket = None
        self.initialized = False

        if FIREBASE_AVAILABLE:
            self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-credentials.json')
            project_id = os.getenv('FIREBASE_PROJECT_ID', 'sanctuary-vr')
            storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET', 'sanctuary-vr.appspot.com')

            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Initialize with service account credentials
                if os.path.exists(credentials_path):
                    cred = credentials.Certificate(credentials_path)
                    self.app = firebase_admin.initialize_app(cred, {
                        'projectId': project_id,
                        'storageBucket': storage_bucket
                    })
                    print(f"[Firebase] Initialized with credentials from {credentials_path}")
                else:
                    # Try to initialize with default credentials (for deployed environments)
                    self.app = firebase_admin.initialize_app()
                    print("[Firebase] Initialized with default credentials")
            else:
                self.app = firebase_admin.get_app()
                print("[Firebase] Using existing Firebase app")

            # Initialize Firestore client
            self.db = firestore.client()

            # Initialize Storage bucket
            self.bucket = storage.bucket()

            self.initialized = True
            print("[Firebase] Firebase service initialized successfully")

        except Exception as e:
            print(f"[Firebase] Initialization failed: {e}")
            self.initialized = False

    # ========== User Profile Operations ==========

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from Firestore"""
        if not self.initialized:
            return None

        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()
            else:
                print(f"[Firebase] User profile not found: {user_id}")
                return None

        except Exception as e:
            print(f"[Firebase] Error getting user profile: {e}")
            return None

    def create_user_profile(self, user_id: str, email: str, display_name: str) -> Dict[str, Any]:
        """Create a new user profile in Firestore"""
        if not self.initialized:
            return None

        try:
            profile = {
                'userId': user_id,
                'email': email,
                'displayName': display_name,
                'isAnonymous': False,
                'createdAt': datetime.utcnow().isoformat(),
                'lastLogin': datetime.utcnow().isoformat(),
                'totalCreations': 0,
                'totalMeditationMinutes': 0,
                'level': 1,
                'xp': 0,
                'avatarPreset': 'default',
                'unlockedTitles': {},
                'favoriteCreations': [],
                'friends': [],
                'isProfilePublic': True
            }

            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set(profile)

            print(f"[Firebase] Created user profile: {user_id}")
            return profile

        except Exception as e:
            print(f"[Firebase] Error creating user profile: {e}")
            return None

    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile in Firestore"""
        if not self.initialized:
            return False

        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update(updates)

            print(f"[Firebase] Updated user profile: {user_id}")
            return True

        except Exception as e:
            print(f"[Firebase] Error updating user profile: {e}")
            return False

    def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        return self.update_user_profile(user_id, {
            'lastLogin': datetime.utcnow().isoformat()
        })

    # ========== Creation Operations ==========

    def save_creation(self, creation: Dict[str, Any]) -> bool:
        """Save a user's creation to Firestore"""
        if not self.initialized:
            return False

        try:
            generation_id = creation.get('generationId')
            if not generation_id:
                print("[Firebase] Creation missing generationId")
                return False

            # Add timestamp if not present
            if 'createdAt' not in creation:
                creation['createdAt'] = datetime.utcnow().isoformat()

            # Save to creations collection
            doc_ref = self.db.collection('creations').document(generation_id)
            doc_ref.set(creation)

            # Update user's creation count
            user_id = creation.get('userId')
            if user_id:
                user_ref = self.db.collection('users').document(user_id)
                user_ref.update({
                    'totalCreations': firestore.Increment(1)
                })

            print(f"[Firebase] Saved creation: {generation_id}")
            return True

        except Exception as e:
            print(f"[Firebase] Error saving creation: {e}")
            return False

    def get_user_creations(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all creations for a user"""
        if not self.initialized:
            return []

        try:
            query = (self.db.collection('creations')
                    .where('userId', '==', user_id)
                    .order_by('createdAt', direction=firestore.Query.DESCENDING)
                    .limit(limit)
                    .offset(offset))

            docs = query.stream()
            creations = [doc.to_dict() for doc in docs]

            print(f"[Firebase] Retrieved {len(creations)} creations for user {user_id}")
            return creations

        except Exception as e:
            print(f"[Firebase] Error getting user creations: {e}")
            return []

    def get_creation(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific creation by ID"""
        if not self.initialized:
            return None

        try:
            doc_ref = self.db.collection('creations').document(generation_id)
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()
            else:
                return None

        except Exception as e:
            print(f"[Firebase] Error getting creation: {e}")
            return None

    def delete_creation(self, generation_id: str, user_id: str) -> bool:
        """Delete a creation (with ownership verification)"""
        if not self.initialized:
            return False

        try:
            # Verify ownership
            creation = self.get_creation(generation_id)
            if not creation or creation.get('userId') != user_id:
                print(f"[Firebase] Unauthorized deletion attempt: {generation_id}")
                return False

            # Delete from Firestore
            doc_ref = self.db.collection('creations').document(generation_id)
            doc_ref.delete()

            # Decrement user's creation count
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'totalCreations': firestore.Increment(-1)
            })

            print(f"[Firebase] Deleted creation: {generation_id}")
            return True

        except Exception as e:
            print(f"[Firebase] Error deleting creation: {e}")
            return False

    # ========== XP and Leveling ==========

    def add_xp(self, user_id: str, xp_amount: int, reason: str = "") -> Dict[str, Any]:
        """Add XP to user and handle leveling"""
        if not self.initialized:
            return None

        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()

            if not user_doc.exists:
                print(f"[Firebase] User not found: {user_id}")
                return None

            user_data = user_doc.to_dict()
            current_xp = user_data.get('xp', 0)
            current_level = user_data.get('level', 1)

            new_xp = current_xp + xp_amount
            new_level = 1 + (new_xp // 100)  # 100 XP per level

            updates = {
                'xp': new_xp,
                'level': new_level
            }

            user_ref.update(updates)

            leveled_up = new_level > current_level

            print(f"[Firebase] Added {xp_amount} XP to {user_id} ({reason}). Level: {new_level}")

            return {
                'xp': new_xp,
                'level': new_level,
                'leveledUp': leveled_up,
                'previousLevel': current_level
            }

        except Exception as e:
            print(f"[Firebase] Error adding XP: {e}")
            return None

    def track_meditation(self, user_id: str, minutes: int) -> bool:
        """Track meditation session and award XP"""
        if not self.initialized:
            return False

        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'totalMeditationMinutes': firestore.Increment(minutes)
            })

            # Award XP (2 XP per minute)
            self.add_xp(user_id, minutes * 2, "meditation")

            print(f"[Firebase] Tracked {minutes} minutes of meditation for {user_id}")
            return True

        except Exception as e:
            print(f"[Firebase] Error tracking meditation: {e}")
            return False

    # ========== Social Features ==========

    def get_public_creations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get public creations from all users"""
        if not self.initialized:
            return []

        try:
            query = (self.db.collection('creations')
                    .where('isPublic', '==', True)
                    .order_by('createdAt', direction=firestore.Query.DESCENDING)
                    .limit(limit))

            docs = query.stream()
            creations = [doc.to_dict() for doc in docs]

            return creations

        except Exception as e:
            print(f"[Firebase] Error getting public creations: {e}")
            return []

    def like_creation(self, generation_id: str, user_id: str) -> bool:
        """Like a creation"""
        if not self.initialized:
            return False

        try:
            doc_ref = self.db.collection('creations').document(generation_id)
            doc_ref.update({
                'likes': firestore.Increment(1)
            })

            print(f"[Firebase] User {user_id} liked creation {generation_id}")
            return True

        except Exception as e:
            print(f"[Firebase] Error liking creation: {e}")
            return False


# Singleton instance
_firebase_service = None

def get_firebase_service() -> FirebaseService:
    """Get singleton Firebase service instance"""
    global _firebase_service
    if _firebase_service is None:
        _firebase_service = FirebaseService()
    return _firebase_service
