package com.sanctuary.dto;

import com.sanctuary.model.AcquiredKnowledge;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Data Transfer Object for Acquired Knowledge
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AcquiredKnowledgeDTO {
    private Long id;
    private String title;
    private String author;
    private AcquiredKnowledge.KnowledgeCategory category;
    private String sourceUrl;
    private Boolean isCompleted;
    private LocalDateTime acquiredAt;
    private LocalDateTime completedAt;
    private Integer experienceGained;
    private String notes;

    /**
     * Convert AcquiredKnowledge entity to DTO
     */
    public static AcquiredKnowledgeDTO fromEntity(AcquiredKnowledge knowledge) {
        return AcquiredKnowledgeDTO.builder()
                .id(knowledge.getId())
                .title(knowledge.getTitle())
                .author(knowledge.getAuthor())
                .category(knowledge.getCategory())
                .sourceUrl(knowledge.getSourceUrl())
                .isCompleted(knowledge.getIsCompleted())
                .acquiredAt(knowledge.getAcquiredAt())
                .completedAt(knowledge.getCompletedAt())
                .experienceGained(knowledge.getExperienceGained())
                .notes(knowledge.getNotes())
                .build();
    }
}
