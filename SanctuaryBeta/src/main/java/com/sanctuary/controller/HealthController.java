package com.sanctuary.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Health check endpoint for monitoring
 */
@RestController
@RequestMapping("/api/v1")
@Tag(name = "Health", description = "Health check endpoints")
public class HealthController {

    @GetMapping("/health")
    @Operation(summary = "Health check")
    public ResponseEntity<Map<String, Object>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "healthy",
                "service", "Sanctuary VR Beta",
                "version", "0.1.0-BETA"
        ));
    }

    @GetMapping("/info")
    @Operation(summary = "Service information")
    public ResponseEntity<Map<String, Object>> info() {
        return ResponseEntity.ok(Map.of(
                "name", "Sanctuary VR Metaverse",
                "description", "Progressive Web Application Beta",
                "platform", "WebXR + Spring Boot",
                "architect", "Curtis G Kyle Junior",
                "features", Map.of(
                        "webxr", true,
                        "ai_generation", true,
                        "multiplayer", true,
                        "biomes", true
                )
        ));
    }
}
