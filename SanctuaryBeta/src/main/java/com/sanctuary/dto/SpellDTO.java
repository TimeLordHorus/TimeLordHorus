package com.sanctuary.dto;

import com.sanctuary.model.Spell;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Data Transfer Object for Spells
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SpellDTO {
    private Long id;
    private String name;
    private String description;
    private Spell.SpellSchool school;
    private Integer level;
    private Integer essenceCost;
    private Integer cooldownSeconds;
    private LocalDateTime lastCastTime;
    private Boolean isUnlocked;
    private Boolean isReady; // Calculated field

    /**
     * Convert Spell entity to DTO
     */
    public static SpellDTO fromEntity(Spell spell) {
        return SpellDTO.builder()
                .id(spell.getId())
                .name(spell.getName())
                .description(spell.getDescription())
                .school(spell.getSchool())
                .level(spell.getLevel())
                .essenceCost(spell.getEssenceCost())
                .cooldownSeconds(spell.getCooldownSeconds())
                .lastCastTime(spell.getLastCastTime())
                .isUnlocked(spell.getIsUnlocked())
                .isReady(spell.isReady())
                .build();
    }
}
