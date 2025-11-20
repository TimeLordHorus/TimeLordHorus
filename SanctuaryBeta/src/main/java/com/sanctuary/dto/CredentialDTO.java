package com.sanctuary.dto;

import com.sanctuary.model.Credential;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Data Transfer Object for Credentials
 * Excludes sensitive information like document URLs and hashes
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CredentialDTO {
    private Long id;
    private String title;
    private Credential.CredentialType type;
    private String issuingOrganization;
    private LocalDate issueDate;
    private LocalDate expiryDate;
    private Credential.VerificationStatus verificationStatus;
    private LocalDateTime submittedAt;
    private LocalDateTime verifiedAt;
    private Integer experienceBonus;
    private String titleGranted;
    private Boolean isPublic;

    /**
     * Convert Credential entity to DTO (excludes sensitive data)
     */
    public static CredentialDTO fromEntity(Credential credential) {
        return CredentialDTO.builder()
                .id(credential.getId())
                .title(credential.getTitle())
                .type(credential.getType())
                .issuingOrganization(credential.getIssuingOrganization())
                .issueDate(credential.getIssueDate())
                .expiryDate(credential.getExpiryDate())
                .verificationStatus(credential.getVerificationStatus())
                .submittedAt(credential.getSubmittedAt())
                .verifiedAt(credential.getVerifiedAt())
                .experienceBonus(credential.getExperienceBonus())
                .titleGranted(credential.getTitleGranted())
                .isPublic(credential.getIsPublic())
                .build();
    }
}
