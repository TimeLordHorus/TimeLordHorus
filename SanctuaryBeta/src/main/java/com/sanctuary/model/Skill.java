package com.sanctuary.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * Skill - Character abilities and proficiencies
 */
@Entity
@Table(name = "skills")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Skill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_profile_id", nullable = false)
    private CharacterProfile characterProfile;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private SkillType type;

    @Column(nullable = false)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false)
    private Integer level = 1;

    @Column(nullable = false)
    private Integer maxLevel = 100;

    @Column(nullable = false)
    private Integer experience = 0;

    @Column(nullable = false)
    private Integer experienceToNextLevel = 50;

    @Column(name = "icon_url")
    private String iconUrl;

    @Column(nullable = false)
    private Boolean isActive = true;

    @CreationTimestamp
    @Column(name = "acquired_at", updatable = false)
    private LocalDateTime acquiredAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    public enum SkillType {
        // Creation Skills
        SCULPTURE("3D Modeling & Sculpting"),
        ARCHITECTURE("Environmental Design"),
        TEXTURING("Material Creation"),

        // Spiritual Skills
        MEDITATION("Mindfulness & Focus"),
        ENLIGHTENMENT("Spiritual Wisdom"),
        HARMONY("Balance & Peace"),

        // Knowledge Skills
        PHILOSOPHY("Philosophical Understanding"),
        LITERATURE("Literary Knowledge"),
        SCIENCE("Scientific Understanding"),
        HISTORY("Historical Knowledge"),

        // Social Skills
        TEACHING("Knowledge Sharing"),
        COLLABORATION("Cooperative Creation"),
        LEADERSHIP("Community Guidance"),

        // Technical Skills
        PROGRAMMING("Code & Logic"),
        MATHEMATICS("Mathematical Reasoning"),
        ENGINEERING("System Design");

        private final String displayName;

        SkillType(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    /**
     * Add experience to skill
     */
    public boolean addExperience(int amount) {
        if (level >= maxLevel) {
            return false;
        }

        this.experience += amount;

        if (this.experience >= this.experienceToNextLevel) {
            levelUp();
            return true;
        }
        return false;
    }

    /**
     * Level up skill
     */
    private void levelUp() {
        if (level < maxLevel) {
            this.level++;
            this.experience -= this.experienceToNextLevel;
            this.experienceToNextLevel = (int) (50 * Math.pow(1.2, level - 1));
        }
    }
}
