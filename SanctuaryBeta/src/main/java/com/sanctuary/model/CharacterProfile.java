package com.sanctuary.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Character Profile - RPG-style character with stats, skills, and progression
 */
@Entity
@Table(name = "character_profiles")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CharacterProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private String characterName;

    @Column(columnDefinition = "TEXT")
    private String biography;

    // Core Stats
    @Column(nullable = false)
    private Integer level = 1;

    @Column(nullable = false)
    private Integer experience = 0;

    @Column(nullable = false)
    private Integer experienceToNextLevel = 100;

    // Spiritual Stats
    @Column(nullable = false)
    private Integer enlightenment = 0;

    @Column(nullable = false)
    private Integer wisdom = 0;

    @Column(nullable = false)
    private Integer creativity = 0;

    @Column(nullable = false)
    private Integer harmony = 0;

    @Column(nullable = false)
    private Integer knowledge = 0;

    // Currency/Resources
    @Column(nullable = false)
    private Integer essencePoints = 0; // Spiritual currency

    @Column(nullable = false)
    private Integer creationTokens = 0; // For AI generation

    // Inventory
    @OneToMany(mappedBy = "characterProfile", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<InventoryItem> inventory = new ArrayList<>();

    // Skills
    @OneToMany(mappedBy = "characterProfile", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Skill> skills = new ArrayList<>();

    // Spells/Abilities
    @OneToMany(mappedBy = "characterProfile", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Spell> spells = new ArrayList<>();

    // Knowledge/Achievements
    @OneToMany(mappedBy = "characterProfile", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<AcquiredKnowledge> knowledgeBase = new ArrayList<>();

    // Real-world Credentials
    @OneToMany(mappedBy = "characterProfile", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Credential> credentials = new ArrayList<>();

    // Spiritual Journey
    @Column(name = "meditation_minutes")
    private Integer meditationMinutes = 0;

    @Column(name = "biomes_visited")
    private Integer biomesVisited = 0;

    @Column(name = "creations_made")
    private Integer creationsMade = 0;

    @Column(name = "texts_read")
    private Integer textsRead = 0;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    /**
     * Add experience and check for level up
     */
    public boolean addExperience(int amount) {
        this.experience += amount;

        if (this.experience >= this.experienceToNextLevel) {
            levelUp();
            return true;
        }
        return false;
    }

    /**
     * Level up character
     */
    private void levelUp() {
        this.level++;
        this.experience -= this.experienceToNextLevel;
        this.experienceToNextLevel = calculateNextLevelRequirement();

        // Stat increases on level up
        this.wisdom += 5;
        this.enlightenment += 3;
        this.creativity += 2;
        this.essencePoints += 10;
        this.creationTokens += 1;
    }

    /**
     * Calculate XP required for next level
     */
    private int calculateNextLevelRequirement() {
        return (int) (100 * Math.pow(1.5, level - 1));
    }
}
