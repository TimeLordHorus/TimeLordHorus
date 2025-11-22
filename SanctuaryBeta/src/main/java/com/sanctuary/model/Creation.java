package com.sanctuary.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * AI-generated 3D model creation
 */
@Entity
@Table(name = "creations")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Creation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String generationId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String prompt;

    @Column(name = "model_url")
    private String modelUrl;

    @Column(name = "thumbnail_url")
    private String thumbnailUrl;

    @Column(name = "polycount")
    private Integer polycount;

    @Column(name = "quality")
    private String quality;

    @Column(name = "style")
    private String style;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private GenerationStatus status = GenerationStatus.PENDING;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "is_public")
    private Boolean isPublic = true;

    @Column(name = "is_moderated")
    private Boolean isModerated = false;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    public enum GenerationStatus {
        PENDING,
        PROCESSING,
        COMPLETED,
        FAILED
    }
}
