package com.sanctuary.repository;

import com.sanctuary.model.AcquiredKnowledge;
import com.sanctuary.model.CharacterProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AcquiredKnowledgeRepository extends JpaRepository<AcquiredKnowledge, Long> {
    List<AcquiredKnowledge> findByCharacterProfile(CharacterProfile profile);
    List<AcquiredKnowledge> findByCharacterProfileAndIsCompletedTrue(CharacterProfile profile);
    List<AcquiredKnowledge> findByCharacterProfileAndCategory(CharacterProfile profile, AcquiredKnowledge.KnowledgeCategory category);
    long countByCharacterProfileAndIsCompletedTrue(CharacterProfile profile);
}
