package com.sanctuary.controller;

import com.sanctuary.model.User;
import com.sanctuary.service.CharacterService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST API Controller for Character Management
 */
@RestController
@RequestMapping("/api/v1/character")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // TODO: Configure proper CORS in production
public class CharacterController {

    private final CharacterService characterService;

    /**
     * GET /api/v1/character/profile
     * Get complete character data including profile, inventory, skills, spells, knowledge, credentials
     */
    @GetMapping("/profile")
    public ResponseEntity<Map<String, Object>> getCompleteProfile(@AuthenticationPrincipal User user) {
        Map<String, Object> characterData = characterService.getCompleteCharacterData(user);
        return ResponseEntity.ok(characterData);
    }

    /**
     * GET /api/v1/character/stats
     * Get character statistics summary
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats(@AuthenticationPrincipal User user) {
        Map<String, Object> stats = characterService.getCharacterStats(user);
        return ResponseEntity.ok(stats);
    }

    /**
     * PUT /api/v1/character/name
     * Update character name
     */
    @PutMapping("/name")
    public ResponseEntity<?> updateName(
            @AuthenticationPrincipal User user,
            @RequestBody Map<String, String> request
    ) {
        String newName = request.get("name");
        if (newName == null || newName.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Name cannot be empty"));
        }

        var profile = characterService.updateCharacterName(user, newName);
        return ResponseEntity.ok(Map.of(
                "success", true,
                "characterName", profile.getCharacterName()
        ));
    }

    /**
     * POST /api/v1/character/meditate
     * Track meditation session
     */
    @PostMapping("/meditate")
    public ResponseEntity<?> trackMeditation(
            @AuthenticationPrincipal User user,
            @RequestBody Map<String, Integer> request
    ) {
        Integer minutes = request.get("minutes");
        if (minutes == null || minutes <= 0) {
            return ResponseEntity.badRequest().body(Map.of("error", "Invalid meditation duration"));
        }

        characterService.trackMeditation(user, minutes);
        return ResponseEntity.ok(Map.of(
                "success", true,
                "message", "Meditation session tracked",
                "minutes", minutes,
                "xpGained", minutes * 2
        ));
    }

    /**
     * POST /api/v1/character/experience
     * Award experience to character
     */
    @PostMapping("/experience")
    public ResponseEntity<?> awardExperience(
            @AuthenticationPrincipal User user,
            @RequestBody Map<String, Object> request
    ) {
        Integer amount = (Integer) request.get("amount");
        String reason = (String) request.get("reason");

        if (amount == null || amount <= 0) {
            return ResponseEntity.badRequest().body(Map.of("error", "Invalid XP amount"));
        }

        boolean leveledUp = characterService.awardExperience(user, amount, reason);

        return ResponseEntity.ok(Map.of(
                "success", true,
                "xpGained", amount,
                "leveledUp", leveledUp,
                "reason", reason != null ? reason : "Experience awarded"
        ));
    }

    /**
     * POST /api/v1/character/biome-visit
     * Track biome visit
     */
    @PostMapping("/biome-visit")
    public ResponseEntity<?> trackBiomeVisit(
            @AuthenticationPrincipal User user,
            @RequestBody Map<String, Object> request
    ) {
        String biomeName = (String) request.get("biomeName");
        Integer durationSeconds = (Integer) request.get("durationSeconds");
        Integer nodesVisited = (Integer) request.get("nodesVisited");

        if (biomeName == null || durationSeconds == null || nodesVisited == null) {
            return ResponseEntity.badRequest().body(Map.of("error", "Missing required fields"));
        }

        characterService.trackBiomeVisit(user, biomeName, durationSeconds, nodesVisited);

        int xpGained = 50 + (nodesVisited * 10);
        return ResponseEntity.ok(Map.of(
                "success", true,
                "biomeName", biomeName,
                "xpGained", xpGained,
                "wisdomGained", nodesVisited
        ));
    }

    /**
     * POST /api/v1/character/knowledge/{knowledgeId}/complete
     * Mark knowledge entry as completed
     */
    @PostMapping("/knowledge/{knowledgeId}/complete")
    public ResponseEntity<?> completeKnowledge(
            @AuthenticationPrincipal User user,
            @PathVariable Long knowledgeId
    ) {
        try {
            characterService.completeKnowledge(user, knowledgeId);
            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", "Knowledge completed",
                    "xpGained", 100
            ));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
}
