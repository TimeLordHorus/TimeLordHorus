package com.sanctuary.dto;

import com.sanctuary.model.CharacterProfile;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object for Character Profile
 * Used to send character data to frontend without exposing internal details
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CharacterProfileDTO {
    private Long id;
    private String characterName;
    private Integer level;
    private Integer experience;
    private Integer experienceToNextLevel;
    private Double progressToNextLevel; // Percentage

    // Core stats
    private Integer enlightenment;
    private Integer wisdom;
    private Integer creativity;
    private Integer harmony;
    private Integer knowledge;

    // Currency
    private Integer essencePoints;
    private Integer creationTokens;

    // Tracking
    private Integer meditationMinutes;
    private Integer biomesVisited;
    private Integer creationsMade;
    private Integer textsRead;

    /**
     * Convert CharacterProfile entity to DTO
     */
    public static CharacterProfileDTO fromEntity(CharacterProfile profile) {
        double progress = profile.getExperienceToNextLevel() > 0
                ? (double) profile.getExperience() / profile.getExperienceToNextLevel() * 100
                : 0.0;

        return CharacterProfileDTO.builder()
                .id(profile.getId())
                .characterName(profile.getCharacterName())
                .level(profile.getLevel())
                .experience(profile.getExperience())
                .experienceToNextLevel(profile.getExperienceToNextLevel())
                .progressToNextLevel(Math.round(progress * 10.0) / 10.0)
                .enlightenment(profile.getEnlightenment())
                .wisdom(profile.getWisdom())
                .creativity(profile.getCreativity())
                .harmony(profile.getHarmony())
                .knowledge(profile.getKnowledge())
                .essencePoints(profile.getEssencePoints())
                .creationTokens(profile.getCreationTokens())
                .meditationMinutes(profile.getMeditationMinutes())
                .biomesVisited(profile.getBiomesVisited())
                .creationsMade(profile.getCreationsMade())
                .textsRead(profile.getTextsRead())
                .build();
    }
}
