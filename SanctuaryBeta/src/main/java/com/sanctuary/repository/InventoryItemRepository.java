package com.sanctuary.repository;

import com.sanctuary.model.CharacterProfile;
import com.sanctuary.model.InventoryItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InventoryItemRepository extends JpaRepository<InventoryItem, Long> {
    List<InventoryItem> findByCharacterProfile(CharacterProfile profile);
    List<InventoryItem> findByCharacterProfileAndType(CharacterProfile profile, InventoryItem.ItemType type);
    long countByCharacterProfile(CharacterProfile profile);
}
