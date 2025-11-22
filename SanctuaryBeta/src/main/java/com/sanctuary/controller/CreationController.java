package com.sanctuary.controller;

import com.sanctuary.dto.GenerateModelRequest;
import com.sanctuary.dto.GenerateModelResponse;
import com.sanctuary.model.Creation;
import com.sanctuary.model.User;
import com.sanctuary.service.CreationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

/**
 * REST API for AI-generated model creation
 */
@RestController
@RequestMapping("/api/v1/creations")
@RequiredArgsConstructor
@Tag(name = "Creations", description = "AI-generated 3D model management")
public class CreationController {

    private final CreationService creationService;

    @PostMapping("/generate")
    @Operation(summary = "Generate 3D model from text prompt")
    public ResponseEntity<GenerateModelResponse> generateModel(
            @Valid @RequestBody GenerateModelRequest request,
            @AuthenticationPrincipal User user
    ) {
        GenerateModelResponse response = creationService.generateModel(request, user);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/my-creations")
    @Operation(summary = "Get current user's creations")
    public ResponseEntity<Page<Creation>> getMyCreations(
            @AuthenticationPrincipal User user,
            Pageable pageable
    ) {
        Page<Creation> creations = creationService.getUserCreations(user, pageable);
        return ResponseEntity.ok(creations);
    }

    @GetMapping("/public")
    @Operation(summary = "Get public creations from all users")
    public ResponseEntity<Page<Creation>> getPublicCreations(Pageable pageable) {
        Page<Creation> creations = creationService.getPublicCreations(pageable);
        return ResponseEntity.ok(creations);
    }

    @GetMapping("/{generationId}")
    @Operation(summary = "Get creation by generation ID")
    public ResponseEntity<Creation> getCreation(@PathVariable String generationId) {
        Creation creation = creationService.getByGenerationId(generationId);
        return ResponseEntity.ok(creation);
    }
}
