package com.sanctuary.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * Acquired Knowledge - Educational achievements and completed studies
 */
@Entity
@Table(name = "acquired_knowledge")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AcquiredKnowledge {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_profile_id", nullable = false)
    private CharacterProfile characterProfile;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private KnowledgeCategory category;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private KnowledgeSource source;

    @Column(name = "source_reference")
    private String sourceReference; // Book title, biome name, etc.

    @Column(name = "completion_percentage")
    private Integer completionPercentage = 0;

    @Column(nullable = false)
    private Boolean isCompleted = false;

    @Column(name = "experience_gained")
    private Integer experienceGained = 0;

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes; // User's personal notes

    @CreationTimestamp
    @Column(name = "started_at", updatable = false)
    private LocalDateTime startedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    public enum KnowledgeCategory {
        PHILOSOPHY("Philosophical Studies"),
        LITERATURE("Literary Works"),
        SCIENCE("Scientific Knowledge"),
        HISTORY("Historical Understanding"),
        SPIRITUALITY("Spiritual Teachings"),
        NATURE("Natural World"),
        TECHNOLOGY("Technical Skills"),
        ARTS("Artistic Studies"),
        MATHEMATICS("Mathematical Concepts"),
        SOCIOLOGY("Social Sciences");

        private final String displayName;

        KnowledgeCategory(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    public enum KnowledgeSource {
        BIOME_EDUCATION,      // From protected biomes
        ARCHIVE_READING,      // From Infinite Archive
        MEDITATION,           // From spiritual practice
        CREATION,             // From making things
        SOCIAL_LEARNING,      // From other users
        ACHIEVEMENT,          // From accomplishments
        REAL_WORLD_CREDENTIAL // Linked real credentials
    }

    /**
     * Complete this knowledge entry
     */
    public void complete() {
        this.isCompleted = true;
        this.completionPercentage = 100;
        this.completedAt = LocalDateTime.now();
    }
}
