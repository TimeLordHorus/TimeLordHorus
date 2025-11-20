package com.sanctuary.service;

import com.sanctuary.model.CharacterProfile;
import com.sanctuary.model.Credential;
import com.sanctuary.model.Skill;
import com.sanctuary.model.User;
import com.sanctuary.repository.CharacterProfileRepository;
import com.sanctuary.repository.CredentialRepository;
import com.sanctuary.repository.SkillRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDate;
import java.util.Base64;
import java.util.List;
import java.util.UUID;

/**
 * Credential Service - Manages real-world credentials and verification
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CredentialService {

    private final CredentialRepository credentialRepository;
    private final CharacterProfileRepository characterProfileRepository;
    private final SkillRepository skillRepository;
    private final CharacterService characterService;

    private static final String UPLOAD_DIR = "uploads/credentials/";

    /**
     * Submit a new credential for verification
     */
    @Transactional
    public Credential submitCredential(
            User user,
            String title,
            Credential.CredentialType type,
            String issuingOrganization,
            LocalDate issueDate,
            MultipartFile document
    ) throws IOException, NoSuchAlgorithmException {

        CharacterProfile profile = characterService.getOrCreateProfile(user);

        // Generate unique filename
        String originalFilename = document.getOriginalFilename();
        String extension = originalFilename.substring(originalFilename.lastIndexOf("."));
        String filename = UUID.randomUUID().toString() + extension;

        // Create upload directory if it doesn't exist
        Path uploadPath = Paths.get(UPLOAD_DIR);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        // Save file
        Path filePath = uploadPath.resolve(filename);
        Files.write(filePath, document.getBytes());

        // Calculate SHA-256 hash
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(document.getBytes());
        String hashString = Base64.getEncoder().encodeToString(hash);

        // Create credential
        Credential credential = Credential.builder()
                .characterProfile(profile)
                .title(title)
                .type(type)
                .issuingOrganization(issuingOrganization)
                .issueDate(issueDate)
                .verificationStatus(Credential.VerificationStatus.PENDING)
                .documentUrl(filePath.toString())
                .documentHash(hashString)
                .isPublic(false) // Default to private
                .experienceBonus(calculateExperienceBonus(type))
                .titleGranted(generateTitle(type))
                .build();

        credential = credentialRepository.save(credential);

        log.info("Credential submitted for {}: {} from {}. Status: PENDING",
                profile.getCharacterName(), title, issuingOrganization);

        return credential;
    }

    /**
     * Verify a credential (admin function)
     */
    @Transactional
    public Credential verifyCredential(Long credentialId, boolean approved, String adminNotes) {
        Credential credential = credentialRepository.findById(credentialId)
                .orElseThrow(() -> new RuntimeException("Credential not found"));

        if (approved) {
            credential.verify();

            // Grant benefits
            grantCredentialBenefits(credential);

            log.info("Credential VERIFIED: {} for {}",
                    credential.getTitle(), credential.getCharacterProfile().getCharacterName());
        } else {
            credential.setVerificationStatus(Credential.VerificationStatus.REJECTED);

            log.info("Credential REJECTED: {} for {}. Reason: {}",
                    credential.getTitle(), credential.getCharacterProfile().getCharacterName(), adminNotes);
        }

        return credentialRepository.save(credential);
    }

    /**
     * Grant in-game benefits for verified credential
     */
    private void grantCredentialBenefits(Credential credential) {
        CharacterProfile profile = credential.getCharacterProfile();

        // Award experience bonus
        if (credential.getExperienceBonus() > 0) {
            profile.addExperience(credential.getExperienceBonus());
            characterProfileRepository.save(profile);

            log.info("Granted {} XP to {} for verified credential",
                    credential.getExperienceBonus(), profile.getCharacterName());
        }

        // Unlock related skills
        unlockSkillsForCredential(credential);
    }

    /**
     * Unlock skills based on credential type
     */
    private void unlockSkillsForCredential(Credential credential) {
        CharacterProfile profile = credential.getCharacterProfile();

        Skill.SkillType skillToUnlock = switch (credential.getType()) {
            case UNIVERSITY_DEGREE -> {
                // Check degree field (would need to parse)
                yield Skill.SkillType.PHILOSOPHY; // Default
            }
            case CERTIFICATION -> Skill.SkillType.ENGINEERING;
            case LICENSE -> Skill.SkillType.PROGRAMMING;
            case PUBLICATION -> Skill.SkillType.LITERATURE;
            default -> null;
        };

        if (skillToUnlock != null) {
            // Check if skill already exists
            boolean exists = skillRepository.findByCharacterProfileAndType(profile, skillToUnlock)
                    .isPresent();

            if (!exists) {
                Skill newSkill = Skill.builder()
                        .characterProfile(profile)
                        .type(skillToUnlock)
                        .name(skillToUnlock.getDisplayName())
                        .description("Unlocked via verified credential: " + credential.getTitle())
                        .level(5) // Start at level 5 for credentialed skills
                        .experience(0)
                        .experienceToNextLevel(100)
                        .isActive(true)
                        .build();

                skillRepository.save(newSkill);

                log.info("Unlocked skill {} for {} via credential",
                        skillToUnlock, profile.getCharacterName());
            }
        }
    }

    /**
     * Calculate XP bonus based on credential type
     */
    private int calculateExperienceBonus(Credential.CredentialType type) {
        return switch (type) {
            case UNIVERSITY_DEGREE -> 100;
            case CERTIFICATION -> 50;
            case LICENSE -> 75;
            case DIPLOMA -> 60;
            case COURSE_COMPLETION -> 25;
            case WORKSHOP -> 15;
            case PUBLICATION -> 80;
            case PATENT -> 150;
            case AWARD -> 40;
            case SKILL_BADGE -> 20;
            case LANGUAGE_PROFICIENCY -> 30;
            default -> 10;
        };
    }

    /**
     * Generate title based on credential type
     */
    private String generateTitle(Credential.CredentialType type) {
        return switch (type) {
            case UNIVERSITY_DEGREE -> "Scholar";
            case CERTIFICATION -> "Certified Professional";
            case LICENSE -> "Licensed Practitioner";
            case PUBLICATION -> "Author";
            case PATENT -> "Inventor";
            case AWARD -> "Award Recipient";
            default -> "Credentialed";
        };
    }

    /**
     * Get all credentials for a user
     */
    @Transactional(readOnly = true)
    public List<Credential> getUserCredentials(User user) {
        CharacterProfile profile = characterService.getOrCreateProfile(user);
        return credentialRepository.findByCharacterProfile(profile);
    }

    /**
     * Get verified credentials for a user
     */
    @Transactional(readOnly = true)
    public List<Credential> getVerifiedCredentials(User user) {
        CharacterProfile profile = characterService.getOrCreateProfile(user);
        return credentialRepository.findByCharacterProfileAndVerificationStatus(
                profile, Credential.VerificationStatus.VERIFIED);
    }

    /**
     * Get public credentials (for profile display)
     */
    @Transactional(readOnly = true)
    public List<Credential> getPublicCredentials(User user) {
        CharacterProfile profile = characterService.getOrCreateProfile(user);
        return credentialRepository.findByCharacterProfileAndIsPublicTrue(profile);
    }

    /**
     * Update credential visibility
     */
    @Transactional
    public Credential updateVisibility(User user, Long credentialId, boolean isPublic) {
        Credential credential = credentialRepository.findById(credentialId)
                .orElseThrow(() -> new RuntimeException("Credential not found"));

        CharacterProfile profile = characterService.getOrCreateProfile(user);

        if (!credential.getCharacterProfile().getId().equals(profile.getId())) {
            throw new RuntimeException("Credential does not belong to this user");
        }

        credential.setIsPublic(isPublic);
        return credentialRepository.save(credential);
    }

    /**
     * Delete credential
     */
    @Transactional
    public void deleteCredential(User user, Long credentialId) {
        Credential credential = credentialRepository.findById(credentialId)
                .orElseThrow(() -> new RuntimeException("Credential not found"));

        CharacterProfile profile = characterService.getOrCreateProfile(user);

        if (!credential.getCharacterProfile().getId().equals(profile.getId())) {
            throw new RuntimeException("Credential does not belong to this user");
        }

        // Delete file
        try {
            Path filePath = Paths.get(credential.getDocumentUrl());
            Files.deleteIfExists(filePath);
        } catch (IOException e) {
            log.warn("Failed to delete credential file: {}", e.getMessage());
        }

        credentialRepository.delete(credential);

        log.info("Deleted credential {} for {}",
                credential.getTitle(), profile.getCharacterName());
    }
}
