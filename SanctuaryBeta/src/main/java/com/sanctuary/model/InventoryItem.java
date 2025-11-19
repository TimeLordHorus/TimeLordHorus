package com.sanctuary.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * Inventory Item - Items, artifacts, and collectibles
 */
@Entity
@Table(name = "inventory_items")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InventoryItem {

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
    private ItemType type;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ItemRarity rarity = ItemRarity.COMMON;

    @Column(nullable = false)
    private Integer quantity = 1;

    @Column(nullable = false)
    private Boolean isEquipped = false;

    @Column(name = "icon_url")
    private String iconUrl;

    @Column(name = "model_url")
    private String modelUrl; // 3D model for VR display

    @Column(columnDefinition = "TEXT")
    private String properties; // JSON for additional properties

    @CreationTimestamp
    @Column(name = "acquired_at", updatable = false)
    private LocalDateTime acquiredAt;

    public enum ItemType {
        CREATION,      // User-generated 3D models
        ARTIFACT,      // Found in biomes
        BOOK,          // Educational texts
        SCROLL,        // Spell/ability scrolls
        MATERIAL,      // Crafting materials
        TOOL,          // Utility items
        GIFT,          // Received from others
        ACHIEVEMENT    // Achievement rewards
    }

    public enum ItemRarity {
        COMMON,
        UNCOMMON,
        RARE,
        EPIC,
        LEGENDARY,
        MYTHIC
    }
}
