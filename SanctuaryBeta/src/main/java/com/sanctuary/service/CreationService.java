package com.sanctuary.service;

import com.sanctuary.dto.GenerateModelRequest;
import com.sanctuary.dto.GenerateModelResponse;
import com.sanctuary.model.Creation;
import com.sanctuary.model.User;
import com.sanctuary.repository.CreationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Service for handling AI-generated 3D model creations
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CreationService {

    private final CreationRepository creationRepository;
    private final AIServiceClient aiServiceClient;

    /**
     * Generate a new 3D model from text prompt
     */
    @Transactional
    public GenerateModelResponse generateModel(GenerateModelRequest request, User user) {
        log.info("Generating model for user: {} with prompt: {}", user.getUsername(), request.getPrompt());

        // Create generation record
        String generationId = "gen_" + UUID.randomUUID().toString().replace("-", "").substring(0, 12);

        Creation creation = Creation.builder()
                .generationId(generationId)
                .user(user)
                .prompt(request.getPrompt())
                .quality(request.getQuality())
                .style(request.getStyle())
                .status(Creation.GenerationStatus.PROCESSING)
                .build();

        creation = creationRepository.save(creation);

        // TODO: Async call to AI service
        // For beta, return placeholder
        String modelUrl = "https://example.com/models/" + generationId + ".glb";
        String thumbnailUrl = "https://example.com/thumbnails/" + generationId + ".jpg";

        creation.setModelUrl(modelUrl);
        creation.setThumbnailUrl(thumbnailUrl);
        creation.setPolycount(5000);
        creation.setStatus(Creation.GenerationStatus.COMPLETED);
        creation = creationRepository.save(creation);

        return GenerateModelResponse.builder()
                .generationId(creation.getGenerationId())
                .status(creation.getStatus().name())
                .modelUrl(creation.getModelUrl())
                .thumbnailUrl(creation.getThumbnailUrl())
                .estimatedPolycount(creation.getPolycount())
                .createdAt(creation.getCreatedAt().toString())
                .build();
    }

    /**
     * Get user's creations with pagination
     */
    public Page<Creation> getUserCreations(User user, Pageable pageable) {
        return creationRepository.findByUser(user, pageable);
    }

    /**
     * Get a creation by generation ID
     */
    public Creation getByGenerationId(String generationId) {
        return creationRepository.findByGenerationId(generationId)
                .orElseThrow(() -> new RuntimeException("Creation not found: " + generationId));
    }

    /**
     * Get public creations
     */
    public Page<Creation> getPublicCreations(Pageable pageable) {
        return creationRepository.findByIsPublicTrue(pageable);
    }
}
