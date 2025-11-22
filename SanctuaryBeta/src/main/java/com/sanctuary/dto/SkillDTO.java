package com.sanctuary.dto;

import com.sanctuary.model.Skill;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object for Skills
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SkillDTO {
    private Long id;
    private Skill.SkillType type;
    private String name;
    private String description;
    private Integer level;
    private Integer experience;
    private Integer experienceToNextLevel;
    private Double progressToNextLevel; // Percentage
    private Boolean isActive;

    /**
     * Convert Skill entity to DTO
     */
    public static SkillDTO fromEntity(Skill skill) {
        double progress = skill.getExperienceToNextLevel() > 0
                ? (double) skill.getExperience() / skill.getExperienceToNextLevel() * 100
                : 0.0;

        return SkillDTO.builder()
                .id(skill.getId())
                .type(skill.getType())
                .name(skill.getName())
                .description(skill.getDescription())
                .level(skill.getLevel())
                .experience(skill.getExperience())
                .experienceToNextLevel(skill.getExperienceToNextLevel())
                .progressToNextLevel(Math.round(progress * 10.0) / 10.0)
                .isActive(skill.getIsActive())
                .build();
    }
}
