package com.sanctuary.controller;

import com.sanctuary.model.Skill;
import com.sanctuary.model.User;
import com.sanctuary.service.CharacterService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST API Controller for Skills and Spells
 */
@RestController
@RequestMapping("/api/v1/skills")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // TODO: Configure proper CORS in production
public class SkillController {

    private final CharacterService characterService;

    /**
     * POST /api/v1/skills/{skillType}/award-xp
     * Award experience to a specific skill
     */
    @PostMapping("/{skillType}/award-xp")
    public ResponseEntity<?> awardSkillExperience(
            @AuthenticationPrincipal User user,
            @PathVariable Skill.SkillType skillType,
            @RequestBody Map<String, Integer> request
    ) {
        try {
            Integer amount = request.get("amount");
            if (amount == null || amount <= 0) {
                return ResponseEntity.badRequest().body(Map.of("error", "Invalid XP amount"));
            }

            boolean leveledUp = characterService.awardSkillExperience(user, skillType, amount);

            return ResponseEntity.ok(Map.of(
                    "success", true,
                    "skillType", skillType,
                    "xpGained", amount,
                    "leveledUp", leveledUp
            ));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * POST /api/v1/skills/spells/{spellId}/cast
     * Cast a spell
     */
    @PostMapping("/spells/{spellId}/cast")
    public ResponseEntity<?> castSpell(
            @AuthenticationPrincipal User user,
            @PathVariable Long spellId
    ) {
        try {
            boolean success = characterService.castSpell(user, spellId);

            if (success) {
                return ResponseEntity.ok(Map.of(
                        "success", true,
                        "message", "Spell cast successfully"
                ));
            } else {
                return ResponseEntity.badRequest().body(Map.of(
                        "error", "Unable to cast spell. Check essence and cooldown."
                ));
            }
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
}
