package com.sanctuary.dto;

import com.sanctuary.model.InventoryItem;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object for Inventory Items
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InventoryItemDTO {
    private Long id;
    private String name;
    private String description;
    private InventoryItem.ItemType type;
    private InventoryItem.ItemRarity rarity;
    private Integer quantity;
    private String iconUrl;
    private Boolean isEquipped;
    private Boolean isTradeable;

    /**
     * Convert InventoryItem entity to DTO
     */
    public static InventoryItemDTO fromEntity(InventoryItem item) {
        return InventoryItemDTO.builder()
                .id(item.getId())
                .name(item.getName())
                .description(item.getDescription())
                .type(item.getType())
                .rarity(item.getRarity())
                .quantity(item.getQuantity())
                .iconUrl(item.getIconUrl())
                .isEquipped(item.getIsEquipped())
                .isTradeable(item.getIsTradeable())
                .build();
    }
}
