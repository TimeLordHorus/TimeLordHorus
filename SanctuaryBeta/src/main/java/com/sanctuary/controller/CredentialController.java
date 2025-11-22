package com.sanctuary.controller;

import com.sanctuary.model.Credential;
import com.sanctuary.model.User;
import com.sanctuary.service.CredentialService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * REST API Controller for Credential Management
 */
@RestController
@RequestMapping("/api/v1/credentials")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // TODO: Configure proper CORS in production
public class CredentialController {

    private final CredentialService credentialService;

    /**
     * POST /api/v1/credentials/submit
     * Submit a new credential for verification
     */
    @PostMapping("/submit")
    public ResponseEntity<?> submitCredential(
            @AuthenticationPrincipal User user,
            @RequestParam("title") String title,
            @RequestParam("type") Credential.CredentialType type,
            @RequestParam("issuingOrganization") String issuingOrganization,
            @RequestParam("issueDate") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate issueDate,
            @RequestParam("document") MultipartFile document
    ) {
        try {
            // Validate file
            if (document.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "Document file is required"));
            }

            // Validate file size (10MB limit)
            if (document.getSize() > 10 * 1024 * 1024) {
                return ResponseEntity.badRequest().body(Map.of("error", "File size exceeds 10MB limit"));
            }

            // Validate file type
            String contentType = document.getContentType();
            if (contentType == null ||
                (!contentType.startsWith("image/") &&
                 !contentType.equals("application/pdf"))) {
                return ResponseEntity.badRequest().body(Map.of(
                        "error", "Invalid file type. Only images and PDFs are allowed"
                ));
            }

            Credential credential = credentialService.submitCredential(
                    user, title, type, issuingOrganization, issueDate, document
            );

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Credential submitted for verification",
                    "credentialId", credential.getId(),
                    "status", credential.getVerificationStatus(),
                    "potentialXP", credential.getExperienceBonus(),
                    "potentialTitle", credential.getTitleGranted()
            ));

        } catch (IOException e) {
            return ResponseEntity.internalServerError().body(Map.of(
                    "error", "Failed to save document: " + e.getMessage()
            ));
        } catch (NoSuchAlgorithmException e) {
            return ResponseEntity.internalServerError().body(Map.of(
                    "error", "Hashing algorithm not available: " + e.getMessage()
            ));
        }
    }

    /**
     * GET /api/v1/credentials
     * Get all credentials for the authenticated user
     */
    @GetMapping
    public ResponseEntity<List<Credential>> getUserCredentials(@AuthenticationPrincipal User user) {
        List<Credential> credentials = credentialService.getUserCredentials(user);
        return ResponseEntity.ok(credentials);
    }

    /**
     * GET /api/v1/credentials/verified
     * Get verified credentials for the authenticated user
     */
    @GetMapping("/verified")
    public ResponseEntity<List<Credential>> getVerifiedCredentials(@AuthenticationPrincipal User user) {
        List<Credential> credentials = credentialService.getVerifiedCredentials(user);
        return ResponseEntity.ok(credentials);
    }

    /**
     * GET /api/v1/credentials/public
     * Get public credentials for display
     */
    @GetMapping("/public")
    public ResponseEntity<List<Credential>> getPublicCredentials(@AuthenticationPrincipal User user) {
        List<Credential> credentials = credentialService.getPublicCredentials(user);
        return ResponseEntity.ok(credentials);
    }

    /**
     * PUT /api/v1/credentials/{credentialId}/visibility
     * Update credential visibility
     */
    @PutMapping("/{credentialId}/visibility")
    public ResponseEntity<?> updateVisibility(
            @AuthenticationPrincipal User user,
            @PathVariable Long credentialId,
            @RequestBody Map<String, Boolean> request
    ) {
        try {
            Boolean isPublic = request.get("isPublic");
            if (isPublic == null) {
                return ResponseEntity.badRequest().body(Map.of("error", "isPublic field is required"));
            }

            Credential credential = credentialService.updateVisibility(user, credentialId, isPublic);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "credentialId", credential.getId(),
                    "isPublic", credential.getIsPublic()
            ));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * DELETE /api/v1/credentials/{credentialId}
     * Delete a credential
     */
    @DeleteMapping("/{credentialId}")
    public ResponseEntity<?> deleteCredential(
            @AuthenticationPrincipal User user,
            @PathVariable Long credentialId
    ) {
        try {
            credentialService.deleteCredential(user, credentialId);
            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Credential deleted"
            ));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * POST /api/v1/credentials/{credentialId}/verify
     * Admin endpoint to verify or reject a credential
     */
    @PostMapping("/{credentialId}/verify")
    public ResponseEntity<?> verifyCredential(
            @PathVariable Long credentialId,
            @RequestBody Map<String, Object> request
    ) {
        // TODO: Add admin authentication check
        try {
            Boolean approved = (Boolean) request.get("approved");
            String adminNotes = (String) request.get("adminNotes");

            if (approved == null) {
                return ResponseEntity.badRequest().body(Map.of("error", "approved field is required"));
            }

            Credential credential = credentialService.verifyCredential(
                    credentialId, approved, adminNotes
            );

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "credentialId", credential.getId(),
                    "status", credential.getVerificationStatus(),
                    "xpAwarded", approved ? credential.getExperienceBonus() : 0,
                    "titleGranted", approved ? credential.getTitleGranted() : null
            ));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
}
