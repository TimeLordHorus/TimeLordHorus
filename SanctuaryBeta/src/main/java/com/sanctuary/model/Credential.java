package com.sanctuary.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Credential - Real-world certifications, degrees, and documents
 * Verified credentials that provide in-game benefits and real-world recognition
 */
@Entity
@Table(name = "credentials")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Credential {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_profile_id", nullable = false)
    private CharacterProfile characterProfile;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private CredentialType type;

    @Column(name = "issuing_organization", nullable = false)
    private String issuingOrganization;

    @Column(name = "issue_date")
    private LocalDate issueDate;

    @Column(name = "expiration_date")
    private LocalDate expirationDate;

    @Column(name = "credential_id")
    private String credentialId; // External credential ID

    @Column(name = "verification_url")
    private String verificationUrl; // URL to verify credential

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private VerificationStatus verificationStatus = VerificationStatus.PENDING;

    @Column(name = "document_url")
    private String documentUrl; // Encrypted document storage

    @Column(name = "document_hash")
    private String documentHash; // SHA-256 hash for verification

    @Column(nullable = false)
    private Boolean isPublic = false; // Display on public profile

    // In-game benefits
    @Column(name = "experience_bonus")
    private Integer experienceBonus = 0;

    @Column(name = "skill_unlocks", columnDefinition = "TEXT")
    private String skillUnlocks; // JSON array of unlocked skills

    @Column(name = "title_granted")
    private String titleGranted; // Special title for this credential

    @Column(name = "badge_icon_url")
    private String badgeIconUrl;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "verified_at")
    private LocalDateTime verifiedAt;

    public enum CredentialType {
        UNIVERSITY_DEGREE("University Degree"),
        CERTIFICATION("Professional Certification"),
        LICENSE("Professional License"),
        DIPLOMA("Academic Diploma"),
        COURSE_COMPLETION("Course Completion"),
        WORKSHOP("Workshop Attendance"),
        PUBLICATION("Published Work"),
        PATENT("Patent"),
        AWARD("Award or Recognition"),
        SKILL_BADGE("Skill Badge"),
        LANGUAGE_PROFICIENCY("Language Proficiency"),
        OTHER("Other Credential");

        private final String displayName;

        CredentialType(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    public enum VerificationStatus {
        PENDING("Pending Verification"),
        VERIFIED("Verified"),
        REJECTED("Verification Failed"),
        EXPIRED("Credential Expired");

        private final String displayName;

        VerificationStatus(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    /**
     * Check if credential is currently valid
     */
    public boolean isValid() {
        if (verificationStatus != VerificationStatus.VERIFIED) {
            return false;
        }

        if (expirationDate == null) {
            return true;
        }

        return LocalDate.now().isBefore(expirationDate);
    }

    /**
     * Verify the credential
     */
    public void verify() {
        this.verificationStatus = VerificationStatus.VERIFIED;
        this.verifiedAt = LocalDateTime.now();
    }
}
