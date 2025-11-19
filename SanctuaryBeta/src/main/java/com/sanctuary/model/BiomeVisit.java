package com.sanctuary.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * Track user visits to Protected Biomes for analytics and progress
 */
@Entity
@Table(name = "biome_visits")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BiomeVisit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "biome_name", nullable = false)
    private String biomeName;

    @Column(name = "duration_seconds")
    private Integer durationSeconds;

    @Column(name = "nodes_visited")
    private Integer nodesVisited;

    @CreationTimestamp
    @Column(name = "visited_at", updatable = false)
    private LocalDateTime visitedAt;
}
