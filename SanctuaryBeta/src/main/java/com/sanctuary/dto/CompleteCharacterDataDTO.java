package com.sanctuary.dto;

import com.sanctuary.model.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Complete Character Data DTO
 * Aggregates all character-related data for the HUD
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CompleteCharacterDataDTO {
    private CharacterProfileDTO profile;
    private List<InventoryItemDTO> inventory;
    private List<SkillDTO> skills;
    private List<SpellDTO> spells;
    private List<AcquiredKnowledgeDTO> knowledge;
    private List<CredentialDTO> credentials;
    private CharacterStatsDTO stats;

    /**
     * Create complete character data from entities
     */
    public static CompleteCharacterDataDTO fromEntities(
            CharacterProfile profile,
            List<InventoryItem> inventory,
            List<Skill> skills,
            List<Spell> spells,
            List<AcquiredKnowledge> knowledge,
            List<Credential> credentials
    ) {
        return CompleteCharacterDataDTO.builder()
                .profile(CharacterProfileDTO.fromEntity(profile))
                .inventory(inventory.stream()
                        .map(InventoryItemDTO::fromEntity)
                        .collect(Collectors.toList()))
                .skills(skills.stream()
                        .map(SkillDTO::fromEntity)
                        .collect(Collectors.toList()))
                .spells(spells.stream()
                        .map(SpellDTO::fromEntity)
                        .collect(Collectors.toList()))
                .knowledge(knowledge.stream()
                        .map(AcquiredKnowledgeDTO::fromEntity)
                        .collect(Collectors.toList()))
                .credentials(credentials.stream()
                        .map(CredentialDTO::fromEntity)
                        .collect(Collectors.toList()))
                .stats(CharacterStatsDTO.builder()
                        .level(profile.getLevel())
                        .experience(profile.getExperience())
                        .totalCreations(profile.getCreationsMade())
                        .totalMeditation(profile.getMeditationMinutes())
                        .biomesVisited(profile.getBiomesVisited())
                        .textsRead(profile.getTextsRead())
                        .skillCount(skills.size())
                        .spellCount((int) spells.stream().filter(Spell::getIsUnlocked).count())
                        .knowledgeCompleted((int) knowledge.stream()
                                .filter(AcquiredKnowledge::getIsCompleted).count())
                        .verifiedCredentials((int) credentials.stream()
                                .filter(c -> c.getVerificationStatus() == Credential.VerificationStatus.VERIFIED)
                                .count())
                        .build())
                .build();
    }
}

/**
 * Character Statistics Summary
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class CharacterStatsDTO {
    private Integer level;
    private Integer experience;
    private Integer totalCreations;
    private Integer totalMeditation;
    private Integer biomesVisited;
    private Integer textsRead;
    private Integer skillCount;
    private Integer spellCount;
    private Integer knowledgeCompleted;
    private Integer verifiedCredentials;
}
