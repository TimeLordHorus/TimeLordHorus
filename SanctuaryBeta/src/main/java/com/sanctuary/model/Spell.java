package com.sanctuary.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * Spell/Ability - Special abilities and powers
 */
@Entity
@Table(name = "spells")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Spell {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_profile_id", nullable = false)
    private CharacterProfile characterProfile;

    @Column(nullable = false)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private SpellSchool school;

    @Column(nullable = false)
    private Integer level = 1;

    @Column(nullable = false)
    private Integer essenceCost = 10; // Cost to cast

    @Column(nullable = false)
    private Integer cooldownSeconds = 0;

    @Column(name = "last_cast_time")
    private LocalDateTime lastCastTime;

    @Column(name = "icon_url")
    private String iconUrl;

    @Column(name = "effect_data", columnDefinition = "TEXT")
    private String effectData; // JSON for spell effects

    @Column(nullable = false)
    private Boolean isUnlocked = false;

    @CreationTimestamp
    @Column(name = "acquired_at", updatable = false)
    private LocalDateTime acquiredAt;

    public enum SpellSchool {
        CREATION("Manifestation & Building"),
        TRANSMUTATION("Transformation & Change"),
        ILLUMINATION("Light & Revelation"),
        HARMONY("Balance & Healing"),
        TEMPORAL("Time & Space"),
        KNOWLEDGE("Information & Wisdom"),
        NATURE("Environmental Control"),
        ETHEREAL("Spirit & Consciousness");

        private final String description;

        SpellSchool(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }

    /**
     * Check if spell is ready to cast
     */
    public boolean isReady() {
        if (!isUnlocked) {
            return false;
        }

        if (lastCastTime == null) {
            return true;
        }

        LocalDateTime now = LocalDateTime.now();
        LocalDateTime readyTime = lastCastTime.plusSeconds(cooldownSeconds);

        return now.isAfter(readyTime);
    }

    /**
     * Cast the spell
     */
    public void cast() {
        this.lastCastTime = LocalDateTime.now();
    }
}
